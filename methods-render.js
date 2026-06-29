/* Renders the "expanded toolchest" radial into #methods-radial from window.CORPUS.
   Hub = traditional toolkit; each spoke = a capability; each paper = a node
   radiating outward (oldest nearest the hub, newest farthest). */
(function () {
  const wrap = document.getElementById('methods-radial');
  if (!wrap) return;
  // Order matters: spokes are placed clockwise from the top, so adjacency follows this list.
  const CAPS = [
    { fam: 'Work at scale', color: '#6cc5ff', trad: 'one graph at a time', now: 'whole literatures and large datasets', papers: [
      { kw: 'scaling n from 1', short: 'Scaling N to 1,000,000' },
      { kw: 'identifying trends in the open-access', short: 'Literature trends' },
      { kw: 'behavioral data science', short: 'Behavioral data science' }] },
    { fam: 'Modeling', color: '#a98bff', trad: 'verbal description', now: 'quantitative and computational models', papers: [
      { kw: 'the many functions of quantitative modeling', short: 'Functions of modeling' },
      { kw: 'we live in interesting times', short: 'Big-data special section' },
      { kw: 'quantitative frontiers in the analysis', short: 'Quantitative frontiers' },
      { kw: 'of models, vectors, and matrices', short: 'Models & matrices' }] },
    { fam: 'Machine learning', color: '#ff7a9c', trad: 'hand-scoring graphs', now: 'algorithms that read, score, and predict', papers: [
      { kw: 'recommending hours', short: 'ML for ABA hours' },
      { kw: 'televisibility', short: 'Televisibility study' },
      { kw: 'predicting the next response', short: 'RL predicts responses' },
      { kw: 'using ml to analyze alternating treatment graphs', short: 'ML for graphs' }] },
    { fam: 'Statistics', color: '#ffd166', trad: 'visual inspection', now: 'principled inference built for ABA', papers: [
      { kw: 'statistics for aba practitioners', short: 'Statistics for ABA' }] },
    { fam: 'Measurement', color: '#5fd6a4', trad: 'count and rate', now: 'movement, field cameras, richer agreement, adjusting tasks', papers: [
      { kw: 'further comparison of 5-trial', short: '5-trial tasks' },
      { kw: 'data recording and analysis', short: 'Data recording' },
      { kw: 'getting more from your ioa data', short: 'IOA measures' },
      { kw: 'escape from static flatland', short: 'Behavior as movement' },
      { kw: 'free-ranging aves', short: 'Field camera traps' }] },
    { fam: 'Design', color: '#7ce0e0', trad: 'convention', now: 'explicit single-case logic, replication, functional terms', papers: [
      { kw: 'within-subject experimental design logic', short: 'Within-subject logic' },
      { kw: 'function matters', short: 'Function & terms' },
      { kw: 'multidisciplinary replication of upper', short: 'Upper replication' }] },
    { fam: 'Reproducible tools', color: '#c3a3ff', trad: 'bespoke and manual', now: 'shared code and templates others reuse', papers: [
      { kw: 'training staff to create equivalence-based instruction', short: 'EBI in Qualtrics' },
      { kw: 'the logic and code behind the cover', short: 'Cover/ToC graphs' },
      { kw: 'readme- the code to create', short: 'Cover graphics code' }] },
  ];
  const items = (window.CORPUS && window.CORPUS.items) || [];
  const find = kw => items.find(it => it.title.toLowerCase().includes(kw));
  const esc = s => String(s || '').replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  const linkOf = it => it.doi ? 'https://doi.org/' + it.doi : 'https://scholar.google.com/scholar?q=' + encodeURIComponent(it.title);

  const NS = 'http://www.w3.org/2000/svg';
  const lines = document.createElementNS(NS, 'svg');
  lines.setAttribute('class', 'lines'); lines.setAttribute('viewBox', '0 0 1360 1360'); lines.setAttribute('preserveAspectRatio', 'none');
  wrap.appendChild(lines);

  const C = 680, r0 = 158, rstep = 110, N = CAPS.length;
  const hub = document.createElement('div'); hub.className = 'hub'; hub.style.left = (C - 98) + 'px'; hub.style.top = (C - 98) + 'px';
  hub.innerHTML = '<div class="ht">TRADITIONAL TOOLCHEST</div><div class="hs">single-subject design &middot; visual analysis &middot; descriptive statistics</div>';
  wrap.appendChild(hub);

  const tip = document.createElement('div'); tip.id = 'methods-tip'; document.body.appendChild(tip);
  const panel = document.createElement('aside'); panel.id = 'methods-panel';
  panel.innerHTML = '<button class="x" aria-label="Close">&times;</button><div class="b"></div>';
  document.body.appendChild(panel);
  panel.querySelector('.x').onclick = () => panel.classList.remove('open');
  const pb = panel.querySelector('.b');
  function showTip(ev, html) {
    tip.innerHTML = html; tip.style.display = 'block';
    let x = ev.clientX + 14, y = ev.clientY + 14; const r = tip.getBoundingClientRect();
    if (x + r.width > innerWidth - 10) x = ev.clientX - r.width - 14;
    if (y + r.height > innerHeight - 10) y = ev.clientY - r.height - 14;
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  const groups = [];
  function highlight(i) { groups.forEach((g, k) => g.forEach(e => e.classList.toggle('dim', i != null && k !== i))); }

  CAPS.forEach((c, i) => {
    const ang = (i * 360 / N - 90) * Math.PI / 180, dx = Math.cos(ang), dy = Math.sin(ang);
    const ps = c.papers.map(p => ({ ...p, it: find(p.kw) })).filter(p => p.it).sort((a, b) => (a.it.year || 0) - (b.it.year || 0));
    const maxR = r0 + (ps.length - 1) * rstep, g = [];
    const ln = document.createElementNS(NS, 'line');
    ln.setAttribute('x1', C); ln.setAttribute('y1', C); ln.setAttribute('x2', C + maxR * dx); ln.setAttribute('y2', C + maxR * dy);
    ln.setAttribute('stroke', c.color); ln.setAttribute('stroke-opacity', '.3'); ln.setAttribute('stroke-width', '2'); lines.appendChild(ln); g.push(ln);
    ps.forEach((p, j) => {
      const r = r0 + j * rstep, x = C + r * dx, y = C + r * dy;
      const nd = document.createElement('div'); nd.className = 'node'; nd.style.left = (x - 50) + 'px'; nd.style.top = (y - 50) + 'px'; nd.style.borderColor = c.color;
      nd.innerHTML = `<div class="lbl">${esc(p.short)}</div><div class="yr">${p.it.year || ''}</div>`;
      nd.addEventListener('mousemove', ev => showTip(ev, `${esc(p.it.title)}<span class="m">${esc(c.fam)} &middot; ${p.it.year || ''} &middot; click to read</span>`));
      nd.addEventListener('mouseleave', () => tip.style.display = 'none');
      nd.addEventListener('mouseenter', () => highlight(i));
      nd.addEventListener('click', () => window.open(linkOf(p.it), '_blank'));
      wrap.appendChild(nd); g.push(nd);
    });
    const lr = maxR + 66, lx = C + lr * dx, ly = C + lr * dy;
    const lab = document.createElement('div'); lab.className = 'caplabel'; lab.style.left = lx + 'px'; lab.style.top = ly + 'px'; lab.style.color = c.color;
    lab.style.transform = `translate(${dx > 0.3 ? '0' : dx < -0.3 ? '-100%' : '-50%'},${dy > 0.3 ? '0' : dy < -0.3 ? '-100%' : '-50%'})`;
    lab.textContent = c.fam;
    lab.addEventListener('mouseenter', () => highlight(i)); lab.addEventListener('mouseleave', () => highlight(null));
    lab.addEventListener('click', () => {
      let h = `<div class="fam" style="color:${c.color}">${esc(c.fam)}</div><h2>${esc(c.fam)}</h2>`;
      h += `<div class="contrast"><b>Traditionally</b> ${esc(c.trad)} <span class="ar">&rarr;</span> <b>now</b> ${esc(c.now)}.</div><div class="ph">Papers</div>`;
      ps.forEach(p => { h += `<a class="paper" href="${esc(linkOf(p.it))}" target="_blank" rel="noopener">${esc(p.it.title)} <span class="yr">${p.it.year || ''}</span></a>`; });
      pb.innerHTML = h; panel.classList.add('open'); panel.scrollTop = 0;
    });
    wrap.appendChild(lab); g.push(lab);
    groups.push(g);
  });
})();
