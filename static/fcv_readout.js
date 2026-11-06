/* Word-aligned Stage 3 readout renderer, shared by the screen and the Share .html export. */
(function (root) {
  'use strict';

  const FCV_SCALE = ['Extremely Low', 'Very Low', 'Low', 'Adequate', 'Well Embedded', 'Very Well Embedded'];
  const CLIMATE_SCALE = ['very_limited', 'limited', 'moderate', 'strong', 'very_strong'];
  const FOCUS_LABELS = { '[S]': 'Sensitivity', '[R]': 'Responsiveness', '[S+R]': 'Sensitivity + Responsiveness' };

  function stripBold(text) {
    return String(text || '').replace(/\*\*/g, '').trim();
  }

  function firstParagraph(text) {
    return String(text || '').split(/\n\s*\n+/).map(p => p.trim()).filter(Boolean);
  }

  function parseStage3Sections(markdown) {
    let text = String(markdown || '').replace(/\r\n?/g, '\n');
    text = text.replace(/^\s*---\s*\n[\s\S]*?\n---\s*\n/, '');
    text = text.replace(/%{2,3}[A-Z][A-Z0-9_]*(?::[^%\n]*)?%{2,3}/g, '');
    text = text.replace(/^#\s+.*$/m, '');
    const sections = { snapshot: '', context: '', strengths: '', gaps: '', risk: '', other: [], found: false };
    const blocks = [];
    let current = { heading: '', level: 0, lines: [] };
    text.split('\n').forEach(line => {
      const match = line.match(/^(#{2,4})\s+(.+?)\s*#*\s*$/);
      if (match) {
        blocks.push(current);
        current = { heading: match[2].trim(), level: match[1].length, lines: [] };
      } else {
        current.lines.push(line);
      }
    });
    blocks.push(current);
    let lead = '';
    blocks.forEach(block => {
      const body = block.lines.join('\n').trim();
      const key = block.heading.replace(/[*_:]/g, '').trim().toLowerCase();
      if (!block.heading || block.level === 2) {
        if (body && !lead) lead = body;
        else if (body) sections.other.push({ heading: block.level === 2 ? block.heading : '', body });
        return;
      }
      if (/^opening assessment/.test(key)) sections.snapshot = body;
      else if (/^operational context/.test(key)) sections.context = body;
      else if (/^strengths?$/.test(key)) sections.strengths = body;
      else if (/^(potential |key )?gaps$/.test(key)) sections.gaps = body;
      else if (/^fcv risk exposure/.test(key)) sections.risk = body;
      else if (/watch list/.test(key)) return;
      else if (body) sections.other.push({ heading: block.heading, body });
    });
    if (!sections.snapshot && lead) {
      const paragraphs = firstParagraph(lead);
      sections.snapshot = paragraphs.shift() || '';
      if (paragraphs.length) sections.other.unshift({ heading: '', body: paragraphs.join('\n\n') });
    } else if (lead) {
      sections.other.unshift({ heading: '', body: lead });
    }
    sections.snapshot = stripBold(sections.snapshot);
    sections.found = !!(sections.context || sections.strengths || sections.gaps ||
      (sections.snapshot && blocks.some(b => b.heading)));
    return sections;
  }

  function create(deps) {
    const esc = deps.esc;
    const md = deps.md;
    const boldFirst = deps.boldFirst;
    const timingLabel = deps.timingLabel || (value => value || '');
    const sentenceEnd = deps.sentenceEnd || (text => {
      const match = String(text).match(/[.!?]["')\]]*(?=\s|$)/);
      return match ? match.index + match[0].length : String(text).length;
    });

    function takeSentences(text, count) {
      let rest = String(text || '').trim();
      const out = [];
      while (rest && out.length < count) {
        const end = sentenceEnd(rest);
        out.push(rest.slice(0, end).trim());
        rest = rest.slice(end).trim();
      }
      return { head: out.join(' '), rest };
    }

    function prose(body) {
      return firstParagraph(body).map(p =>
        (/^\s*(?:[-*+]|\d+[.)])\s/m.test(p) || /\*\*|^#|\|/.test(p))
          ? `<div class="fr-md">${md(p)}</div>`
          : `<p class="fr-p">${boldFirst(p)}</p>`).join('');
    }

    function paragraphs(list) {
      return (list || []).map(t => String(t || '').trim()).filter(Boolean)
        .map(t => `<p class="fr-p">${boldFirst(t)}</p>`).join('');
    }

    function numbering() {
      let n = 0;
      return title => {
        n += 1;
        return `<header class="fr-h1"><span class="fr-h1-num">${String(n).padStart(2, '0')}</span><h2 class="fr-h1-txt">${esc(title)}</h2></header>`;
      };
    }

    function sub(label) {
      return `<h3 class="fr-h2c">${esc(label)}</h3>`;
    }

    function intro(text) {
      return `<p class="fr-intro">${esc(text)}</p>`;
    }

    function infoBox(label, innerHtml) {
      return `<div class="fr-info">${label ? `<div class="fr-info-lbl">${esc(label)}</div>` : ''}<div class="fr-info-body">${innerHtml}</div></div>`;
    }

    function section(cls, innerHtml) {
      return `<section class="fr-section ${cls}">${innerHtml}</section>`;
    }

    function meter(steps, level) {
      if (!level) return '';
      let segments = '';
      for (let i = 1; i <= steps; i++) segments += `<span class="fr-ms${i <= level ? ' fr-c' + i : ''}"></span>`;
      return `<div class="fr-meter" role="img" aria-label="${level} of ${steps}">${segments}</div>`;
    }

    function scorecard(tiles, count) {
      const tileHtml = tiles.map(t => `<div class="fr-sc-tile" data-fr-rating="${esc(t.key)}"><div class="fr-sc-label">${esc(t.label)}</div><div class="fr-sc-value">${esc(t.value || 'Not available')}</div>${meter(t.steps, t.level)}${t.level ? `<div class="fr-sc-scale"><span>${esc(t.lo)}</span><span>${esc(t.hi)}</span></div>` : ''}<div class="fr-sc-def">${esc(t.def)}</div></div>`).join('');
      const pills = (count.pills || []).map(p => `<span class="fr-pill ${p.cls}">${esc(p.text)}</span>`).join('');
      return `<section class="fr-scorecard" aria-label="Assessment ratings">${tileHtml}<div class="fr-sc-count"><div class="fr-sc-count-lbl">${esc(count.label)}</div><div class="fr-sc-count-num">${Number(count.number) || 0}</div>${pills}</div></section><p class="fr-note">Advisory judgments, not official WBG ratings.</p>`;
    }

    function ratingRows(rows) {
      return `<div class="fr-ratings">${rows.map(r => `<div class="fr-rating-row"><div class="fr-rating-meta"><div class="fr-rating-dim">${esc(r.dim)}</div><span class="fr-rating-val ${r.cls}">${esc(r.value || 'Not available')}</span><div class="fr-rating-def">${esc(r.def)}</div></div><div class="fr-rating-why">${r.whyHtml || '<p class="fr-p">No rationale was returned for this rating.</p>'}</div></div>`).join('')}</div>`;
    }

    function priorityTable(headers, rows) {
      const head = headers.map(h => `<th scope="col">${esc(h)}</th>`).join('');
      const body = rows.map(r => `<tr><td class="fr-pt-num">${r.rank}</td><td><a class="fr-pt-link" href="#${r.id}" onclick="var d=document.getElementById('${r.id}');if(d)d.open=true;">${esc(r.title)}</a></td>${r.cells.map(c => `<td>${c}</td>`).join('')}</tr>`).join('');
      return `<table class="fr-ptable"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
    }

    function priorityCard(p) {
      const zones = (p.zones || []).filter(z => z.html).map(z => `<section class="fr-zone"><h4 class="fr-lbl">${esc(z.label)}</h4>${z.html}</section>`).join('');
      const drafts = (p.drafts || []).filter(d => d.text).map(d => `<section class="fr-draft"><div class="fr-draft-lbl">${esc(d.label)}</div>${d.forText ? `<div class="fr-draft-for">For: ${esc(d.forText)}</div>` : ''}<p>${esc(d.text)}</p></section>`).join('');
      const cycle = p.cycle && p.cycle.text ? `<p class="fr-cycle"><strong>${esc(p.cycle.label || 'When to address')}:</strong> ${esc(p.cycle.text)}</p>` : '';
      return `<details class="fr-pc" id="${p.id}"${p.open ? ' open' : ''}><summary class="fr-pc-hdr"><span class="fr-pc-rank">${p.rank}</span><span class="fr-pc-title"><span class="fr-pc-sup">${p.supHtml || ''}</span><span class="fr-pc-title-txt">${esc(p.title)}</span></span><span class="fr-pc-chev" aria-hidden="true"></span></summary><div class="fr-pc-body">${zones}${drafts}${cycle}${p.extraHtml || ''}</div></details>`;
    }

    function disclosure(summary, bodyHtml) {
      return `<details class="fr-disc"><summary class="fr-disc-sum">${esc(summary)}</summary><div class="fr-disc-body">${bodyHtml}</div></details>`;
    }

    function checkItems(items) {
      return items.map((it, i) => `<div class="fr-check"><span class="fr-check-num">${String(i + 1).padStart(2, '0')}</span><div><h4 class="fr-check-title">${esc(it.title)}</h4>${it.why ? `<p class="fr-p">${esc(it.why)}</p>` : ''}${it.how ? `<p class="fr-check-how"><strong>How to address:</strong> ${esc(it.how)}</p>` : ''}</div></div>`).join('');
    }

    function pill(level) {
      const key = String(level || '').toLowerCase();
      return level ? `<span class="fr-pill fr-pill-${esc(key)}">${esc(level)}</span>` : '';
    }

    const kit = { esc, md, boldFirst, timingLabel, takeSentences, prose, paragraphs, numbering, sub, intro, infoBox, section, meter, scorecard, ratingRows, priorityTable, priorityCard, disclosure, checkItems, pill };
    return Object.assign(kit, {
      renderNormal: data => renderNormal(kit, data),
      renderClimate: (reader, opts) => renderClimate(kit, reader, opts),
    });
  }

  function renderNormal() { return ''; }
  function renderClimate() { return ''; }

  const api = { FCV_SCALE, CLIMATE_SCALE, FOCUS_LABELS, parseStage3Sections, create };
  root.FcvReadout = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
