/* Publications page. Renders window.PUBS (data/publications.js, built by
   scripts/build_publications.py) as a filterable index grouped by year.
   Filters: text search, topic and form (multi-tags from
   data/publication_tags.json; an entry passes if it carries any selected
   tag), and a year range brushed on the histogram. */
(function () {
  const D = window.PUBS;
  if (!D) return;
  const PALETTE = ['#3b8acd','#ab78fd','#1ff7df','#fecb28','#fe87ba','#379062',
                   '#7dc1fb','#e84d37','#6ac358','#be449c','#9aa6bd'];
  // topic ids are positions in the fixed _topics list of
  // data/publication_tags.json (not map cluster ids, which shift with cluster
  // size); 8 and 9 are tags with no map region. topic-map.js uses the same
  // label -> color pairs. The ten hues were checked for normal and
  // color-blind separation against the page background.
  const colorOf = id => id == null ? '#6b7689' : PALETTE[id % PALETTE.length];
  const PROGRESS = 'In progress';
  const FORMS = [...D.forms, PROGRESS];
  const topicLabel = id => D.topics[id].label;
  const STATUS_GROUPS = [
    ['inpress', 'Forthcoming', 'In press'],
    ['inreview', 'In review', 'Under review'],
    ['preprint', 'Preprints', 'Working papers'],
  ];
  const formsOf = p => p.status !== 'published' ? [...p.forms, PROGRESS] : p.forms;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const items = D.items.map(p => ({
    ...p,
    _forms: formsOf(p),
    _hay: [p.title, p.authors, p.venue, ...p.topics.map(topicLabel), ...p.forms].join(' ').toLowerCase(),
  }));
  const years = items.filter(p => p.year).map(p => p.year);
  const minY = Math.min(...years), maxY = Math.max(...years);

  const state = { q: '', topics: new Set(), forms: new Set(), range: null };

  const $ = id => document.getElementById(id);
  const list = $('pubs-list');

  // ---- filtering
  function passes(p, ignore) {
    if (state.q && !state.q.split(/\s+/).every(w => p._hay.includes(w))) return false;
    if (ignore !== 'topic' && state.topics.size && !p.topics.some(t => state.topics.has(t))) return false;
    if (ignore !== 'form' && state.forms.size && !p._forms.some(f => state.forms.has(f))) return false;
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
    // topics show as dots only; the name is in the hover title
    const dots = p.topics.map(t =>
      `<span class="dot" style="--c:${colorOf(t)}" title="${esc(topicLabel(t))}" role="img" aria-label="${esc(topicLabel(t))}"></span>`).join('');
    const bits = dots ? [`<span class="e-topics">${dots}</span>`] : [];
    const forms = p.forms.length ? p.forms
      : [{ article: 'Article', chapter: 'Chapter', book: 'Book', report: 'Report' }[p.kind]];
    bits.push(`<span class="e-kind">${forms.map(esc).join(' &middot; ')}</span>`);
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
          `<article class="ix-entry">${entryBody(p)}</article>`).join('')}</div>
      </div>`).join('');
  }

  // ---- filter dropdowns: a button that opens a panel of checkboxes
  function option(label, checked, color, n, onChange) {
    const l = document.createElement('label');
    l.className = 'dd-opt';
    if (color) l.style.setProperty('--c', color);
    l.innerHTML = `<input type="checkbox"${checked ? ' checked' : ''}>` +
      (color ? '<span class="dot"></span>' : '') +
      `<span class="lbl">${esc(label)}</span><span class="n">${n}</span>`;
    l.firstChild.dataset.v = label;
    l.firstChild.addEventListener('change', onChange);
    return l;
  }
  function toggle(set, v) { set.has(v) ? set.delete(v) : set.add(v); render(); }
  // rebuilding a panel drops focus, so put it back on the same option
  function fill(panel, opts) {
    const f = panel.contains(document.activeElement) && document.activeElement.dataset.v;
    panel.replaceChildren(...opts);
    if (f) [...panel.querySelectorAll('input')].find(i => i.dataset.v === f)?.focus();
  }
  // the button names a lone choice and counts several
  const summary = names => !names.length ? 'All' : names.length === 1 ? names[0] : `${names.length} selected`;
  function renderChips() {
    const topics = $('pubs-topics'), forms = $('pubs-types');
    fill(topics, [
      Object.assign(document.createElement('p'), { className: 'dd-note', textContent: 'Topics are shown in color in the chart and list' }),
      ...D.topics
        .map(c => [c, items.filter(p => p.topics.includes(c.id) && passes(p, 'topic')).length])
        .filter(([c, n]) => n || state.topics.has(c.id))
        .map(([c, n]) => option(c.label, state.topics.has(c.id), colorOf(c.id), n, () => toggle(state.topics, c.id))),
    ]);
    fill(forms, FORMS
      .map(f => [f, items.filter(p => p._forms.includes(f) && passes(p, 'form')).length])
      .filter(([f, n]) => n || state.forms.has(f))
      .map(([f, n]) => option(f, state.forms.has(f), null, n, () => toggle(state.forms, f))));
    $('pubs-topics-sum').textContent = summary(D.topics.filter(c => state.topics.has(c.id)).map(c => c.label));
    $('pubs-types-sum').textContent = summary(FORMS.filter(f => state.forms.has(f)));
  }
  function openDd(dd, open) {
    dd.querySelector('.pubs-dd-btn').setAttribute('aria-expanded', open);
    dd.querySelector('.pubs-dd-panel').hidden = !open;
    dd.classList.toggle('open', open);
  }
  document.querySelectorAll('.pubs-dd').forEach(dd => {
    dd.querySelector('.pubs-dd-btn').addEventListener('click', () => {
      const open = !dd.classList.contains('open');
      document.querySelectorAll('.pubs-dd.open').forEach(o => openDd(o, false));
      openDd(dd, open);
    });
  });
  document.addEventListener('click', e => {
    document.querySelectorAll('.pubs-dd.open').forEach(dd => { if (!dd.contains(e.target)) openDd(dd, false); });
  });
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.pubs-dd.open').forEach(dd => { openDd(dd, false); dd.querySelector('.pubs-dd-btn').focus(); });
  });

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
      (counts[y] || []).forEach(p => { byCluster[p.primary] = (byCluster[p.primary] || 0) + 1; });
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
    state.topics.clear(); state.forms.clear(); state.range = null;
    render();
  });
  window.addEventListener('resize', () => renderHist());

  const total = items.length;

  // names the active filters, e.g. "Showing 51 of 107: Empirical, 2018 to 2022"
  function activeFilters() {
    const parts = [];
    if (state.q) parts.push(`"${state.q}"`);
    if (state.topics.size) parts.push(D.topics.filter(c => state.topics.has(c.id)).map(c => c.label).join(' or '));
    if (state.forms.size) parts.push(FORMS.filter(f => state.forms.has(f)).join(' or '));
    if (state.range) parts.push(state.range[0] === state.range[1] ? `${state.range[0]}` : `${state.range[0]} to ${state.range[1]}`);
    return parts;
  }

  // ---- export: whatever is currently shown, as BibTeX, RIS, or APA text
  let current = [];
  const isInitials = s => /^(?:[A-Z][a-z]?\.?\s?-?\s?)+$/.test(s) && !/^(?:Jr|Sr|I{2,3}|IV)\.?$/.test(s);
  // "Cox, D.J., Garcia-Romeu, A., & Johnson, M.W." -> [["Cox","D.J."], ...];
  // a corporate author stays whole
  function people(a) {
    const t = String(a || '').replace(/\s*,?\s*&\s*/g, ', ').split(/,\s*/).filter(Boolean);
    const out = [];
    for (let i = 0; i < t.length; i++) {
      if (/^\.{3}|\u2026/.test(t[i])) continue;                       // "..." in long author lists
      if (/^(?:Jr|Sr|I{2,3}|IV)\.?$/.test(t[i]) && out.length) {     // "Hardy, J. H., III."
        out[out.length - 1][1] = (out[out.length - 1][1] || '') + ' ' + t[i]; continue;
      }
      if (t[i + 1] && isInitials(t[i + 1])) { out.push([t[i], t[i + 1]]); i++; }
      else out.push([t[i]]);
    }
    return out;
  }
  // "Journal Name, 71(4), 349-366" -> {journal, volume, number, pages}
  function venueParts(v) {
    const m = String(v || '').match(/^(.*?),\s*(\d+)(?:\(([^)]+)\))?(?:,\s*([\w\u2013-]+))?\.?$/);
    return m ? { journal: m[1], volume: m[2], number: m[3], pages: m[4] } : { journal: v || '' };
  }
  const doiOf = url => (String(url || '').match(/doi\.org\/(10\..+)$/i) || [])[1];
  const plainStatus = { inpress: 'In press', inreview: 'Manuscript under review', preprint: 'Preprint' };
  function bibKey(p, used) {
    const who = (people(p.authors)[0] || ['anon'])[0].normalize('NFD').replace(/[^A-Za-z]/g, '');
    const word = (p.title.toLowerCase().match(/[a-z]{4,}/) || ['work'])[0];
    let k = `${who}${p.year || p.status}${word}`, n = 1;
    while (used.has(k)) k = `${who}${p.year || p.status}${word}${++n}`;
    used.add(k);
    return k;
  }
  function toBib(list) {
    const used = new Set();
    return list.map(p => {
      const f = [], v = venueParts(p.venue), doi = doiOf(p.link);
      const auth = people(p.authors).map(([s, g]) => g ? `${s}, ${g}` : `{${s}}`).join(' and ');
      let type = 'article';
      f.push(['title', `{${p.title}}`], ['author', auth]);
      if (p.year) f.push(['year', p.year]);
      if (p.status !== 'published') { type = 'unpublished'; f.push(['note', [plainStatus[p.status], p.venue].filter(Boolean).join('. ')]); }
      else if (p.kind === 'chapter') { type = 'incollection'; f.push(['booktitle', p.venue.replace(/^In\s+/, '')]); }
      else if (p.kind === 'book') { type = 'book'; f.push(['publisher', p.venue]); }
      else if (p.kind === 'report') { type = 'techreport'; f.push(['institution', p.authors]); }
      else { f.push(['journal', v.journal]); if (v.volume) f.push(['volume', v.volume]); if (v.number) f.push(['number', v.number]); if (v.pages) f.push(['pages', v.pages.replace(/[-\u2013]/, '--')]); }
      if (doi) f.push(['doi', doi]); else if (p.link) f.push(['url', p.link]);
      return `@${type}{${bibKey(p, used)},\n` + f.map(([k, x]) => `  ${k} = {${x}}`).join(',\n') + '\n}';
    }).join('\n\n') + '\n';
  }
  function toRis(list) {
    return list.map(p => {
      const r = [], v = venueParts(p.venue), doi = doiOf(p.link);
      const ty = p.status !== 'published' ? 'UNPB' : { chapter: 'CHAP', book: 'BOOK', report: 'RPRT' }[p.kind] || 'JOUR';
      r.push(['TY', ty]);
      people(p.authors).forEach(([s, g]) => r.push(['AU', g ? `${s}, ${g}` : s]));
      r.push(['TI', p.title]);
      if (p.year) r.push(['PY', p.year]);
      if (ty === 'JOUR') { r.push(['JO', v.journal]); if (v.volume) r.push(['VL', v.volume]); if (v.number) r.push(['IS', v.number]);
        if (v.pages) { const [sp, ep] = v.pages.split(/[-\u2013]/); r.push(['SP', sp]); if (ep) r.push(['EP', ep]); } }
      else if (p.venue) r.push([ty === 'CHAP' ? 'T2' : ty === 'BOOK' ? 'PB' : 'N1', p.venue]);
      if (doi) r.push(['DO', doi]);
      if (p.link) r.push(['UR', p.link]);
      r.push(['ER', '']);
      return r.map(([k, x]) => `${k}  - ${x}`).join('\r\n');
    }).join('\r\n\r\n') + '\r\n';
  }
  // APA 7: in-press work is "(in press)"; undated manuscripts and preprints
  // are "(n.d.)" with a bracketed description after the title
  const apaNote = { inreview: ' [Manuscript submitted for publication]', preprint: ' [Preprint]' };
  function toApa(list) {
    return list.map(p => {
      const when = p.year || (p.status === 'inpress' ? 'in press' : 'n.d.');
      const title = p.title.replace(/[.?!]?$/, m => m || '.').replace(/\.$/, '') + (apaNote[p.status] || '') + (/[?!]$/.test(p.title) && !apaNote[p.status] ? '' : '.');
      return [`${p.authors} (${when}).`, title, p.venue ? `${p.venue}.` : '', p.link || '']
        .filter(Boolean).join(' ');
    }).join('\n\n') + '\n';
  }
  $('pubs-export').addEventListener('click', e => {
    const fmt = e.target.dataset && e.target.dataset.fmt;
    if (!fmt) return;
    const [text, ext, mime] = fmt === 'bib' ? [toBib(current), 'bib', 'application/x-bibtex']
      : fmt === 'ris' ? [toRis(current), 'ris', 'application/x-research-info-systems']
      : [toApa(current), 'txt', 'text/plain'];
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type: mime + ';charset=utf-8' }));
    a.download = `cox-lab-publications.${ext}`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });

  function render() {
    const shown = items.filter(p => passes(p));
    renderChips();
    renderHist();
    const active = activeFilters();
    $('pubs-reset').hidden = !active.length;
    $('pubs-range').textContent = state.range
      ? (state.range[0] === state.range[1] ? `${state.range[0]}` : `${state.range[0]} to ${state.range[1]}`)
      : `All years, ${minY} to ${maxY}`;
    // the count line names the filters only while one is on
    $('pubs-count').innerHTML = active.length
      ? `Showing <b>${shown.length}</b> of ${total}: ${esc(active.join(', '))}`
      : '';
    current = shown;
    $('pubs-export-n').textContent = `Download ${shown.length === total ? 'all ' + total : shown.length} as`;
    $('pubs-export').hidden = !shown.length;
    if (!shown.length) {
      list.innerHTML = '<p class="pubs-empty">Nothing matches those filters.</p>';
      return;
    }
    renderIndex(shown);
  }
  render();
})();
