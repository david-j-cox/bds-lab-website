#!/usr/bin/env python3
"""Enrich data/corpus.json with topic-space coordinates and clusters.

Pure-numpy pipeline (no sklearn / no API keys):
  text -> TF-IDF -> truncated SVD (LSA) -> classical MDS to 2D
                                        -> k-means clusters -> top-term labels

Deterministic. Re-run after build_corpus.py. If a neural embedding source is
added later, only the `vectorize` function needs to change.
"""
import json
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "corpus.json"
LABELS_FILE = ROOT / "data" / "labels.json"
K_CLUSTERS = 11
SVD_DIMS = 40
SEED = 7

STOPWORDS = set("""
a an the of and or to in on for with without by from as at is are was were be been being
this that these those it its their our your his her they we you i he she them us
into over under between within across about more most less least than then thus
can may might will would should could also however therefore using used use uses
study studies analysis analyses effect effects results result data approach approaches
behavior behavioral behaviour via toward towards based across new non per via et al
""".split())

# Words too generic to make useful cluster labels even if statistically salient.
LABEL_STOP = STOPWORDS | set("""
human humans participants participant model models modeling quantitative review
intro introduction special section issue chapter guide proof concept demonstration
""".split())


def tokenize(text):
    toks = re.findall(r"[a-zA-Z][a-zA-Z\-]+", text.lower())
    return [t for t in toks if len(t) >= 3 and t not in STOPWORDS]


def doc_text(item):
    # Weight the title heavily, include authors lightly, then the abstract.
    return " ".join([
        (item["title"] + " ") * 3,
        item.get("authors", ""),
        item.get("abstract", ""),
    ])


def build_tfidf(docs):
    tokenized = [tokenize(d) for d in docs]
    n = len(docs)
    df = {}
    for toks in tokenized:
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    vocab = sorted(t for t, c in df.items() if 2 <= c <= 0.6 * n)
    vindex = {t: i for i, t in enumerate(vocab)}
    X = np.zeros((n, len(vocab)))
    for i, toks in enumerate(tokenized):
        counts = {}
        for t in toks:
            if t in vindex:
                counts[t] = counts.get(t, 0) + 1
        for t, c in counts.items():
            idf = math.log((1 + n) / (1 + df[t])) + 1
            X[i, vindex[t]] = (1 + math.log(c)) * idf
    # L2 normalise rows
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1
    X = X / norms
    return X, vocab


def truncated_svd(X, dims):
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    d = min(dims, len(S))
    return U[:, :d] * S[:d], Vt[:d]


def classical_mds(coords, out_dim=2):
    # Cosine distance -> classical MDS via double-centering eigendecomposition.
    norm = coords / (np.linalg.norm(coords, axis=1, keepdims=True) + 1e-9)
    sim = norm @ norm.T
    D2 = np.clip(1 - sim, 0, None) ** 2
    n = D2.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ D2 @ J
    w, V = np.linalg.eigh(B)
    idx = np.argsort(w)[::-1][:out_dim]
    L = np.sqrt(np.clip(w[idx], 0, None))
    return V[:, idx] * L


def _separate(points, radii, iters=300, seed=SEED):
    """Push circles apart until none overlap (relaxation), keeping them compact."""
    rng = np.random.default_rng(seed)
    pos = points.astype(float) + rng.normal(0, 1e-3, points.shape)
    for _ in range(iters):
        moved = False
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                d = pos[j] - pos[i]
                dist = np.linalg.norm(d) + 1e-9
                need = radii[i] + radii[j]
                if dist < need:
                    push = (need - dist) / 2 * (d / dist)
                    pos[i] -= push
                    pos[j] += push
                    moved = True
        # Gentle pull to origin so the map stays centred and compact
        pos -= pos.mean(0) * 0.05
        if not moved:
            break
    return pos


def island_layout(unit, labels, seed=SEED):
    """Two-level 'topic islands' layout.

    1. Place each cluster centroid by cosine-MDS, then separate the islands so
       they don't overlap (territory size ~ sqrt(member count)).
    2. Pack each cluster's members tightly around its centroid via local MDS.
    Produces clean, separated, legible topic regions.
    """
    rng = np.random.default_rng(seed)
    ids = sorted(np.unique(labels))
    cvecs = np.array([unit[labels == c].mean(0) for c in ids])
    cvecs /= np.linalg.norm(cvecs, axis=1, keepdims=True) + 1e-9
    centers = classical_mds(cvecs, 2)
    centers = (centers - centers.mean(0)) / (centers.std(0) + 1e-9)
    # Compress outlier groups toward the middle so nothing strands at the margin,
    # while keeping the similarity ordering.
    rad = np.linalg.norm(centers, axis=1, keepdims=True)
    centers = centers / (rad + 1e-9) * np.tanh(rad)
    counts = np.array([(labels == c).sum() for c in ids])
    radii = 0.4 + 0.26 * np.sqrt(counts)
    centers = _separate(centers * 2.0, radii + 0.3)

    pos = np.zeros((len(labels), 2))
    for ci, c in enumerate(ids):
        idx = np.where(labels == c)[0]
        m = unit[idx]
        if len(idx) >= 3:
            local = classical_mds(m, 2)
            span = np.abs(local).max(0)
            span[span == 0] = 1
            local = local / span * radii[ci] * 0.8
        elif len(idx) == 2:
            local = np.array([[-radii[ci] * 0.4, 0], [radii[ci] * 0.4, 0]])
        else:
            local = np.zeros((1, 2))
        local += rng.normal(0, radii[ci] * 0.05, local.shape)
        pos[idx] = centers[ci] + local
    return pos


def agglomerative(unit, k):
    """Average-linkage agglomerative clustering on cosine distance.

    More robust than k-means here: a few thematic outliers don't each steal a
    centroid and leave everyone else in one blob.
    """
    n = len(unit)
    sim = unit @ unit.T
    D = np.clip(1 - sim, 0, 2)
    np.fill_diagonal(D, np.inf)
    members = {i: [i] for i in range(n)}
    active = set(range(n))
    while len(active) > k:
        # Find the closest pair of active clusters.
        best = None
        for i in active:
            for j in active:
                if j <= i:
                    continue
                if best is None or D[i, j] < best[0]:
                    best = (D[i, j], i, j)
        _, i, j = best
        # Merge j into i (average linkage via Lance-Williams).
        ni, nj = len(members[i]), len(members[j])
        for m in active:
            if m == i or m == j:
                continue
            D[i, m] = D[m, i] = (ni * D[i, m] + nj * D[j, m]) / (ni + nj)
        members[i].extend(members[j])
        active.discard(j)
        D[j, :] = D[:, j] = np.inf
    labels = np.zeros(n, dtype=int)
    for new_id, c in enumerate(sorted(active, key=lambda c: -len(members[c]))):
        for m in members[c]:
            labels[m] = new_id
    return labels


def kmeans(X, k, seed=SEED, iters=100):
    rng = np.random.default_rng(seed)
    # k-means++ init
    centers = [X[rng.integers(len(X))]]
    for _ in range(1, k):
        d = np.min([np.sum((X - c) ** 2, axis=1) for c in centers], axis=0)
        probs = d / d.sum()
        centers.append(X[rng.choice(len(X), p=probs)])
    centers = np.array(centers)
    labels = np.zeros(len(X), dtype=int)
    for _ in range(iters):
        dists = np.linalg.norm(X[:, None] - centers[None], axis=2)
        new = dists.argmin(axis=1)
        if np.array_equal(new, labels):
            break
        labels = new
        for j in range(k):
            members = X[labels == j]
            if len(members):
                centers[j] = members.mean(axis=0)
    return labels


def cluster_labels(X_tfidf, vocab, labels, k, top=3):
    out = {}
    for j in range(k):
        members = X_tfidf[labels == j]
        if not len(members):
            out[j] = f"topic {j}"
            continue
        score = members.sum(axis=0)
        order = np.argsort(score)[::-1]
        terms = []
        for idx in order:
            term = vocab[idx]
            if term in LABEL_STOP:
                continue
            terms.append(term)
            if len(terms) == top:
                break
        out[j] = ", ".join(terms)
    return out


def load_manual_labels(corpus):
    """Use hand labels from data/labels.json when present (overrides clustering)."""
    if not LABELS_FILE.exists():
        return None, None
    assign = json.loads(LABELS_FILE.read_text()).get("assign", {})
    # Items may also carry their own label (e.g. preprints from preprints.json).
    label_of = lambda it: assign.get(it["id"]) or it.get("label")
    from collections import Counter
    counts = Counter(label_of(it) for it in corpus if label_of(it))
    # Largest group is id 0 (matches the legend ordering).
    ordered = [lab for lab, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    index = {lab: i for i, lab in enumerate(ordered)}
    labels = np.array([index.get(label_of(it), -1) for it in corpus])
    if (labels == -1).any():
        ordered.append("Unlabeled")
        labels[labels == -1] = len(ordered) - 1
    return labels, {i: lab for i, lab in enumerate(ordered)}


def main():
    raw = json.loads(CORPUS.read_text())
    corpus = raw["items"] if isinstance(raw, dict) else raw
    docs = [doc_text(it) for it in corpus]
    X, vocab = build_tfidf(docs)
    reduced, _ = truncated_svd(X, SVD_DIMS)
    # Cluster by cosine direction, not text length / magnitude.
    unit = reduced / (np.linalg.norm(reduced, axis=1, keepdims=True) + 1e-9)
    labels, names = load_manual_labels(corpus)
    if labels is not None:
        print(f"using manual labels from {LABELS_FILE.name}")
    else:
        labels = agglomerative(unit, K_CLUSTERS)
        names = cluster_labels(X, vocab, labels, K_CLUSTERS)
    k = len(names)
    # Two-level "topic islands" layout: separated cluster territories.
    xy = island_layout(unit, labels)
    xy = (xy - xy.mean(0)) / (xy.std(0) + 1e-9)
    # Rotate so the principal (highest-variance) axis is horizontal -> fills the
    # wide map area instead of coming out as a tall narrow strip.
    _, V = np.linalg.eigh(np.cov(xy.T))
    xy = xy @ V[:, ::-1]
    xy = (xy - xy.mean(0)) / (xy.std(0) + 1e-9)

    # Nearest neighbours by cosine similarity for the "related work" drill-down.
    sim = unit @ unit.T
    np.fill_diagonal(sim, -1)
    for i, it in enumerate(corpus):
        it["x"] = round(float(xy[i, 0]), 4)
        it["y"] = round(float(xy[i, 1]), 4)
        it["cluster"] = int(labels[i])
        order = np.argsort(sim[i])[::-1][:5]
        it["related"] = [corpus[j]["id"] for j in order if sim[i, j] > 0.05]

    meta = {
        "clusters": [
            {"id": j, "label": names[j], "count": int((labels == j).sum())}
            for j in range(k)
        ]
    }
    out = {"meta": meta, "items": corpus}
    CORPUS.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    # Also emit a JS global so the page works when opened via file:// (no fetch).
    (ROOT / "data" / "corpus.js").write_text(
        "window.CORPUS = " + json.dumps(out, ensure_ascii=False) + ";\n"
    )
    print(f"vocab={len(vocab)} items={len(corpus)} clusters={k}")
    for c in meta["clusters"]:
        print(f"  [{c['id']}] n={c['count']:2d}  {c['label']}")


if __name__ == "__main__":
    main()
