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
    let html = d.noticesHtml || '';
    html += k.scorecard([
      { key: 'sensitivity', label: 'FCV Sensitivity', value: d.fcvRating, steps: 6, level: levelOf(d.fcvRating), lo: FCV_SCALE[0], hi: FCV_SCALE[5], def: 'Does the design fit its FCV context and avoid doing harm?' },
      { key: 'responsiveness', label: 'FCV Responsiveness', value: d.fcvResponsivenessRating, steps: 6, level: levelOf(d.fcvResponsivenessRating), lo: FCV_SCALE[0], hi: FCV_SCALE[5], def: 'Does the project actively address FCV drivers? Not expected for every project.' },
    ], { label: 'Priority actions', number: priorities.length, pills: countPills(priorities, p => p.risk_level, [
      { key: 'High', text: 'High', cls: 'fr-pill-high' }, { key: 'Medium', text: 'Medium', cls: 'fr-pill-medium' }, { key: 'Low', text: 'Low', cls: 'fr-pill-low' }]) });

    if (s.found) {
      html += k.section('fr-exec', h('Executive Summary')
        + (s.snapshot ? k.infoBox('Assessment snapshot', `<strong>${k.esc(s.snapshot)}</strong>`) : '')
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
      html += k.section('fr-ratings-sec', h('FCV Sensitivity & Responsiveness')
        + k.intro('The ratings below explain the judgments behind the scorecard above.')
        + k.ratingRows([
          { dim: 'FCV Sensitivity', value: d.fcvRating, cls: 'fr-rv-sens', def: 'How well does the project design fit its FCV context, avoiding harm and accounting for conflict and fragility dynamics?', whyHtml: k.prose(d.sensitivitySummary) },
          { dim: 'FCV Responsiveness', value: d.fcvResponsivenessRating, cls: 'fr-rv-resp', def: 'Does the project actively contribute to addressing FCV drivers? Not expected for every project.', whyHtml: k.prose(d.responsivenessSummary) },
        ]) + '<p class="fr-note">Advisory judgments, not official WBG ratings.</p>');
    }

    if (priorities.length) {
      const n = priorities.length;
      const rows = priorities.map((p, i) => ({
        id: `fr-priority-${i + 1}`, rank: i + 1, title: priorityTitle(p.title),
        cells: [k.pill(p.risk_level), k.esc(FOCUS_LABELS[p.tag] || p.tag || ''), k.esc(k.timingLabel(p.action_timing))],
      }));
      html += k.section('fr-ptable-sec', h('Priority Actions for the Task Team')
        + k.infoBox('', `<strong>Based on a three-stage assessment of the project documents, ${n} priority ${n === 1 ? 'action has' : 'actions have'} been identified</strong> to strengthen FCV sensitivity and responsiveness in the design and delivery of this project.`)
        + k.priorityTable(['#', 'Priority action', 'Level', 'FCV focus', 'Timing'], rows));

      const cards = priorities.map((p, i) => {
        const actions = Array.isArray(p.actions) ? p.actions : [];
        const actionsHtml = actions.length ? `<ol class="fr-actions">${actions.map(a => `<li>${a.document_element ? `<strong>${k.esc(a.document_element)}:</strong> ` : ''}${k.esc(a.guidance || '')}</li>`).join('')}</ol>` : '';
        const cycleText = p.implementation_note || (p.project_cycle && p.project_cycle.primary_text) || '';
        const cycleLabel = p.implementation_note ? 'When to address' : ((p.project_cycle && p.project_cycle.primary_label) || 'When to address');
        const sup = [`Priority ${i + 1}`, k.pill(p.risk_level), k.esc(p.fcv_dimension || ''), k.esc(k.timingLabel(p.action_timing))].filter(Boolean).join(' &middot; ');
        return k.priorityCard({
          id: `fr-priority-${i + 1}`, rank: i + 1, open: i === 0, supHtml: sup, title: priorityTitle(p.title),
          zones: [{ label: 'The gap', html: k.prose(p.the_gap) }, { label: 'Why it matters', html: k.prose(p.why_it_matters) }, { label: 'Essential actions', html: actionsHtml }],
          drafts: actions.map(a => ({ label: 'Suggested text', forText: a.document_element || '', text: a.suggested_language || '' })),
          cycle: { label: cycleLabel, text: cycleText },
          extraHtml: typeof d.priorityExtras === 'function' ? d.priorityExtras(p, i) : '',
        });
      }).join('');
      html += k.section('fr-cards-sec', h('Strategic Priorities') + `<div class="fr-cards">${cards}</div>`);
    }

    if (d.watchHtml) {
      html += k.section('fr-watch', h('Watch List for Supervision')
        + k.disclosure('Risks to monitor during implementation', '<p class="fr-intro">These are FCV risks or dynamics the team cannot act on now but should monitor during implementation. They do not affect the FCV ratings above.</p>' + d.watchHtml));
    }
    return `<article class="fr-readout fr-route-fcv">${html}${d.tailHtml || ''}</article>`;
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

    let html = o.noticesHtml || '';
    html += k.scorecard([
      { key: 'climate-sensitivity', label: 'Climate sensitivity', value: climateLabel(sens.value), steps: 5, level: level(sens.value), lo: 'Very limited', hi: 'Very strong', def: 'How well does the design address interacting climate and FCV risks?' },
      { key: 'climate-responsiveness', label: 'Climate responsiveness', value: climateLabel(resp.value), steps: 5, level: level(resp.value), lo: 'Very limited', hi: 'Very strong', def: 'Does the project generate wider climate, peace and social dividends?' },
    ], { label: 'Priorities', number: priorities.length, pills: countPills(priorities, p => String(p.confidence || '').toLowerCase(), [
      { key: 'high', text: 'High confidence', cls: 'fr-pill-conf-high' }, { key: 'medium', text: 'Medium confidence', cls: 'fr-pill-medium' }, { key: 'low', text: 'Low confidence', cls: 'fr-pill-conf-low' }]) });

    const overview = (Array.isArray(r.summary_overview) ? r.summary_overview : [r.summary_overview]).map(t => String(t || '').trim()).filter(Boolean);
    let snapshot = '';
    let context = [];
    if (r.summary_overview_status === 'generated' && overview.length) {
      snapshot = overview[0];
      context = overview.slice(1, 3);
    } else {
      const paras = firstParagraph(r.executive_readout);
      const split = k.takeSentences(paras[0] || '', 2);
      snapshot = split.head;
      context = [split.rest, paras[1]].filter(Boolean);
    }
    const working = (Array.isArray(r.existing_responses) ? r.existing_responses : []).map(x => x && x.description).filter(Boolean).slice(0, 4);
    const gaps = (Array.isArray(r.summary_gaps) ? r.summary_gaps : []).map(x => x && x.text).filter(Boolean).slice(0, 5);
    html += k.section('fr-exec', h('Overview')
      + (r.reader_review_notice ? `<p class="fr-notice">${k.esc(r.reader_review_notice)}</p>` : '')
      + (snapshot ? k.infoBox('Assessment snapshot', `<strong>${k.esc(snapshot)}</strong>`) : '')
      + k.paragraphs(context)
      + (working.length ? k.sub('What is already working') + k.paragraphs(working) : '')
      + (gaps.length ? k.sub('Key gaps at this stage') + k.paragraphs(gaps) : ''));

    const themes = (Array.isArray(r.assessment_themes) ? r.assessment_themes : []).map(t => {
      const question = t.question || THEME_QUESTIONS[t.title] || t.title || '';
      const findings = Array.isArray(t.findings) ? t.findings : [];
      const paras = Array.isArray(t.paragraphs) && t.paragraphs.length ? t.paragraphs : [findings.map(f => f.text || '').join(' ')];
      const ranks = Array.isArray(t.priority_ranks) ? t.priority_ranks : [];
      const links = ranks.filter(Number.isInteger).map(n => `<a href="#fr-priority-${n}" onclick="var d=document.getElementById('fr-priority-${n}');if(d)d.open=true;">Priority ${n}</a>`).join(' &middot; ');
      return `<div class="fr-theme"><h3 class="fr-theme-q">${k.esc(question)}</h3>${k.paragraphs(paras)}${links ? `<p class="fr-theme-links">Related operational priorities: ${links}</p>` : ''}</div>`;
    }).join('');
    if (themes) html += k.section('fr-themes', h('Assessment Findings') + k.intro('Three cross-cutting questions about how the project interacts with climate and FCV dynamics. Each links to the operational priorities below.') + `<div class="fr-themes-stack">${themes}</div>`);

    const ops = judgment('operationalization');
    const rel = judgment('relevance');
    const notes = [rel.value ? `<p><strong>Climate relevance: ${k.esc(climateLabel(rel.value))}.</strong> ${k.esc(rel.rationale || '')}</p>` : '',
      ops.value ? `<p><strong>Operationalization: ${k.esc(climateLabel(ops.value))}.</strong> ${k.esc(ops.rationale || '')}</p>` : ''].join('');
    html += k.section('fr-ratings-sec', h('Climate & FCV Sensitivity & Responsiveness')
      + k.intro('The ratings below explain the judgments behind the scorecard above.')
      + k.ratingRows([
        { dim: 'Climate sensitivity', value: climateLabel(sens.value), cls: climatePillClass(sens.value), def: 'How well does the project recognize and address interacting climate and FCV risks?', whyHtml: k.paragraphs([sens.rationale || sens.description]) },
        { dim: 'Climate responsiveness', value: climateLabel(resp.value), cls: climatePillClass(resp.value), def: 'Does the project use relevant opportunities to generate wider peace and social dividends? Not expected for every project.', whyHtml: k.paragraphs([resp.rationale || resp.description]) },
      ]) + (notes ? `<div class="fr-ops-note">${notes}</div>` : '') + '<p class="fr-note">Advisory judgments, not official WBG ratings.</p>');

    const statement = (r.priority_summary && r.priority_summary.statement) || '';
    if (priorities.length) {
      const rows = priorities.map((p, i) => ({
        id: `fr-priority-${Number(p.rank) || i + 1}`, rank: Number(p.rank) || i + 1, title: priorityTitle(p.title),
        cells: [k.pill(climateLabel(p.confidence)), k.esc(p.responsible_function || '')],
      }));
      html += k.section('fr-ptable-sec', h('Ranked Operational Priorities')
        + (statement ? k.infoBox('', k.boldFirst(statement)) : '')
        + k.priorityTable(['#', 'Operational priority', 'Confidence', 'Suggested lead'], rows));
      const cards = priorities.map((p, i) => {
        const rank = Number(p.rank) || i + 1;
        const paras = firstParagraph(p.narrative);
        const why = paras.length ? paras.slice(0, 1) : [p.limitation];
        const act = paras.length > 1 ? paras.slice(1) : [p.minimum_action || p.decision];
        const cur = o.draftingAllowed && p.current_document_drafting ? p.current_document_drafting : null;
        const opd = o.draftingAllowed && p.operational_instrument_drafting ? p.operational_instrument_drafting : null;
        const target = cur ? [cur.target_document, cur.target_section].filter(Boolean).join(' - ') : '';
        const cycle = p.project_cycle || {};
        return k.priorityCard({
          id: `fr-priority-${rank}`, rank, open: i === 0, title: priorityTitle(p.title),
          supHtml: [`Priority ${rank}`, p.confidence ? k.pill(climateLabel(p.confidence) + ' confidence') : '', k.esc(target)].filter(Boolean).join(' &middot; '),
          zones: [{ label: 'Why this matters', html: k.paragraphs(why) }, { label: 'What the team could do', html: k.paragraphs(act) },
            { label: 'Optional further work', html: p.enhanced_action ? k.paragraphs([p.enhanced_action]) : '' }],
          drafts: [cur && { label: 'Suggested drafting', forText: target, text: cur.text },
            opd && { label: 'Suggested drafting for an operational instrument', forText: [opd.target_document, opd.target_section].filter(Boolean).join(' - '), text: opd.text }].filter(Boolean),
          cycle: { label: cycle.primary_label || 'When to address', text: cycle.primary_text || '' },
          extraHtml: typeof o.priorityExtras === 'function' ? o.priorityExtras(p, i) : '',
        });
      }).join('');
      html += k.section('fr-cards-sec', h('Strategic Priorities') + `<div class="fr-cards">${cards}</div>`);
    } else {
      html += k.section('fr-ptable-sec', h('Ranked Operational Priorities') + `<p class="fr-p">${k.esc(r.recommendation_message || 'No operational priorities were identified in this assessment. Review the assessment findings and points to check below.')}</p>`);
    }

    const checks = [].concat(
      (Array.isArray(r.review_readiness_flags) ? r.review_readiness_flags : []).map(f => ({ title: f.flag || 'Point to verify', why: f.why_it_matters, how: f.suggested_verification })),
      (Array.isArray(r.minor_climate_points) ? r.minor_climate_points : []).map(m => ({ title: m.point || 'Point to consider', why: m.why, how: m.how_to_check })));
    if (checks.length) html += k.section('fr-checks', h('Points to Check Before the Applicable Review') + k.disclosure('Smaller checks for the project team to confirm', '<p class="fr-intro">These sit alongside the main priorities above. None is a reason to stop the project.</p>' + k.checkItems(checks)));

    const guides = (Array.isArray(r.guidance_items) ? r.guidance_items : []).filter(g => g && g.title).map(g => {
      const url = safeUrl(g.url);
      const title = url ? `<a class="fr-guide-title" href="${k.esc(url)}" target="_blank" rel="noopener noreferrer">${k.esc(g.title)}</a>` : `<span class="fr-guide-title">${k.esc(g.title)}</span>`;
      return `<div class="fr-guide">${title}${g.use ? `<p class="fr-p">${k.esc(g.use)}</p>` : ''}</div>`;
    }).join('');
    if (guides) html += k.section('fr-guidance', h('Relevant WBG Guidance') + k.disclosure('Selected WBG resources for the team', guides));

    const trail = r.evidence_trail || {};
    const limits = Array.isArray(trail.limitations) ? trail.limitations.filter(Boolean).join(' ') : String(trail.limitations || '').trim();
    html += k.section('fr-limits', h('Limitations') + `<div class="fr-limits">${k.paragraphs([limits || 'This automated screening is advisory and is limited by the coverage and detail of the uploaded documents. The team should confirm material findings through project and country expertise.', r.advisory_notice])}</div>`);
    return `<article class="fr-readout fr-route-climate">${html}</article>`;
  }

  const api = { FCV_SCALE, CLIMATE_SCALE, FOCUS_LABELS, parseStage3Sections, create };
  root.FcvReadout = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
