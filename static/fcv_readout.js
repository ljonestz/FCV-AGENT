/* Word-aligned Stage 3 readout renderer, shared by the screen and the Share .html export. */
(function (root) {
  'use strict';

  const FCV_SCALE = ['Extremely Low', 'Very Low', 'Low', 'Adequate', 'Well Embedded', 'Very Well Embedded'];
  const CLIMATE_SCALE = ['very_limited', 'limited', 'moderate', 'strong', 'very_strong'];
  const FOCUS_LABELS = { '[S]': 'Sensitivity', '[R]': 'Responsiveness', '[S+R]': 'Sensitivity + Responsiveness' };

  // One definition per dimension, shared by the scorecard tile and the ratings row.
  const DEFINITIONS = {
    sensitivity: 'How well does the project design fit its FCV context, avoiding harm and accounting for conflict and fragility dynamics?',
    responsiveness: 'Does the project actively contribute to addressing FCV drivers? Not expected for every project.',
    climateSensitivity: 'How well does the design recognize and manage interacting climate and FCV risks, and avoid doing harm?',
    climateResponsiveness: 'Does the project use relevant opportunities to generate wider peace and social dividends? Not expected for every project.',
  };

  const CLOSING_LINE = 'This automated screening supports task-team judgment. It is not a compliance, eligibility, adequacy or clearance decision.';

  // Self-contained handlers (no model text) so they also work in the Share .html export.
  const COPY_DRAFT_HANDLER = "navigator.clipboard&&navigator.clipboard.writeText(this.closest('.fr-draft').querySelector('.fr-draft-text').innerText);this.textContent='Copied'";
  const EXPAND_ALL_HANDLER = "var d=Array.prototype.slice.call(this.closest('.fr-section').querySelectorAll('details.fr-pc')),o=d.some(function(x){return !x.open});d.forEach(function(x){x.open=o});this.textContent=o?'Collapse all':'Expand all'";
  const CHEVRON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" focusable="false"><polyline points="6 9 12 15 18 9"/></svg>';

  function stripBold(text) {
    return String(text || '').replace(/\*\*/g, '').trim();
  }

  function splitParagraphs(text) {
    return String(text || '').split(/\n\s*\n+/).map(p => p.trim()).filter(Boolean);
  }

  function parseStage3Sections(markdown) {
    let text = String(markdown || '').replace(/\r\n?/g, '\n');
    text = text.replace(/^\s*---\s*\n[\s\S]*?\n---[ \t]*(?:\n|$)/, '');
    text = text.replace(/%{2,3}[A-Z][A-Z0-9_]*(?::[^%\n]*)?%{2,3}/g, '');
    text = text.replace(/^\s*(?:-{3,}|\*{3,}|_{3,})\s*$/gm, '');
    text = text.replace(/^#\s+.*$/m, '');
    const sections = { snapshot: '', leadRest: '', context: '', strengths: '', gaps: '', risk: '', other: [], found: false };
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
    const keyOf = block => block.heading.replace(/[*_:]/g, '').trim().toLowerCase();
    const bodyOf = block => block.lines.join('\n').trim();
    const isTop = block => !block.heading || block.level === 2;
    const leadBlock = blocks.find(b => isTop(b) && /executive summary/.test(keyOf(b)) && bodyOf(b))
      || blocks.find(b => isTop(b) && bodyOf(b));
    let watchLevel = 0;
    blocks.forEach(block => {
      const body = bodyOf(block);
      const key = keyOf(block);
      if (watchLevel) {
        if (block.level > watchLevel) return;
        watchLevel = 0;
      }
      if (isTop(block)) {
        if (body && block !== leadBlock) sections.other.push({ heading: block.level === 2 ? block.heading : '', body });
        return;
      }
      if (/^opening assessment/.test(key)) sections.snapshot = body;
      else if (/^operational context/.test(key)) sections.context = body;
      else if (/^strengths?$/.test(key)) sections.strengths = body;
      else if (/^(potential |key )?gaps$/.test(key)) sections.gaps = body;
      else if (/^fcv risk exposure/.test(key)) sections.risk = body;
      else if (/watch list/.test(key)) watchLevel = block.level;
      else if (body) sections.other.push({ heading: block.heading, body });
    });
    const lead = leadBlock ? bodyOf(leadBlock) : '';
    const leadHeading = leadBlock && leadBlock.level === 2 && !/executive summary/.test(keyOf(leadBlock)) ? leadBlock.heading : '';
    // Untitled Executive Summary lead text stays with the snapshot; a titled lead block keeps its heading.
    const keepLead = body => {
      if (leadHeading) sections.other.unshift({ heading: leadHeading, body });
      else sections.leadRest = body;
    };
    if (!sections.snapshot && lead) {
      const paragraphs = splitParagraphs(lead);
      const first = paragraphs.shift() || '';
      // A bold opening span is the verdict; the rest of that paragraph is supporting text.
      const boldLead = first.match(/^\*\*([^*]+?)\*\*\s*([\s\S]*\S)\s*$/);
      if (boldLead) {
        sections.snapshot = boldLead[1];
        paragraphs.unshift(boldLead[2]);
      } else {
        sections.snapshot = first;
      }
      if (paragraphs.length) keepLead(paragraphs.join('\n\n'));
    } else if (lead) {
      keepLead(lead);
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
        const end = Math.max(1, sentenceEnd(rest));
        out.push(rest.slice(0, end).trim());
        rest = rest.slice(end).trim();
      }
      return { head: out.join(' '), rest };
    }

    function prose(body) {
      return splitParagraphs(body).map(p =>
        (/^\s*(?:[-*+]|\d+[.)])\s/m.test(p) || /\*\*|^#|\|/.test(p))
          ? `<div class="fr-md">${md(p)}</div>`
          : `<p dir="auto" class="fr-p">${boldFirst(p)}</p>`).join('');
    }

    function paragraphs(list) {
      return (list || []).map(t => String(t || '').trim()).filter(Boolean)
        .map(t => `<p dir="auto" class="fr-p">${boldFirst(t)}</p>`).join('');
    }

    // Numbered section headers; the recorded list feeds the section jump nav.
    function numbering() {
      let n = 0;
      const list = [];
      const h = title => {
        n += 1;
        const num = String(n).padStart(2, '0');
        list.push({ id: `fr-s${num}`, title });
        return `<header class="fr-h1" id="fr-s${num}"><span class="fr-h1-num">${num}</span><h2 class="fr-h1-txt">${esc(title)}</h2></header>`;
      };
      h.list = list;
      return h;
    }

    function toc(list) {
      if (!list || list.length < 2) return '';
      return `<nav class="fr-toc" aria-label="Sections" data-copy-skip>${list.map(s => `<a href="#${s.id}">${esc(s.title)}</a>`).join('')}</nav>`;
    }

    function sub(label) {
      return `<h3 class="fr-h2c">${esc(label)}</h3>`;
    }

    function intro(text) {
      return `<p class="fr-intro">${esc(text)}</p>`;
    }

    function advisory(text) {
      return text ? `<p class="fr-advisory">${esc(text)}</p>` : '';
    }

    function infoBox(label, innerHtml) {
      return `<div class="fr-info">${label ? `<div class="fr-info-lbl">${esc(label)}</div>` : ''}<div class="fr-info-body">${innerHtml}</div></div>`;
    }

    function section(cls, innerHtml) {
      return `<section class="fr-section ${cls}">${innerHtml}</section>`;
    }

    function closing() {
      return `<p class="fr-note fr-closing">${esc(CLOSING_LINE)}</p>`;
    }

    function meter(steps, level) {
      if (!level) return '';
      let segments = '';
      for (let i = 1; i <= steps; i++) segments += `<span class="fr-ms${i <= level ? ' fr-c' + i : ''}"></span>`;
      return `<div class="fr-meter" role="img" aria-label="${level} of ${steps}" data-copy-skip>${segments}</div>`;
    }

    function scorecard(tiles, count) {
      const tileHtml = tiles.map(t => `<div class="fr-sc-tile" data-fr-rating="${esc(t.key)}"><div class="fr-sc-label">${esc(t.label)}</div><div class="fr-sc-value">${esc(t.value || 'Not available')}</div>${meter(t.steps, t.level)}${t.level ? `<div class="fr-sc-scale" data-copy-skip><span>${esc(t.lo)}</span><span>${esc(t.hi)}</span></div>` : ''}<div class="fr-sc-def">${esc(t.def)}</div></div>`).join('');
      const pills = (count.pills || []).map(p => `<span class="fr-pill ${p.cls}">${esc(p.text)}</span>`).join('');
      return `<p class="fr-sc-lead">${esc(SCORECARD_LEAD)}</p><section class="fr-scorecard" aria-label="Assessment ratings">${tileHtml}<div class="fr-sc-count"><div class="fr-sc-count-lbl">${esc(count.label)}</div><div class="fr-sc-count-num">${Number(count.number) || 0}</div>${pills ? `<div class="fr-sc-pills">${pills}</div>` : ''}${count.def ? `<div class="fr-sc-count-def">${esc(count.def)}</div>` : ''}</div></section>`;
    }

    function ratingRows(rows) {
      return `<div class="fr-ratings">${rows.map(r => `<div class="fr-rating-row"><div class="fr-rating-meta"><div class="fr-rating-dim">${esc(r.dim)}</div><span class="fr-rating-val ${r.cls}">${esc(r.value || 'Not available')}</span><div class="fr-rating-def">${esc(r.def)}</div></div><div class="fr-rating-why">${r.whyHtml || '<p class="fr-p">No rationale was returned for this rating.</p>'}</div></div>`).join('')}</div>`;
    }

    function priorityCard(p) {
      const zones = (p.zones || []).filter(z => z.html).map(z => `<section class="fr-zone"><h4 class="fr-lbl">${esc(z.label)}</h4>${z.html}</section>`).join('');
      const drafts = (p.drafts || []).filter(d => d.text).map(d => `<section class="fr-draft"><div class="fr-draft-hd"><div class="fr-draft-lbl">${esc(d.label)}</div><button type="button" class="fr-copy" data-copy-skip onclick="${COPY_DRAFT_HANDLER}">Copy</button></div>${d.forText ? `<div class="fr-draft-for">For: ${esc(d.forText)}</div>` : ''}<p dir="auto" class="fr-draft-text">${esc(d.text)}</p></section>`).join('');
      const cycle = p.cycle && p.cycle.text ? `<p class="fr-cycle"><strong>${esc(p.cycle.label || 'When to address')}:</strong> ${esc(p.cycle.text)}</p>` : '';
      const meta = p.supHtml ? `<span class="fr-pc-meta">${p.supHtml}</span>` : '';
      return `<details class="fr-pc" id="${p.id}"${p.open ? ' open' : ''}><summary class="fr-pc-hdr"><span class="fr-pc-rank">${p.rank}</span><span class="fr-pc-title">${meta}<span dir="auto" class="fr-pc-title-txt">${esc(p.title)}</span></span><span class="fr-pc-chev" aria-hidden="true">${CHEVRON_SVG}</span></summary><div class="fr-pc-body">${zones}${drafts}${cycle}${p.extraHtml || ''}</div></details>`;
    }

    function cards(cardsHtml, count) {
      const tools = count > 1 ? `<div class="fr-cards-tools" data-copy-skip><button type="button" class="fr-expand" data-copy-skip onclick="${EXPAND_ALL_HANDLER}">Expand all</button></div>` : '';
      return `${tools}<div class="fr-cards">${cardsHtml}</div>`;
    }

    function disclosure(summary, bodyHtml) {
      return `<details class="fr-disc"><summary class="fr-disc-sum">${esc(summary)}</summary><div class="fr-disc-body">${bodyHtml}</div></details>`;
    }

    function checkItems(items) {
      return items.map((it, i) => `<div class="fr-check"><span class="fr-check-num">${String(i + 1).padStart(2, '0')}</span><div><h4 class="fr-check-title">${esc(it.title)}</h4>${it.why ? `<p dir="auto" class="fr-p">${esc(it.why)}</p>` : ''}${it.how ? `<p class="fr-check-how"><strong>How to address:</strong> ${esc(it.how)}</p>` : ''}</div></div>`).join('');
    }

    function pill(text, cls, title) {
      const key = String(text || '').toLowerCase();
      return text ? `<span class="fr-pill ${cls ? esc(cls) : 'fr-pill-' + esc(key)}"${title ? ` title="${esc(title)}"` : ''}>${esc(text)}</span>` : '';
    }

    // Normal-route priority level pill: level word plus "priority", level colour class.
    function levelPill(level) {
      const key = String(level || '').trim().toLowerCase();
      return key ? pill(`${String(level).trim()} priority`, 'fr-pill-' + key) : '';
    }

    const kit = { esc, md, boldFirst, timingLabel, takeSentences, prose, paragraphs, numbering, toc, sub, intro, advisory, infoBox, section, closing, meter, scorecard, ratingRows, priorityCard, cards, disclosure, checkItems, pill, levelPill };
    return Object.assign(kit, {
      renderNormal: data => renderNormal(kit, data),
      renderClimate: (reader, opts) => renderClimate(kit, reader, opts),
    });
  }

  const SCORECARD_LEAD = 'The ratings below are a high-level AI assessment based on insights from the project package. They do not reflect a formal WBG or FCV Group designation. Read them as a general guide, alongside the more detailed overview and assessment that follows.';

  // Zero gets no line: an empty list can mean a withheld or incomplete stage, not "none needed".
  function countDef(n, one, many) {
    if (!n) return '';
    return n === 1 ? `1 ${one} is identified by the FCV Screener.` : `${n} ${many} are identified by the FCV Screener.`;
  }

  function priorityTitle(title) {
    return String(title || 'Priority action').replace(/^\s*Priority\s+\d+\s*(?:[·•:.\-–]\s*)?/i, '').trim() || 'Priority action';
  }

  function countPills(items, keyOf, labels) {
    const counts = {};
    items.forEach(item => { const k = keyOf(item); if (k) counts[k] = (counts[k] || 0) + 1; });
    return labels.filter(l => counts[l.key]).map(l => ({ text: `${counts[l.key]} ${l.text}`, cls: l.cls }));
  }

  function renderNormal(k, d) {
    const h = k.numbering();
    const s = parseStage3Sections(d.stage3Markdown);
    const priorities = Array.isArray(d.priorities) ? d.priorities.slice(0, 5) : [];
    const levelOf = v => FCV_SCALE.findIndex(x => x.toLowerCase() === String(v || '').toLowerCase()) + 1;
    let head = d.noticesHtml || '';
    head += k.scorecard([
      { key: 'sensitivity', label: 'FCV Sensitivity', value: d.fcvRating, steps: 6, level: levelOf(d.fcvRating), lo: FCV_SCALE[0], hi: FCV_SCALE[5], def: DEFINITIONS.sensitivity },
      { key: 'responsiveness', label: 'FCV Responsiveness', value: d.fcvResponsivenessRating, steps: 6, level: levelOf(d.fcvResponsivenessRating), lo: FCV_SCALE[0], hi: FCV_SCALE[5], def: DEFINITIONS.responsiveness },
    ], { label: 'Priority actions', number: priorities.length, def: countDef(priorities.length, 'priority action', 'priority actions'), pills: countPills(priorities, p => String(p.risk_level || '').toLowerCase(), [
      { key: 'high', text: 'high priority', cls: 'fr-pill-high' }, { key: 'medium', text: 'medium priority', cls: 'fr-pill-medium' }, { key: 'low', text: 'low priority', cls: 'fr-pill-low' }]) });

    let html = '';
    if (s.found) {
      html += k.section('fr-exec', h('Executive Summary')
        + (s.snapshot ? k.infoBox('Assessment snapshot', `<strong>${k.esc(s.snapshot)}</strong>`) : '')
        + (s.leadRest ? k.prose(s.leadRest) : '')
        + (s.context ? k.sub('Operational context') + k.prose(s.context) : '')
        + (s.strengths ? k.sub('Strengths') + k.prose(s.strengths) : '')
        + (s.gaps ? k.sub('Potential gaps') + k.prose(s.gaps) : '')
        + s.other.map(o => (o.heading ? k.sub(o.heading) : '') + k.prose(o.body)).join(''));
    } else if (String(d.stage3Markdown || '').trim()) {
      html += k.section('fr-exec', h('Executive Summary') + `<div class="fr-md">${k.md(d.stage3Markdown)}</div>`);
    }

    const risk = d.riskExposure || {};
    if (risk.risks_to || risk.risks_from) {
      html += k.section('fr-risk', h('FCV Risk Exposure') + `<div class="fr-pair">`
        + (risk.risks_to ? `<div class="fr-col">${k.sub('Risks to the project')}${k.prose(risk.risks_to)}</div>` : '')
        + (risk.risks_from ? `<div class="fr-col">${k.sub('Risks from the project')}${k.prose(risk.risks_from)}</div>` : '')
        + `</div>`);
    } else if (s.found && s.risk) {
      html += k.section('fr-risk', h('FCV Risk Exposure') + k.prose(s.risk));
    }

    if (d.fcvRating || d.fcvResponsivenessRating || d.sensitivitySummary || d.responsivenessSummary) {
      html += k.section('fr-ratings-sec', h('FCV Sensitivity and Responsiveness')
        + k.intro('The ratings below explain the judgments behind the scorecard above.')
        + k.ratingRows([
          { dim: 'FCV Sensitivity', value: d.fcvRating, cls: 'fr-rv-sens', def: DEFINITIONS.sensitivity, whyHtml: k.prose(d.sensitivitySummary) },
          { dim: 'FCV Responsiveness', value: d.fcvResponsivenessRating, cls: 'fr-rv-resp', def: DEFINITIONS.responsiveness, whyHtml: k.prose(d.responsivenessSummary) },
        ]));
    }

    if (priorities.length) {
      const n = priorities.length;
      const intro = k.infoBox('', `<strong>Based on a three-stage assessment of the project documents, ${n} priority ${n === 1 ? 'action has' : 'actions have'} been identified</strong> to strengthen FCV sensitivity and responsiveness in the design and delivery of this project.` + k.advisory(d.advisoryText));

      const cards = priorities.map((p, i) => {
        const actions = Array.isArray(p.actions) ? p.actions : [];
        const actionsHtml = actions.length ? `<ol class="fr-actions">${actions.map(a => `<li>${a.document_element ? `<strong>${k.esc(a.document_element)}:</strong> ` : ''}${k.esc(a.guidance || '')}</li>`).join('')}</ol>` : '';
        const cycleText = p.implementation_note || (p.project_cycle && p.project_cycle.primary_text) || '';
        const cycleLabel = p.implementation_note ? 'When to address' : ((p.project_cycle && p.project_cycle.primary_label) || 'When to address');
        const sup = [k.levelPill(p.risk_level), k.esc(FOCUS_LABELS[p.tag] || p.tag || ''), k.esc(p.fcv_dimension || ''), k.esc(k.timingLabel(p.action_timing))].filter(Boolean).join(' &middot; ');
        return k.priorityCard({
          id: `fr-priority-${i + 1}`, rank: i + 1, open: i === 0, supHtml: sup, title: priorityTitle(p.title),
          zones: [{ label: 'The gap', html: k.prose(p.the_gap) }, { label: 'Why it matters', html: k.prose(p.why_it_matters) }, { label: 'Suggested actions', html: actionsHtml }],
          drafts: actions.map(a => ({ label: 'Suggested Text', forText: a.document_element || '', text: a.suggested_language || '' })),
          cycle: { label: cycleLabel, text: cycleText },
          extraHtml: typeof d.priorityExtras === 'function' ? d.priorityExtras(p, i) : '',
        });
      }).join('');
      html += k.section('fr-cards-sec', h('Priority Actions for the Task Team') + intro + k.cards(cards, n));
    }

    if (d.watchHtml) {
      html += k.section('fr-watch', h('Watch List for Supervision')
        + k.disclosure('Risks to monitor during implementation', '<p class="fr-intro">These are FCV risks or dynamics the team cannot act on now but should monitor during implementation. They do not affect the FCV ratings above.</p>' + d.watchHtml));
    }
    return `<article class="fr-readout fr-route-fcv">${head}${k.toc(h.list)}${html}${d.tailHtml || ''}${k.closing()}</article>`;
  }
  const THEME_QUESTIONS = {
    'Climate risks, design and delivery': 'Does the project address interacting climate and FCV risks in design and delivery?',
    'Wider peace and social dividends': 'Could the project generate wider peace and social benefits, and how could these be strengthened?',
    'Access, inclusion and potential harm': 'Will people benefit fairly, and could delivery create exclusion or harm?',
  };

  function climateLabel(value) {
    if (value === 'not_expected') return 'Not expected';
    return String(value || 'unclear').replace(/_/g, ' ').replace(/^./, c => c.toUpperCase());
  }

  function climatePillClass(value) {
    if (['strong', 'very_strong', 'high'].includes(value)) return 'fr-rv-strong';
    if (value === 'moderate') return 'fr-rv-moderate';
    if (['limited', 'very_limited'].includes(value)) return 'fr-rv-limited';
    return 'fr-rv-unclear';
  }

  const CONFIDENCE_CLASS = { high: 'fr-pill-conf-high', medium: 'fr-pill-conf-medium', low: 'fr-pill-conf-low' };
  const CONFIDENCE_TITLE = 'How well the documents support this priority';

  function confidencePill(k, confidence, suffix) {
    const key = String(confidence || '').toLowerCase();
    return key ? k.pill(climateLabel(key) + (suffix || ''), 'fr-pill-conf ' + (CONFIDENCE_CLASS[key] || 'fr-pill-conf-medium'), CONFIDENCE_TITLE) : '';
  }

  // Document keys arrive in lower case ("pad - project description"); give them reader casing.
  const DOC_ACRONYMS = ['pad', 'pid', 'pcn', 'pom', 'esmf', 'escp', 'esrs', 'sep', 'rpf', 'rap', 'lmp', 'grm', 'pdo', 'ois', 'dpf', 'mpa', 'cerc', 'piu', 'pmu', 'esf', 'td', 'ir', 'pp', 'ppsd', 'm&e', 'gbv', 'sea', 'sh', 'ipf', 'fcv', 'cpf', 'rra', 'aar', 'isr', 'icr', 'ppa', 'ida', 'ibrd'];
  const SMALL_WORDS = ['and', 'or', 'of', 'the', 'for', 'in', 'to', 'a', 'an', 'on', 'at', 'by', 'with'];

  function titleKey(text) {
    const value = String(text || '').replace(/_/g, ' ').trim();
    if (!value || /[A-Z]/.test(value)) return value;
    let first = true;
    return value.replace(/[a-z0-9&]+/g, word => {
      const out = word === 'pforr' ? 'PforR'
        : DOC_ACRONYMS.includes(word) ? word.toUpperCase()
          : (!first && SMALL_WORDS.includes(word)) ? word
            : word.charAt(0).toUpperCase() + word.slice(1);
      first = false;
      return out;
    });
  }

  function safeUrl(url) {
    return /^https?:\/\//i.test(String(url || '')) ? String(url) : '';
  }

  function renderClimate(k, reader, opts) {
    const r = reader && typeof reader === 'object' ? reader : {};
    const o = opts || {};
    const h = k.numbering();
    const judgments = Array.isArray(r.judgments) ? r.judgments : [];
    const judgment = key => judgments.find(j => j && j.dimension === key) || {};
    const csr = r.climate_sensitivity_rating || {};
    const sens = Object.assign({}, judgment('sensitivity'));
    if (!sens.value && csr.value) sens.value = csr.value;
    const resp = judgment('responsiveness');
    const level = v => CLIMATE_SCALE.indexOf(String(v || '')) + 1;
    const priorities = (Array.isArray(r.priorities) ? r.priorities : []).slice()
      .sort((a, b) => (Number(a.rank) || 999) - (Number(b.rank) || 999)).slice(0, 5);

    let head = o.noticesHtml || '';
    head += k.scorecard([
      { key: 'climate-sensitivity', label: 'Climate-FCV sensitivity', value: climateLabel(sens.value), steps: 5, level: level(sens.value), lo: 'Very limited', hi: 'Very strong', def: DEFINITIONS.climateSensitivity },
      { key: 'climate-responsiveness', label: 'Climate-FCV responsiveness', value: climateLabel(resp.value), steps: 5, level: level(resp.value), lo: 'Very limited', hi: 'Very strong', def: DEFINITIONS.climateResponsiveness },
    ], { label: 'Priority actions', number: priorities.length, def: countDef(priorities.length, 'priority action', 'priority actions'), pills: countPills(priorities, p => String(p.confidence || '').toLowerCase(), [
      { key: 'high', text: 'High confidence', cls: 'fr-pill-conf fr-pill-conf-high' }, { key: 'medium', text: 'Medium confidence', cls: 'fr-pill-conf fr-pill-conf-medium' }, { key: 'low', text: 'Low confidence', cls: 'fr-pill-conf fr-pill-conf-low' }]) });

    const overview = (Array.isArray(r.summary_overview) ? r.summary_overview : [r.summary_overview]).map(t => String(t || '').trim()).filter(Boolean);
    let snapshot = '';
    let contextHtml = '';
    if (r.summary_overview_status === 'generated' && overview.length) {
      snapshot = overview[0];
      contextHtml = k.paragraphs(overview.slice(1, 3));
    } else if (r.reader_contract === 'final-reader-v1') {
      // Fallback text explains why no summary is shown; keep it muted rather than as findings.
      contextHtml = overview.map(t => k.intro(t)).join('');
    } else {
      const paras = splitParagraphs(r.executive_readout);
      const split = k.takeSentences(paras[0] || '', 2);
      snapshot = split.head;
      contextHtml = k.paragraphs([split.rest, paras[1]].filter(Boolean));
    }
    const working = (Array.isArray(r.existing_responses) ? r.existing_responses : []).map(x => x && x.description).filter(Boolean).slice(0, 4);
    const gaps = (Array.isArray(r.summary_gaps) ? r.summary_gaps : []).map(x => x && x.text).filter(Boolean).slice(0, 5);
    let html = k.section('fr-exec', h('Overview')
      + (snapshot ? k.infoBox('Assessment snapshot', `<strong>${k.esc(snapshot)}</strong>`) : '')
      + contextHtml
      + (working.length ? k.sub('What is already working') + k.paragraphs(working) : '')
      + (gaps.length ? k.sub('Key gaps at this stage') + k.paragraphs(gaps) : ''));

    const rankIndex = new Map();
    priorities.forEach((p, i) => { const n = Number(p.rank); if (Number.isInteger(n) && !rankIndex.has(n)) rankIndex.set(n, i + 1); });
    const themes = (Array.isArray(r.assessment_themes) ? r.assessment_themes : []).map(t => {
      const question = t.question || THEME_QUESTIONS[t.title] || t.title || '';
      const findings = Array.isArray(t.findings) ? t.findings : [];
      const paras = Array.isArray(t.paragraphs) && t.paragraphs.length ? t.paragraphs : [findings.map(f => f.text || '').join(' ')];
      const ranks = Array.isArray(t.priority_ranks) ? t.priority_ranks : [];
      const links = ranks.map(n => rankIndex.get(n)).filter(Boolean).map(n => `<a href="#fr-priority-${n}" onclick="var d=document.getElementById('fr-priority-${n}');if(d)d.open=true;">Priority ${n}</a>`).join(' &middot; ');
      return `<div class="fr-theme"><h3 class="fr-theme-q">${k.esc(question)}</h3>${k.paragraphs(paras)}${links ? `<p class="fr-theme-links">Related priority actions: ${links}</p>` : ''}</div>`;
    }).join('');
    if (themes) html += k.section('fr-themes', h('Assessment Findings') + k.intro('Three cross-cutting questions about how the project interacts with climate and FCV dynamics. Each links to the priority actions below.') + `<div class="fr-themes-stack">${themes}</div>`);

    const ops = judgment('operationalization');
    const rel = judgment('relevance');
    const notes = [rel.value ? `<p><strong>Climate relevance: ${k.esc(climateLabel(rel.value))}.</strong> ${k.esc(rel.rationale || '')}</p>` : '',
      ops.value ? `<p><strong>Operationalization: ${k.esc(climateLabel(ops.value))}.</strong> ${k.esc(ops.rationale || '')}</p>` : ''].join('');
    html += k.section('fr-ratings-sec', h('Climate-FCV Sensitivity and Responsiveness')
      + k.intro('The ratings below explain the judgments behind the scorecard above.')
      + k.ratingRows([
        { dim: 'Climate-FCV sensitivity', value: climateLabel(sens.value), cls: climatePillClass(sens.value), def: DEFINITIONS.climateSensitivity, whyHtml: k.paragraphs([sens.rationale || sens.description]) },
        { dim: 'Climate-FCV responsiveness', value: climateLabel(resp.value), cls: climatePillClass(resp.value), def: DEFINITIONS.climateResponsiveness, whyHtml: k.paragraphs([resp.rationale || resp.description]) },
      ]) + (notes ? `<div class="fr-ops-note"><div class="fr-ops-lbl">Supporting judgments (not shown on the scorecard)</div>${notes}</div>` : ''));

    const statement = (r.priority_summary && r.priority_summary.statement) || '';
    if (priorities.length) {
      const n = priorities.length;
      const lead = statement ? k.boldFirst(statement) : `<strong>${n} operational ${n === 1 ? 'priority is' : 'priorities are'} identified for the task team.</strong>`;
      const intro = k.infoBox('', lead + k.advisory(o.advisoryText));
      const cards = priorities.map((p, i) => {
        const rank = i + 1;
        const paras = splitParagraphs(p.narrative);
        const why = paras.length ? paras.slice(0, 1) : [p.limitation];
        const act = paras.length > 1 ? paras.slice(1) : [p.minimum_action || p.decision];
        const cur = o.draftingAllowed && p.current_document_drafting ? p.current_document_drafting : null;
        const opd = o.draftingAllowed && p.operational_instrument_drafting ? p.operational_instrument_drafting : null;
        const target = cur ? [titleKey(cur.target_document), titleKey(cur.target_section)].filter(Boolean).join(' - ') : '';
        const lead = String(p.responsible_function || '').trim().replace(/\.+$/, '');
        const cycle = p.project_cycle || {};
        const norm = t => String(t || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
        const visible = paras.map(norm).filter(Boolean);
        const visibleText = visible.join(' ');
        const shown = [];
        const fresh = text => {
          const n = norm(text);
          if (!n || visible.includes(n) || visibleText.includes(n) || shown.includes(n)) return false;
          shown.push(n);
          return true;
        };
        const practical = [p.limitation, p.caution].map(t => String(t || '').trim()).filter(fresh);
        const optionalText = [p.enhanced_action, p.enhanced_activation].map(t => String(t || '').trim()).filter(Boolean).join(' ');
        const optional = optionalText && fresh(optionalText) ? [optionalText] : [];
        return k.priorityCard({
          id: `fr-priority-${rank}`, rank, open: i === 0, title: priorityTitle(p.title),
          supHtml: [confidencePill(k, p.confidence, ' confidence'), lead ? `Lead: ${k.esc(lead)}` : '', k.esc(target)].filter(Boolean).join(' &middot; '),
          zones: [{ label: 'Why this matters', html: k.paragraphs(why) }, { label: 'What the team could do', html: k.paragraphs(act) },
            { label: 'Practical considerations', html: k.paragraphs(practical) },
            { label: 'Optional further work', html: k.paragraphs(optional) }],
          drafts: [cur && { label: 'Suggested Text', forText: target, text: cur.text },
            opd && { label: 'Suggested Text for an operational instrument', forText: [titleKey(opd.target_document), titleKey(opd.target_section)].filter(Boolean).join(' - '), text: opd.text }].filter(Boolean),
          cycle: { label: cycle.primary_label || 'When to address', text: cycle.primary_text || '' },
          extraHtml: typeof o.priorityExtras === 'function' ? o.priorityExtras(p, i) : '',
        });
      }).join('');
      html += k.section('fr-cards-sec', h('Priority Actions for the Task Team') + intro + k.cards(cards, n));
    } else {
      html += k.section('fr-cards-sec', h('Priority Actions for the Task Team') + `<p class="fr-p">${k.esc(r.recommendation_message || 'No operational priorities were identified in this assessment. Review the assessment findings and points to check below.')}</p>`);
    }

    const checks = [].concat(
      (Array.isArray(r.review_readiness_flags) ? r.review_readiness_flags : []).map(f => ({ title: f.flag || 'Point to verify', why: f.why_it_matters, how: f.suggested_verification })),
      (Array.isArray(r.minor_climate_points) ? r.minor_climate_points : []).map(m => ({ title: m.point || 'Point to consider', why: m.why, how: m.how_to_check })));
    if (checks.length) html += k.section('fr-checks', h('Smaller Points to Check During Preparation') + k.disclosure('Smaller checks for the project team to confirm', '<p class="fr-intro">These sit alongside the main priorities above. None is a reason to stop the project.</p>' + k.checkItems(checks)));

    const guides = (Array.isArray(r.guidance_items) ? r.guidance_items : []).filter(g => g && g.title).map(g => {
      const url = safeUrl(g.url);
      const title = url ? `<a class="fr-guide-title" href="${k.esc(url)}" target="_blank" rel="noopener noreferrer">${k.esc(g.title)}</a>` : `<span class="fr-guide-title">${k.esc(g.title)}</span>`;
      return `<div class="fr-guide">${title}${g.use ? `<p dir="auto" class="fr-p">${k.esc(g.use)}</p>` : ''}</div>`;
    }).join('');
    if (guides) html += k.section('fr-guidance', h('Relevant WBG Guidance') + k.disclosure('Selected WBG resources for the team', guides));

    const trail = r.evidence_trail || {};
    const limits = Array.isArray(trail.limitations) ? trail.limitations.filter(Boolean).join(' ') : String(trail.limitations || '').trim();
    const limitsText = limits || 'This automated screening is advisory and is limited by the coverage and detail of the uploaded documents. The team should confirm material findings through project and country expertise.';
    html += k.section('fr-limits-sec', h('Limitations') + `<div class="fr-limits">${k.paragraphs([limitsText, r.advisory_notice])}</div>`);
    const saysAlready = /does not constitute/i.test(`${limitsText} ${r.advisory_notice || ''}`);
    return `<article class="fr-readout fr-route-climate">${head}${k.toc(h.list)}${html}${saysAlready ? '' : k.closing()}</article>`;
  }

  const api = { FCV_SCALE, CLIMATE_SCALE, FOCUS_LABELS, DEFINITIONS, CLOSING_LINE, parseStage3Sections, create };
  root.FcvReadout = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
