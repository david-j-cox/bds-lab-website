/* Renders the translation map (bipartite bridges) into #translation-map.
   Expects window.TRANSLATION (data/translation.js). Adds its own tooltip + panel. */
(function () {
  const D = window.TRANSLATION;
  const mount = document.getElementById('translation-map');
  if (!D || !mount) return;
  const F = D.fundamentals, DM = D.domains, E = D.edges;
  const paperById = Object.fromEntries(D.papers.map(p => [p.id, p]));
  const COLOR = { beh_econ: '#6cc5ff', matching: '#a98bff', reinforcement: '#5fd6a4', verbal: '#ffb454',
    ethics_fn: '#ff7a9c', stim_control: '#7ce0e0', design: '#c3a3ff', modeling: '#ffd166' };
  const flbl = Object.fromEntries(F.map(f => [f.id, f.label])), dlbl = Object.fromEntries(DM.map(d => [d.id, d.label]));

  const fOut = {}, dIn = {};
  F.forEach(f => fOut[f.id] = 0); DM.forEach(d => dIn[d.id] = 0);
  E.forEach(e => { fOut[e.fund] += e.papers.length; dIn[e.domain] += e.papers.length; });
  const domOrder = DM.slice().sort((a, b) => dIn[b.id] - dIn[a.id]);

  const H = 640, tpad = 46, bot = H - 30, LX = 360, RX = 620;
  const fy = {}, dy = {};
  F.forEach((f, i) => fy[f.id] = tpad + (bot - tpad) * i / (F.length - 1));
  domOrder.forEach((d, i) => dy[d.id] = tpad + (bot - tpad) * i / (domOrder.length - 1));
  const rOf = id => 5 + Math.sqrt(fOut[id]) * 3.0;
  const wOf = n => 1.5 + n * 1.4;

  const NS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', '0 0 980 640'); svg.id = 'tmap-svg';
  svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', 'Translation map');
  mount.appendChild(svg);
  const el = (t, a) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); return e; };
  const esc = s => String(s || '').replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

  const tip = document.createElement('div'); tip.id = 'tmap-tip'; document.body.appendChild(tip);
  const panel = document.createElement('aside'); panel.id = 'tmap-panel';
  panel.innerHTML = '<button class="x" aria-label="Close">&times;</button><div class="b"></div>';
  document.body.appendChild(panel);
  panel.querySelector('.x').onclick = () => panel.classList.remove('open');
  const pb = panel.querySelector('.b');

  const bridgeEls = [];
  E.slice().sort((a, b) => b.papers.length - a.papers.length).forEach(e => {
    const x1 = LX, y1 = fy[e.fund], x2 = RX, y2 = dy[e.domain], c = (x1 + x2) / 2;
    const p = el('path', { class: 'bridge', d: `M${x1},${y1} C${c},${y1} ${c},${y2} ${x2},${y2}`,
      stroke: COLOR[e.fund], 'stroke-width': wOf(e.papers.length), 'stroke-opacity': .5 });
    p.addEventListener('mousemove', ev => showTip(ev, `<b>${esc(flbl[e.fund])} &rarr; ${esc(dlbl[e.domain])}</b><span>${e.papers.length} stud${e.papers.length > 1 ? 'ies' : 'y'} &middot; click to read</span>`));
    p.addEventListener('mouseleave', () => tip.style.display = 'none');
    p.addEventListener('mouseenter', () => highlight(e.fund));
    p.addEventListener('click', () => openEdge(e));
    svg.appendChild(p); bridgeEls.push({ p, fund: e.fund });
  });

  F.forEach(f => {
    const y = fy[f.id], r = rOf(f.id);
    const g = el('g', { class: 'node' });
    g.appendChild(el('circle', { cx: LX, cy: y, r, fill: COLOR[f.id], 'fill-opacity': fOut[f.id] ? .9 : .25, stroke: COLOR[f.id], 'stroke-opacity': .5 }));
    const t = el('text', { x: LX - r - 10, y: y + 4, 'text-anchor': 'end', class: 'node-lbl' }); t.textContent = f.label; g.appendChild(t);
    const s = el('text', { x: LX - r - 10, y: y + 18, 'text-anchor': 'end', class: 'node-sub' }); s.textContent = fOut[f.id] ? fOut[f.id] + ' applications' : 'not yet applied'; g.appendChild(s);
    g.addEventListener('mouseenter', () => highlight(f.id));
    g.addEventListener('mouseleave', () => highlight(null));
    svg.appendChild(g);
  });
  domOrder.forEach(d => {
    const y = dy[d.id];
    const g = el('g', {});
    g.appendChild(el('circle', { cx: RX, cy: y, r: 5, fill: '#9aa6bd' }));
    const t = el('text', { x: RX + 14, y: y + 4, 'text-anchor': 'start', class: 'node-lbl' }); t.textContent = d.label; g.appendChild(t);
    const s = el('text', { x: RX + 14, y: y + 18, 'text-anchor': 'start', class: 'node-sub' }); s.textContent = dIn[d.id] + ' studies'; g.appendChild(s);
    svg.appendChild(g);
  });

  function highlight(fund) {
    bridgeEls.forEach(b => {
      b.p.classList.toggle('dim', fund && b.fund !== fund);
      b.p.setAttribute('stroke-opacity', !fund ? .5 : (b.fund === fund ? .85 : .5));
    });
  }
  function showTip(ev, html) {
    tip.innerHTML = html; tip.style.display = 'block';
    let x = ev.clientX + 14, y = ev.clientY + 14; const r = tip.getBoundingClientRect();
    if (x + r.width > innerWidth - 10) x = ev.clientX - r.width - 14;
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  function openEdge(e) {
    let h = `<div class="tag" style="color:${COLOR[e.fund]}">Translation</div>`;
    h += `<h2>${esc(flbl[e.fund])} &rarr; ${esc(dlbl[e.domain])}</h2><p class="c">${e.papers.length} stud${e.papers.length > 1 ? 'ies' : 'y'}</p>`;
    e.papers.forEach(id => {
      const p = paperById[id], link = p.doi ? `https://doi.org/${p.doi}` : `https://scholar.google.com/scholar?q=${encodeURIComponent(p.title)}`;
      h += `<div class="art"><a href="${esc(link)}" target="_blank" rel="noopener">${esc(p.title)}</a><div class="meta">${p.year || 'Book'}</div></div>`;
    });
    pb.innerHTML = h; panel.classList.add('open'); panel.scrollTop = 0;
  }

  // Full study list, grouped by domain (newest first).
  const list = document.getElementById('study-list');
  if (list) {
    let h = '';
    domOrder.forEach(d => {
      const ps = D.papers.filter(p => p.domain === d.id).sort((a, b) => (b.year || 0) - (a.year || 0));
      if (!ps.length) return;
      h += `<div class="dom-group"><h3>${esc(d.label)} <span>${ps.length}</span></h3>`;
      ps.forEach(p => {
        const link = p.doi ? `https://doi.org/${p.doi}` : `https://scholar.google.com/scholar?q=${encodeURIComponent(p.title)}`;
        h += `<a class="study" href="${esc(link)}" target="_blank" rel="noopener"><span class="st">${esc(p.title)}</span><span class="sm">${esc(flbl[p.fund])} &middot; ${p.year || 'Book'}</span></a>`;
      });
      h += `</div>`;
    });
    list.innerHTML = h;
  }
})();
