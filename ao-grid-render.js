/* Renders the AO coverage grid into #ao-grid from window.AOGRID. */
(function () {
  const D = window.AOGRID;
  const mount = document.getElementById('ao-grid');
  if (!D || !mount) return;

  const labOf = c => D.lab[c] || [];
  const stateOf = (row, col) => {
    const l = labOf(col);
    const isLab = l === '*' || (Array.isArray(l) && l.includes(row));
    const isField = (D.field[col] || []).includes(row);
    if (isLab && isField) return 'both';
    if (isLab) return 'lab';
    if (isField) return 'field';
    return 'open';
  };
  const rowLabel = {}; D.groups.forEach(g => g.rows.forEach(r => rowLabel[r[0]] = r[1]));
  const colLabel = Object.fromEntries(D.cols.map(c => [c.id, c.label]));

  const grid = document.createElement('div');
  grid.className = 'aogrid';
  grid.style.gridTemplateColumns = `minmax(210px, 1.7fr) repeat(${D.cols.length}, 1fr)`;

  const cell = (cls, html) => { const d = document.createElement('div'); d.className = cls; if (html != null) d.innerHTML = html; return d; };

  // header
  grid.appendChild(cell('aoh corner', ''));
  D.cols.forEach(c => grid.appendChild(cell('aoh col', c.label)));

  D.groups.forEach(g => {
    const gh = cell('aogroup', g.label); gh.style.gridColumn = '1 / -1'; grid.appendChild(gh);
    g.rows.forEach(([rid, rlabel]) => {
      grid.appendChild(cell('aorow', rlabel));
      D.cols.forEach(c => {
        const st = stateOf(rid, c.id);
        const dc = cell('aocell ' + st, '');
        dc.dataset.row = rid; dc.dataset.col = c.id; dc.dataset.state = st;
        grid.appendChild(dc);
      });
    });
  });
  mount.appendChild(grid);

  // tooltip
  const tip = document.createElement('div'); tip.id = 'aogrid-tip'; document.body.appendChild(tip);
  const STATE = { lab: 'Done by our lab', field: 'Done by another researcher', both: 'Done by our lab and others', open: 'Not yet done with this AO' };
  const esc = s => String(s || '').replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

  // detail panel (click)
  const panel = document.createElement('aside'); panel.id = 'aogrid-panel';
  panel.innerHTML = '<button class="x" aria-label="Close">&times;</button><div class="b"></div>';
  document.body.appendChild(panel);
  panel.querySelector('.x').onclick = () => panel.classList.remove('open');
  const pb = panel.querySelector('.b');
  const refsOf = dc => (D.refs || {})[dc.dataset.row + '|' + dc.dataset.col];
  const scholar = c => 'https://scholar.google.com/scholar?q=' + encodeURIComponent(c.replace(/\.$/, ''));
  function openCell(dc) {
    const row = dc.dataset.row, col = dc.dataset.col, st = dc.dataset.state;
    const note = D.notes[row + '|' + col], refs = refsOf(dc);
    let h = `<div class="tag st-${st}">${STATE[st]}</div><h2>${rowLabel[row]}</h2><p class="c">${colLabel[col]}</p>`;
    if (note) h += `<p class="nt">${note}</p>`;
    if (refs && refs.length) {
      h += `<div class="refs-h">${st === 'lab' ? 'Our work' : 'Other researchers'}</div>`;
      refs.forEach(r => h += `<a class="ref" href="${scholar(r)}" target="_blank" rel="noopener">${esc(r)}</a>`);
    } else if (st === 'open') {
      h += '<p class="nt">No AO of this approach has reproduced this yet. An open invitation to collaborate.</p>';
    }
    pb.innerHTML = h; panel.classList.add('open'); panel.scrollTop = 0;
  }

  grid.querySelectorAll('.aocell').forEach(dc => {
    if (refsOf(dc)) dc.style.cursor = 'pointer';
    dc.addEventListener('mousemove', ev => {
      const note = D.notes[dc.dataset.row + '|' + dc.dataset.col], refs = refsOf(dc);
      tip.innerHTML = `<b>${rowLabel[dc.dataset.row]}</b><span class="ap">${colLabel[dc.dataset.col]}</span>`
        + `<span class="st st-${dc.dataset.state}">${STATE[dc.dataset.state]}</span>`
        + (note ? `<span class="nt">${note}</span>` : '')
        + (refs ? `<span class="more">${refs.length} source${refs.length > 1 ? 's' : ''} &middot; click to open</span>` : '');
      tip.style.display = 'block';
      let x = ev.clientX + 14, y = ev.clientY + 14; const r = tip.getBoundingClientRect();
      if (x + r.width > innerWidth - 10) x = ev.clientX - r.width - 14;
      if (y + r.height > innerHeight - 10) y = ev.clientY - r.height - 14;
      tip.style.left = x + 'px'; tip.style.top = y + 'px';
    });
    dc.addEventListener('mouseleave', () => tip.style.display = 'none');
    dc.addEventListener('click', () => { tip.style.display = 'none'; openCell(dc); });
  });
})();
