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
  const STATE = { lab: "Our lab's AO", field: "Another group's AO of this approach", both: "Our lab's AO and another group's", open: 'No AO of this approach yet' };
  grid.querySelectorAll('.aocell').forEach(dc => {
    dc.addEventListener('mousemove', ev => {
      const note = D.notes[dc.dataset.row + '|' + dc.dataset.col];
      tip.innerHTML = `<b>${rowLabel[dc.dataset.row]}</b><span class="ap">${colLabel[dc.dataset.col]}</span>`
        + `<span class="st st-${dc.dataset.state}">${STATE[dc.dataset.state]}</span>`
        + (note ? `<span class="nt">${note}</span>` : '');
      tip.style.display = 'block';
      let x = ev.clientX + 14, y = ev.clientY + 14; const r = tip.getBoundingClientRect();
      if (x + r.width > innerWidth - 10) x = ev.clientX - r.width - 14;
      if (y + r.height > innerHeight - 10) y = ev.clientY - r.height - 14;
      tip.style.left = x + 'px'; tip.style.top = y + 'px';
    });
    dc.addEventListener('mouseleave', () => tip.style.display = 'none');
  });
})();
