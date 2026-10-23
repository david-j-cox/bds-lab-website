/* Publications page. Renders window.PUBS (data/publications.js, built by
   scripts/build_publications.py) as a filterable index grouped by year.
   Filters: text search, topic (topic-map clusters), type, and a year range
   brushed on the histogram. */
(function () {
  const D = window.PUBS;
  if (!D) return;
  // same palette and cluster ids as the topic map (topic-map.js)
  const PALETTE = ['#6cc5ff','#a98bff','#5fd6a4','#ffb454','#ff7a9c','#7ce0e0',
                   '#c3a3ff','#ffd166','#8fd694','#f4978e','#9aa6bd'];
  const colorOf = id => id == null ? '#6b7689' : PALETTE[id % PALETTE.length];
  const TYPES = [
    ['article', 'Articles'], ['chapter', 'Chapters'], ['book', 'Books'],
    ['report', 'Reports'], ['progress', 'In progress'],
  ];
  const STATUS_GROUPS = [
    ['inpress', 'Forthcoming', 'In press'],
    ['inreview', 'In review', 'Under review'],
    ['preprint', 'Preprints', 'Working papers'],
  ];
  const typeOf = p => p.status !== 'published' ? 'progress' : p.kind;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const items = D.items.map(p => ({
    ...p,
    _hay: [p.title, p.authors, p.venue, p.topic].join(' ').toLowerCase(),
  }));
  const years = items.filter(p => p.year).map(p => p.year);
  const minY = Math.min(...years), maxY = Math.max(...years);

  const state = { q: '', topics: new Set(), types: new Set(), range: null };

  const $ = id => document.getElementById(id);
  const list = $('pubs-list');

  // ---- filtering
  function passes(p, ignore) {
    if (state.q && !state.q.split(/\s+/).every(w => p._hay.includes(w))) return false;
    if (ignore !== 'topic' && state.topics.size && !state.topics.has(p.cluster)) return false;
    if (ignore !== 'type' && state.types.size && !state.types.has(typeOf(p))) return false;
    if (ignore !== 'year' && state.range) {
      const [a, b] = state.range;
      if (p.year == null) return b === maxY;      // work in progress counts as current
      if (p.year < a || p.year > b) return false;
    }
    return true;
  }

  // ---- entry markup
  function authorsHTML(a) {
    return esc(a).replace(/Cox, D\.\s?J\.?/g, m => `<b>${m}</b>`);
  }
  function linkLabel(url, status) {
    if (status !== 'published') return 'Preprint';
    if (/doi\.org/i.test(url)) return 'DOI';
    if (/\.pdf$/i.test(url)) return 'PDF';
    return 'Read';
  }
  function metaHTML(p) {
    const bits = [];
    if (p.cluster != null) bits.push(`<span class="e-topic"><span class="dot"></span>${esc(p.topic)}</span>`);
    const kind = { article: 'Article', chapter: 'Chapter', book: 'Book', report: 'Report' }[p.kind];
    bits.push(`<span class="e-kind">${kind}</span>`);
    if (p.link) bits.push(`<a href="${esc(p.link)}" target="_blank" rel="noopener">${linkLabel(p.link, p.status)}</a>`);
    if (p.map) bits.push(`<a href="index.html#paper=${encodeURIComponent(p.map)}">On the map</a>`);
    return `<div class="e-meta">${bits.join('')}</div>`;
  }
  function titleHTML(p) {
    const t = esc(p.title);
    return `<h3 class="e-title">${p.link ? `<a href="${esc(p.link)}" target="_blank" rel="noopener">${t}</a>` : t}</h3>`;
  }
  function entryBody(p) {
    return titleHTML(p) +
      `<p class="e-authors">${authorsHTML(p.authors)}</p>` +
      (p.venue ? `<p class="e-venue">${esc(p.venue)}</p>` : '') +
      metaHTML(p);
  }

  // ---- index
  function groups(shown) {
    const out = [];
    for (const [status, label, sub] of STATUS_GROUPS) {
      const g = shown.filter(p => p.status === status);
      if (g.length) out.push({ label, sub, words: true, items: g });
    }
    const dated = shown.filter(p => p.status === 'published');
    const ys = [...new Set(dated.map(p => p.year))].sort((a, b) => b - a);
    for (const y of ys) out.push({ label: y, items: dated.filter(p => p.year === y) });
    return out;
  }
  function renderIndex(shown) {
    list.innerHTML = groups(shown).map(g => `
      <div class="ix-group">
        <div class="ix-label${g.words ? ' words' : ''}">${esc(g.label)}<small>${g.items.length} ${g.items.length === 1 ? 'work' : 'works'}</small></div>
        <div class="ix-entries">${g.items.map(p =>
          `<article class="ix-entry" style="--c:${colorOf(p.cluster)}">${entryBody(p)}</article>`).join('')}</div>
      </div>`).join('');
  }

  // ---- chips
  function chip(label, pressed, color, n, onClick) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'chip';
    b.setAttribute('aria-pressed', pressed);
    if (color) b.style.setProperty('--c', color);
    b.innerHTML = (color ? '<span class="dot"></span>' : '') + esc(label) + ` <span class="n">${n}</span>`;
    b.addEventListener('click', onClick);
    return b;
  }
  function toggle(set, v) { set.has(v) ? set.delete(v) : set.add(v); render(); }
  function renderChips() {
    const topics = $('pubs-topics'), types = $('pubs-types');
    topics.replaceChildren(...D.clusters
      .map(c => [c, items.filter(p => p.cluster === c.id && passes(p, 'topic')).length])
      .filter(([c, n]) => n || state.topics.has(c.id))
      .map(([c, n]) => chip(c.label, state.topics.has(c.id), colorOf(c.id), n, () => toggle(state.topics, c.id))));
    types.replaceChildren(...TYPES
      .map(([k, label]) => [k, label, items.filter(p => typeOf(p) === k && passes(p, 'type')).length])
      .filter(([k, , n]) => n || state.types.has(k))
      .map(([k, label, n]) => chip(label, state.types.has(k), null, n, () => toggle(state.types, k))));
  }

  // ---- year histogram with a draggable range
  const svg = $('pubs-hist');
  const NS = 'http://www.w3.org/2000/svg';
  let geom = null;
  function renderHist() {
    const W = svg.clientWidth || 800, H = svg.clientHeight || 64, padB = 14;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const n = maxY - minY + 1, bw = W / n, gap = Math.min(4, bw * 0.25);
    const counts = {};
    items.forEach(p => {
      if (!p.year || !passes(p, 'year')) return;
      (counts[p.year] = counts[p.year] || []).push(p);
    });
    const peak = Math.max(1, ...Object.values(counts).map(a => a.length));
    const unit = (H - padB - 4) / peak;
    const parts = [];
    for (let y = minY; y <= maxY; y++) {
      const x = (y - minY) * bw + gap / 2;
      const inRange = !state.range || (y >= state.range[0] && y <= state.range[1]);
      let top = H - padB;
      const byCluster = {};
      (counts[y] || []).forEach(p => { byCluster[p.cluster] = (byCluster[p.cluster] || 0) + 1; });
      Object.keys(byCluster).sort().forEach(k => {
        const h = byCluster[k] * unit;
        top -= h;
        const cid = k === 'null' ? null : +k;
        parts.push(`<rect class="bar${inRange ? '' : ' out'}" x="${x}" y="${top}" width="${bw - gap}" height="${h}" fill="${colorOf(cid)}"/>`);
      });
      if ((y - minY) % 2 === 0 || y === maxY)
        parts.push(`<text class="tick" x="${x + (bw - gap) / 2}" y="${H - 2}" text-anchor="middle">${bw < 34 ? "'" + String(y).slice(2) : y}</text>`);
    }
    if (state.range) {
      const x0 = (state.range[0] - minY) * bw, x1 = (state.range[1] - minY + 1) * bw;
      parts.push(`<rect class="brush" x="${x0}" y="0.5" width="${x1 - x0}" height="${H - padB}" rx="3"/>`);
    }
    svg.innerHTML = parts.join('');
    geom = { W, bw };
  }
  function yearAt(evt) {
    const r = svg.getBoundingClientRect();
    const x = (evt.clientX - r.left) * (geom.W / r.width);
    return Math.max(minY, Math.min(maxY, minY + Math.floor(x / geom.bw)));
  }
  let drag = null;
  svg.addEventListener('pointerdown', e => {
    svg.setPointerCapture(e.pointerId);
    const y = yearAt(e);
    drag = { start: y, moved: false, prev: state.range };
    state.range = [y, y];
    render();
  });
  svg.addEventListener('pointermove', e => {
    if (!drag) return;
    const y = yearAt(e);
    if (y !== drag.start) drag.moved = true;
    state.range = [Math.min(drag.start, y), Math.max(drag.start, y)];
    render();
  });
  svg.addEventListener('pointerup', () => {
    // a plain click on an already-selected single year clears it
    if (drag && !drag.moved && drag.prev && drag.prev[0] === drag.start && drag.prev[1] === drag.start)
      state.range = null;
    drag = null;
    render();
  });

  // ---- wiring
  $('pubs-q').addEventListener('input', e => { state.q = e.target.value.trim().toLowerCase(); render(); });
  $('pubs-reset').addEventListener('click', () => {
    state.q = ''; $('pubs-q').value = '';
    state.topics.clear(); state.types.clear(); state.range = null;
    render();
  });
  window.addEventListener('resize', () => renderHist());

  const total = items.length;
  $('pubs-lede').textContent =
    `${total} articles, chapters, books, reports, and works in progress, ${minY} to the present. ` +
    'Filter by topic or type, drag across the timeline to choose years, or search.';

  // names the active filters, e.g. "Showing 74 of 107: Articles, 2018 to 2022"
  function activeFilters() {
    const parts = [];
    if (state.q) parts.push(`"${state.q}"`);
    if (state.topics.size) parts.push(D.clusters.filter(c => state.topics.has(c.id)).map(c => c.label).join(' or '));
    if (state.types.size) parts.push(TYPES.filter(([k]) => state.types.has(k)).map(([, l]) => l).join(' or '));
    if (state.range) parts.push(state.range[0] === state.range[1] ? `${state.range[0]}` : `${state.range[0]} to ${state.range[1]}`);
    return parts;
  }

  function render() {
    const shown = items.filter(p => passes(p));
    renderChips();
    renderHist();
    const active = activeFilters();
    $('pubs-reset').hidden = !active.length;
    $('pubs-range').textContent = state.range
      ? (state.range[0] === state.range[1] ? `${state.range[0]}` : `${state.range[0]} to ${state.range[1]}`)
      : `All years, ${minY} to ${maxY}`;
    $('pubs-count').innerHTML = active.length
      ? `Showing <b>${shown.length}</b> of ${total}: ${esc(active.join(', '))}`
      : `All ${total} works`;
    if (!shown.length) {
      list.innerHTML = '<p class="pubs-empty">Nothing matches those filters.</p>';
      return;
    }
    renderIndex(shown);
  }
  render();
})();
