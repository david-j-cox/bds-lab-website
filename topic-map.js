/* Topic-space map of the corpus. Vanilla canvas 2D — no dependencies. */
(() => {
  const PALETTE = ['#6cc5ff','#a98bff','#5fd6a4','#ffb454','#ff7a9c','#7ce0e0',
                   '#c3a3ff','#ffd166','#8fd694','#f4978e','#9aa6bd'];
  // Labels come straight from the data (your hand labels in data/labels.json).
  const LABEL_OVERRIDE = {};

  const canvas = document.getElementById('map');
  const ctx = canvas.getContext('2d');
  const tooltip = document.getElementById('tooltip');
  const detail = document.getElementById('detail');
  const app = document.getElementById('app');
  // The map fills #app (a section), not the whole window.
  const W = () => app.clientWidth, H = () => app.clientHeight;
  const local = e => { const r = canvas.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };

  let DPR = window.devicePixelRatio || 1;
  let items = [], clusters = [], centroids = [];
  let view = { scale: 1, ox: 0, oy: 0 };
  let fit = { scale: 1, ox: 0, oy: 0 };
  let hovered = null, selected = null;
  const hiddenClusters = new Set();

  const labelOf = c => LABEL_OVERRIDE[c.id] || c.label;
  const colorOf = id => PALETTE[id % PALETTE.length];

  // Greedy word-wrap so multi-word labels stack instead of overflowing.
  function wrapLabel(text, maxChars) {
    const words = text.split(' ');
    const lines = [];
    let cur = '';
    for (const w of words) {
      if (cur && (cur + ' ' + w).length > maxChars) { lines.push(cur); cur = w; }
      else cur = cur ? cur + ' ' + w : w;
    }
    if (cur) lines.push(cur);
    return lines;
  }

  function resize() {
    DPR = window.devicePixelRatio || 1;
    canvas.width = W() * DPR;
    canvas.height = H() * DPR;
    canvas.style.width = W() + 'px';
    canvas.style.height = H() + 'px';
  }

  function computeFit() {
    const xs = items.map(d => d.x), ys = items.map(d => d.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const pad = 110, rightInset = W() > 720 ? 270 : 0;
    const w = W() - rightInset - pad * 2, h = H() - pad * 2;
    const scale = Math.min(w / (maxX - minX || 1), h / (maxY - minY || 1));
    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    fit = {
      scale,
      ox: (W() - rightInset) / 2 - cx * scale,
      oy: H() / 2 + cy * scale, // y flipped below
    };
    view = { ...fit };
  }

  // World -> screen. Flip y so positive points up.
  const sx = wx => wx * view.scale + view.ox;
  const sy = wy => -wy * view.scale + view.oy;

  function clusterCentroids() {
    centroids = clusters.map(c => {
      const mem = items.filter(d => d.cluster === c.id);
      const mx = mem.reduce((s, d) => s + d.x, 0) / (mem.length || 1);
      const my = mem.reduce((s, d) => s + d.y, 0) / (mem.length || 1);
      return { id: c.id, x: mx, y: my };
    });
  }

  function draw() {
    ctx.save();
    ctx.scale(DPR, DPR);
    ctx.clearRect(0, 0, innerWidth, innerHeight);

    // Cluster labels (behind nodes), word-wrapped so long names don't run off.
    ctx.textAlign = 'center';
    ctx.font = '600 13px Inter, sans-serif';
    centroids.forEach(c => {
      if (hiddenClusters.has(c.id)) return;
      const cl = clusters.find(k => k.id === c.id);
      ctx.fillStyle = colorOf(c.id) + 'cc';
      const lines = wrapLabel(labelOf(cl), 22);
      lines.forEach((ln, j) => ctx.fillText(ln, sx(c.x), sy(c.y) + j * 15 - (lines.length - 1) * 7.5));
    });

    // Nodes
    items.forEach(d => {
      if (hiddenClusters.has(d.cluster)) return;
      const x = sx(d.x), y = sy(d.y);
      const isBook = d.type === 'book';
      const base = isBook ? 7 : 5.5;
      const r = base * (d === hovered || d === selected ? 1.7 : 1);
      ctx.beginPath();
      ctx.fillStyle = colorOf(d.cluster);
      ctx.globalAlpha = d === hovered || d === selected ? 1 : 0.82;
      if (isBook) {
        ctx.rect(x - r, y - r, r * 2, r * 2);
      } else {
        ctx.arc(x, y, r, 0, Math.PI * 2);
      }
      ctx.fill();
      if (d === hovered || d === selected) {
        ctx.globalAlpha = 1;
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#fff';
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    });
    ctx.restore();
  }

  function nodeAt(px, py) {
    let best = null, bestD = 14;
    for (const d of items) {
      if (hiddenClusters.has(d.cluster)) continue;
      const dx = px - sx(d.x), dy = py - sy(d.y);
      const dist = Math.hypot(dx, dy);
      if (dist < bestD) { bestD = dist; best = d; }
    }
    return best;
  }

  // ---- Interaction ----
  let dragging = false, moved = false, last = null;

  canvas.addEventListener('mousedown', e => {
    dragging = true; moved = false; last = { x: e.clientX, y: e.clientY };
    canvas.classList.add('grabbing');
  });
  window.addEventListener('mouseup', () => { dragging = false; canvas.classList.remove('grabbing'); });
  window.addEventListener('mousemove', e => {
    if (dragging) {
      const dx = e.clientX - last.x, dy = e.clientY - last.y;
      if (Math.abs(dx) + Math.abs(dy) > 2) moved = true;
      view.ox += dx; view.oy += dy; last = { x: e.clientX, y: e.clientY };
      draw();
      return;
    }
    const [px, py] = local(e);
    const hit = nodeAt(px, py);
    if (hit !== hovered) { hovered = hit; draw(); }
    if (hit) showTooltip(hit, px, py);
    else tooltip.hidden = true;
  });

  canvas.addEventListener('click', e => {
    if (moved) return;
    const [px, py] = local(e);
    const hit = nodeAt(px, py);
    if (hit) openDetail(hit);
  });

  canvas.addEventListener('wheel', e => {
    e.preventDefault();
    const factor = Math.exp(-e.deltaY * 0.0015);
    const [mx, my] = local(e);
    // Zoom about cursor: keep world point under cursor fixed.
    const wx = (mx - view.ox) / view.scale, wy = -(my - view.oy) / view.scale;
    view.scale = Math.max(fit.scale * 0.5, Math.min(fit.scale * 12, view.scale * factor));
    view.ox = mx - wx * view.scale;
    view.oy = my + wy * view.scale;
    draw();
  }, { passive: false });

  function showTooltip(d, px, py) {
    tooltip.innerHTML = `<div class="tt-title">${esc(d.title)}</div>
      <div class="tt-meta">${d.authors ? esc(d.authors) + ' &middot; ' : ''}${d.year || 'Book'}</div>`;
    tooltip.hidden = false;
    const r = tooltip.getBoundingClientRect();
    let x = px + 14, y = py + 14;
    if (x + r.width > W() - 10) x = px - r.width - 14;
    if (y + r.height > H() - 10) y = py - r.height - 14;
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }

  const byId = id => items.find(d => d.id === id);

  function openDetail(d) {
    selected = d; draw();
    const cl = clusters.find(k => k.id === d.cluster);
    const color = colorOf(d.cluster);
    const tag = document.getElementById('detail-tag');
    tag.textContent = labelOf(cl);
    tag.style.background = color + '22';
    tag.style.color = color;
    document.getElementById('detail-title').textContent = d.title;
    document.getElementById('detail-meta').innerHTML =
      `${d.authors ? '<span>' + esc(d.authors) + '</span> &middot; ' : ''}` +
      `${d.year ? d.year : 'Book'} &middot; ${d.type}`;
    const abs = document.getElementById('detail-abstract');
    abs.textContent = d.abstract || '';
    abs.style.display = d.abstract ? '' : 'none';

    // Related work in the same neighbourhood
    const relBox = document.getElementById('detail-related');
    const rel = (d.related || []).map(byId).filter(Boolean);
    if (rel.length) {
      relBox.innerHTML = '<div class="rel-head">Related work</div>' +
        rel.map(r => {
          const c = colorOf(r.cluster);
          return `<button class="rel-item" data-id="${r.id}">
            <span class="rel-dot" style="background:${c}"></span>
            <span class="rel-txt">${esc(r.title)}<span class="rel-yr">${r.year || 'Book'}</span></span>
          </button>`;
        }).join('');
      relBox.querySelectorAll('.rel-item').forEach(btn =>
        btn.addEventListener('click', () => navigateTo(byId(btn.dataset.id))));
    } else {
      relBox.innerHTML = '';
    }

    // Links: DOI (if known) + Scholar fallback
    const links = [];
    if (d.doi) links.push(`<a href="https://doi.org/${encodeURIComponent(d.doi)}" target="_blank" rel="noopener">View paper (DOI)</a>`);
    links.push(`<a href="https://scholar.google.com/scholar?q=${encodeURIComponent(d.title)}" target="_blank" rel="noopener">Find on Scholar</a>`);
    document.getElementById('detail-links').innerHTML = links.join('');
    detail.hidden = false;
    detail.scrollTop = 0;
    history.replaceState(null, '', '#paper=' + d.id);
  }

  // Fly the map to centre a node, then open its detail (deep-exploration loop).
  function navigateTo(d) {
    if (!d) return;
    hiddenClusters.delete(d.cluster);
    document.querySelectorAll('#legend li').forEach((li, i) => {
      if (clusters.filter(c => c.count > 0)[i]?.id === d.cluster) li.classList.remove('dim');
    });
    const targetScale = Math.max(view.scale, fit.scale * 2.4);
    const rightInset = W() > 720 ? Math.min(440, W() * 0.92) : 0;
    const tx = (W() - rightInset) / 2, ty = H() / 2;
    const start = { ...view }, t0 = performance.now(), dur = 480;
    const startOx = view.ox, startOy = view.oy;
    const endOx = tx - d.x * targetScale, endOy = ty + d.y * targetScale;
    function step(now) {
      const p = Math.min(1, (now - t0) / dur);
      const e = p < .5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2; // easeInOutQuad
      view.scale = start.scale + (targetScale - start.scale) * e;
      view.ox = startOx + (endOx - startOx) * e;
      view.oy = startOy + (endOy - startOy) * e;
      draw();
      if (p < 1) requestAnimationFrame(step);
      else openDetail(d);
    }
    requestAnimationFrame(step);
  }

  document.getElementById('detail-close').addEventListener('click', () => {
    detail.hidden = true; selected = null; draw();
    history.replaceState(null, '', location.pathname);
  });

  // ---- Legend ----
  function buildLegend() {
    const ul = document.getElementById('legend-list');
    ul.innerHTML = '';
    clusters.filter(c => c.count > 0).forEach(c => {
      const li = document.createElement('li');
      li.innerHTML = `<span class="swatch" style="background:${colorOf(c.id)}"></span>
        <span class="legend-text">${esc(labelOf(c))}<span class="n">${c.count}</span></span>`;
      li.addEventListener('click', () => {
        if (hiddenClusters.has(c.id)) hiddenClusters.delete(c.id);
        else hiddenClusters.add(c.id);
        li.classList.toggle('dim');
        draw();
      });
      ul.appendChild(li);
    });
  }

  document.getElementById('reset-view').addEventListener('click', () => {
    hiddenClusters.clear();
    document.querySelectorAll('#legend li').forEach(li => li.classList.remove('dim'));
    computeFit(); draw();
  });

  window.addEventListener('resize', () => { resize(); computeFit(); draw(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { detail.hidden = true; selected = null; draw(); }
  });

  const esc = s => String(s).replace(/[&<>"]/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // ---- Boot ----
  function boot(data) {
    items = data.items;
    clusters = data.meta.clusters;
    resize();
    clusterCentroids();
    computeFit();
    buildLegend();
    draw();
    // Deep link: #paper=<id> opens and flies to that paper.
    const m = location.hash.match(/paper=([\w-]+)/);
    if (m) { const d = byId(m[1]); if (d) navigateTo(d); }
  }

  // Prefer the inline global (works over file://); fall back to fetch.
  if (window.CORPUS) {
    boot(window.CORPUS);
  } else {
    fetch('data/corpus.json').then(r => r.json()).then(boot).catch(err => {
      document.getElementById('hint').textContent = 'Could not load data/corpus.json';
      console.error(err);
    });
  }
})();
