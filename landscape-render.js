/* Renders the combination-landscape matrix into #landscape-matrix.
   Expects window.LANDSCAPE (data/landscape.js). Adds its own tooltip + panel. */
(function () {
  const D = window.LANDSCAPE;
  const mount = document.getElementById('landscape-matrix');
  if (!D || !mount) return;
  const P = D.processes, N = P.length;
  const fkey = (a, b) => [a, b].sort().join('|');
  const el = (t, c) => { const e = document.createElement(t); if (c) e.className = c; return e; };
  const esc = s => String(s || '').replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

  const fieldMap = {}, labMap = {}; let maxN = 1;
  D.field.forEach(f => { fieldMap[fkey(f.a, f.b)] = { n: f.n, refs: f.refs }; if (f.n > maxN) maxN = f.n; });
  D.lab.forEach(l => { labMap[fkey(l.a, l.b)] = l.studies; });

  const alpha = n => (.18 + .62 * Math.log(n + 1) / Math.log(maxN + 1)).toFixed(2);

  const grid = el('div'); grid.id = 'lsm';
  grid.style.gridTemplateColumns = `auto repeat(${N}, 1fr)`;
  grid.appendChild(el('div'));
  P.forEach(p => { const c = el('div', 'collbl'); c.textContent = p.label; grid.appendChild(c); });
  P.forEach((rp, r) => {
    const lbl = el('div', 'rowlbl'); lbl.textContent = rp.label; grid.appendChild(lbl);
    P.forEach((cp, c) => {
      const cell = el('div', 'cell');
      if (r === c) cell.classList.add('diag');
      else {
        const k = fkey(rp.id, cp.id), fm = fieldMap[k], fn = fm ? fm.n : 0, lab = labMap[k];
        if (fn > 0) cell.style.setProperty('--a', alpha(fn));
        // A pair we have worked on that the field has too gets split diagonally,
        // so our claim on it never hides how much other work is already there.
        if (lab && fn > 0) cell.classList.add('both');
        else if (lab) cell.classList.add('lab');
        else if (fn > 0) cell.classList.add('field');
        else cell.classList.add('open');
        cell.onmousemove = e => tipShow(e, rp, cp, fn, lab);
        cell.onmouseleave = () => tip.style.display = 'none';
        cell.onclick = () => openCell(rp, cp, fm, lab);
      }
      grid.appendChild(cell);
    });
  });
  mount.appendChild(grid);

  const tip = el('div'); tip.id = 'ls-tip'; document.body.appendChild(tip);
  function tipShow(e, rp, cp, fn, lab) {
    let h = `<b>${esc(rp.label)} &times; ${esc(cp.label)}</b>`;
    const st = n => `stud${n === 1 ? 'y' : 'ies'}`;
    if (lab && fn) h += `<span class="s lab">our lab, and ${fn} other field ${st(fn)} &middot; click to read</span>`;
    else if (lab) h += `<span class="s lab">our lab &middot; click to read</span>`;
    else if (fn) h += `<span class="s">${fn} field ${st(fn)} &middot; click to read</span>`;
    else h += `<span class="s">open frontier &middot; click to propose</span>`;
    tip.innerHTML = h; tip.style.display = 'block';
    let x = e.clientX + 14, y = e.clientY + 14; const r = tip.getBoundingClientRect();
    if (x + r.width > innerWidth - 10) x = e.clientX - r.width - 14;
    if (y + r.height > innerHeight - 10) y = e.clientY - r.height - 14;
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }

  const panel = el('aside'); panel.id = 'ls-panel';
  panel.innerHTML = '<button class="x" aria-label="Close">&times;</button><div class="b"></div>';
  document.body.appendChild(panel);
  panel.querySelector('.x').onclick = () => panel.classList.remove('open');
  const pbody = panel.querySelector('.b');
  function openCell(rp, cp, fm, lab) {
    const title = `${esc(rp.label)} &times; ${esc(cp.label)}`; let h = '';
    const fieldList = () => fm.refs.map(i => { const a = D.articles[i];
      const href = a.u && !/^https?:/.test(a.u) ? 'https://doi.org/' + a.u : a.u;
      // A handful of older records carry no DOI; show the title unlinked.
      const t = href ? `<a href="${esc(href)}" target="_blank" rel="noopener">${esc(a.t)}</a>` : esc(a.t);
      return `<div class="art">${t}<div class="meta">${esc(a.a)}${a.y ? ' &middot; ' + a.y : ''}</div></div>`;
    }).join('');
    const shown = n => n > 8 ? ', 8 most cited shown' : '';
    if (lab) {
      h += `<div class="tag lab">Our lab</div><h3>${title}</h3>`;
      lab.forEach(s => h += `<div class="art"><a href="https://doi.org/${esc(s.doi)}" target="_blank" rel="noopener">${esc(s.study)}</a></div>`);
      if (fm && fm.n) {
        h += `<p class="c" style="margin-top:1.4rem">${fm.n} other paper${fm.n > 1 ? 's' : ''} in the field co-study this pair${shown(fm.n)}</p>` + fieldList();
      }
    } else if (fm && fm.n) {
      h += `<div class="tag field">Studied by the field</div><h3>${title}</h3><p class="c">${fm.n} paper${fm.n > 1 ? 's' : ''} co-study this pair${shown(fm.n)}</p>`;
      h += fieldList();
    } else {
      const subj = encodeURIComponent(`Collaboration: ${rp.label} × ${cp.label}`);
      h += `<div class="tag open">Open frontier</div><h3>${title}</h3><p class="c">No one has co-studied this pair yet. Want to take it on with us?</p><a class="cta" href="mailto:dcox@endicott.edu?subject=${subj}">Propose this study &rarr;</a>`;
    }
    pbody.innerHTML = h; panel.classList.add('open'); panel.scrollTop = 0;
  }
})();
