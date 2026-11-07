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

  const CLOSING_LINE = 'This automated screening supports task-team judgment. It is not a compliance, eligibility or clearance decision.';

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

  const STAGE_TAG_RE = /\s*\[(?:S|R|S\+R)\]/g;
  // Spec pattern, but only spaces or tabs before "Tagged" so a paragraph break before the sentence survives.
  const TAG_JUSTIFICATION_RE = /[ \t]*Tagged \[(?:S|R|S\+R)\][^.]*\./g;

  // Card prose only: drop model sentences that justify the S/R tag.
  function stripTagNotes(text) {
    return String(text || '').replace(TAG_JUSTIFICATION_RE, '').trim();
  }

  // Reviewer notes ("[Verify before sharing: ...]") are pulled out of displayed prose and listed once
  // in Limitations, without internal block hashes or PF-nnn fact ids.
  const VERIFY_NOTE_RE = /[ \t]*\[Verify before sharing:\s*([^\]]*)\]/gi;

  function cleanVerifyNote(note) {
    let t = String(note || '');
    t = t.replace(/\s*\((?:source )?blocks?\s+[0-9a-f]{8,}[^)]*\)/gi, '');
    t = t.replace(/(?:\band\s+)?(?:\bsource\s+)?\bblocks?\s+[0-9a-f]{8,}(?:\s*(?:,|and)\s*[0-9a-f]{8,})*/gi, '');
    t = t.replace(/(?:\band\s+|,\s*)?\bPF-\d+\b/g, '');
    // A lead clause left with no object ("Check  and :") is dropped.
    t = t.replace(/^\s*(?:Check|See|Compare)(?:\s|,|and)*:\s*/i, '');
    t = t.replace(/\(\s*\)/g, '').replace(/\s{2,}/g, ' ').replace(/\s+([,.;:])/g, '$1').trim();
    return t ? t.charAt(0).toUpperCase() + t.slice(1) : '';
  }

  // Parenthetical internal evidence ids in prose ("(PF-008, PF-010)", "(RG-001)") are dropped from display.
  const INTERNAL_IDS_RE = /[ \t]*\((?:PF|RG|CE|ER|EV)-\d+(?:\s*(?:,|;|and)\s*(?:PF|RG|CE|ER|EV)-\d+)*\)/g;

  // Removes reviewer notes from one string; cleaned notes go to sink (deduplicated, first-seen order).
  function extractVerifyNotes(text, sink) {
    let value = String(text || '');
    if (/\((?:PF|RG|CE|ER|EV)-\d/.test(value)) value = value.replace(INTERNAL_IDS_RE, '');
    if (value.indexOf('[') < 0) return value;
    let found = false;
    const out = value.replace(VERIFY_NOTE_RE, (m, note) => {
      found = true;
      const clean = cleanVerifyNote(note);
      const key = clean.toLowerCase();
      if (clean && sink && !sink.some(x => x.toLowerCase() === key)) sink.push(clean);
      return '';
    });
    return found ? out.replace(/[ \t]+$/gm, '') : value;
  }

  // Copy of plain data with every string scrubbed; HTML fields (keys ending in "Html") and functions are kept.
  function scrubDeep(value, sink) {
    if (typeof value === 'string') return extractVerifyNotes(value, sink);
    if (Array.isArray(value)) return value.map(v => scrubDeep(v, sink));
    if (value && typeof value === 'object' && Object.getPrototypeOf(value) === Object.prototype) {
      const out = {};
      Object.keys(value).forEach(key => { out[key] = /Html$/.test(key) ? value[key] : scrubDeep(value[key], sink); });
      return out;
    }
    return value;
  }

  // "Project Appraisal Document (PAD)_v3.docx" -> "Project Appraisal Document (PAD) v3".
  function displayFileName(name) {
    return String(name || '').replace(/^.*[\/]/, '').replace(/\.[A-Za-z0-9]{1,5}$/, '').replace(/_+/g, ' ').replace(/\s{2,}/g, ' ').trim();
  }

  // Display order for normal priorities: High, Medium, Low, then anything else; stable within a level.
  const LEVEL_ORDER = { high: 0, medium: 1, low: 2 };
  function orderByLevel(priorities) {
    return (Array.isArray(priorities) ? priorities : []).map((p, index) => ({ p, index }))
      .sort((a, b) => {
        const la = LEVEL_ORDER[String((a.p && a.p.risk_level) || '').trim().toLowerCase()];
        const lb = LEVEL_ORDER[String((b.p && b.p.risk_level) || '').trim().toLowerCase()];
        return ((la === undefined ? 3 : la) - (lb === undefined ? 3 : lb)) || (a.index - b.index);
      });
  }
  const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  // Stage 2 "## Supplementary FCV Dimensions" bullets ("- **Label:** text") as smaller checks.
  function parseSupplementaryPoints(markdown) {
    const lines = String(markdown || '').replace(/\r\n?/g, '\n').split('\n');
    const start = lines.findIndex(l => /^#{2,4}\s+supplementary fcv dimensions\b/i.test(l.trim()));
    if (start < 0) return [];
    const level = (lines[start].trim().match(/^#+/) || [''])[0].length;
    const out = [];
    for (let i = start + 1; i < lines.length; i++) {
      const line = lines[i].trim();
      const head = line.match(/^(#{1,6})\s/);
      if (head && head[1].length <= level) break;
      const m = line.match(/^[-*+]\s+\*\*(.+?)\*\*\s*:?\s*(.*)$/);
      if (!m) continue;
      const title = m[1].replace(/:\s*$/, '').replace(STAGE_TAG_RE, '').trim();
      const why = m[2].replace(/^:\s*/, '').replace(STAGE_TAG_RE, '').replace(/\*\*/g, '').replace(/\s{2,}/g, ' ').trim();
      if (title) out.push({ title, why });
    }
    return out;
  }

  // "Research run timestamp: 2026-11-07T08:20:40+00:00" -> "7 November 2026" (date part only, no timezone shift).
  function researchDate(brief) {
    const m = String(brief || '').match(/Research run timestamp:\s*(\d{4})-(\d{2})-(\d{2})/i);
    if (!m) return '';
    const month = MONTHS[Number(m[2]) - 1];
    return month ? `${Number(m[3])} ${month} ${m[1]}` : '';
  }

  // Markdown fragment -> one line of plain text (escapes, emphasis and link syntax removed).
  function plainText(text) {
    return String(text || '').replace(/\\(.)/g, '$1').replace(/\[([^\]]*)\]\([^)\s]*\)/g, '$1')
      .replace(/\*\*|__|`/g, '').replace(/\s*-?\s*\b\d+\s+days?\s+ago\b/gi, '').replace(/\s+/g, ' ').trim();
  }

  // Stored research brief -> provider-cited sources: [{title, url, excerpt}], http(s) only, one entry per URL.
  // Collection stops at the model-interpretation part of the brief.
  function researchSources(brief) {
    const out = [];
    const seen = new Set();
    let current = null;
    const lines = String(brief || '').replace(/\r\n?/g, '\n').split('\n');
    for (const line of lines) {
      if (/^\s*#{1,6}\s/.test(line) && /model interpretation/i.test(line)) break;
      const link = line.match(/^\s*[-*+]\s+\[([^\]]+)\]\((\S+)\)(?:\s|$)/);
      if (link) {
        current = null;
        const url = safeUrl(link[2]);
        if (!url || seen.has(url)) continue;
        seen.add(url);
        current = { title: plainText(link[1]) || url, url, excerpt: '' };
        out.push(current);
        continue;
      }
      const quote = line.match(/^\s*>\s?(.*)$/);
      if (quote) {
        if (current && !current.excerpt) current.excerpt = plainText(quote[1]);
        continue;
      }
      if (line.trim() && !/^\s/.test(line)) current = null;
    }
    return out;
  }

  // Plain-text paragraphs for a brief without a source list: headings, quote markers and preambles dropped.
  function researchParagraphs(brief) {
    const paras = String(brief || '').replace(/\r\n?/g, '\n').split(/\n\s*\n+/)
      .map(p => p.split('\n').filter(l => !/^\s*(?:\\?#)+\s/.test(l)).map(l => l.replace(/^\s*>\s?/, '')).join(' '))
      .map(plainText).filter(p => p && !/^Research run timestamp:/i.test(p));
    if (paras.length && /^(?:I'll|I will|Let me)\b/i.test(paras[0])) paras.shift();
    return paras;
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

    // Limitations: only the first sentence of a multi-sentence paragraph is bold.
    function limitParagraphs(list) {
      return (list || []).map(t => String(t || '').trim()).filter(Boolean)
        .map(t => takeSentences(t, 1).rest ? `<p dir="auto" class="fr-p">${boldFirst(t)}</p>` : `<p dir="auto" class="fr-p">${esc(t)}</p>`).join('');
    }

    function verifyList(notes) {
      const list = (notes || []).filter(Boolean);
      return list.length ? `<div class="fr-verify"><h3 class="fr-verify-lbl">Points to verify before sharing</h3><ul class="fr-verify-list">${list.map(n => `<li dir="auto">${esc(n)}</li>`).join('')}</ul></div>` : '';
    }

    function limitsBox(paras, notes) {
      return `<div class="fr-limits">${limitParagraphs(paras)}${verifyList(notes)}</div>`;
    }

    // Share .html research briefing: intro line plus a list of source links with a one-line excerpt.
    function researchBriefing(brief) {
      const sources = researchSources(brief);
      if (!sources.length) {
        const paras = researchParagraphs(brief);
        return paras.length ? paras.map(t => `<p dir="auto" class="fr-p">${esc(t)}</p>`).join('') : '';
      }
      const date = researchDate(brief);
      const lead = `Public sources retrieved ${date ? `on ${date} ` : ''}to supplement the project documents.`;
      const items = sources.map(src => `<li><a href="${esc(src.url)}" target="_blank" rel="noopener noreferrer">${esc(src.title)}</a>${src.excerpt ? `<span class="fr-research-ex" dir="auto">${esc(src.excerpt)}</span>` : ''}</li>`).join('');
      return `<p class="fr-p fr-research-intro">${esc(lead)}</p><ul class="fr-research-list">${items}</ul>`;
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
      const tileHtml = tiles.map(t => `<div class="fr-sc-tile" data-fr-rating="${esc(t.key)}"><div class="fr-sc-label">${esc(t.label)}</div><div class="fr-sc-value">${esc(t.value || 'Not available')}</div>${meter(t.steps, t.level)}${t.level ? `<div class="fr-sc-scale" data-copy-skip><span>${esc(t.lo)}</span><span class="fr-sc-of">${t.level} of ${t.steps}</span><span>${esc(t.hi)}</span></div>` : ''}<div class="fr-sc-def">${esc(t.def)}</div></div>`).join('');
      const pills = (count.pills || []).map(p => `<span class="fr-pill ${p.cls}">${esc(p.text)}</span>`).join('');
      return `<p class="fr-sc-lead">${esc(SCORECARD_LEAD)}</p><section class="fr-scorecard" aria-label="Assessment ratings">${tileHtml}<div class="fr-sc-count"><div class="fr-sc-count-lbl">${esc(count.label)}</div><div class="fr-sc-count-num">${Number(count.number) || 0}</div>${pills ? `<div class="fr-sc-pills">${pills}</div>` : ''}${count.def ? `<div class="fr-sc-count-def">${esc(count.def)}</div>` : ''}</div></section>`;
    }

    function ratingRows(rows) {
      return `<div class="fr-ratings">${rows.map(r => `<div class="fr-rating-row"><div class="fr-rating-meta"><div class="fr-rating-dim">${esc(r.dim)}</div><span class="fr-rating-val ${r.cls}">${esc(r.value || 'Not available')}</span><div class="fr-rating-def">${esc(r.def)}</div></div><div class="fr-rating-why">${r.whyHtml || '<p class="fr-p">No rationale was returned for this rating.</p>'}</div></div>`).join('')}</div>`;
    }

    function priorityCard(p) {
      // Drafts follow the first draftsAt zones (default: after every zone).
      const zoneHtml = list => list.filter(z => z.html).map(z => `<section class="fr-zone"><h4 class="fr-lbl">${esc(z.label)}</h4>${z.html}</section>`).join('');
      const allZones = p.zones || [];
      const at = Number.isInteger(p.draftsAt) ? p.draftsAt : allZones.length;
      const drafts = (p.drafts || []).filter(d => d.text).map(d => `<section class="fr-draft"><div class="fr-draft-hd"><div class="fr-draft-lbl">${esc(d.label)}</div><button type="button" class="fr-copy" data-copy-skip onclick="${COPY_DRAFT_HANDLER}">Copy</button></div>${d.forText ? `<div class="fr-draft-for">For: ${esc(d.forText)}</div>` : ''}<p dir="auto" class="fr-draft-text">${esc(d.text)}</p></section>`).join('');
      const cycle = p.cycle && p.cycle.text ? `<p class="fr-cycle"><strong>${esc(p.cycle.label || 'When to address')}:</strong> ${esc(p.cycle.text)}</p>` : '';
      const meta = p.supHtml ? `<span class="fr-pc-meta">${p.supHtml}</span>` : '';
      const src = Number.isInteger(p.srcIndex) ? ` data-fr-src-index="${p.srcIndex}"` : '';
      return `<details class="fr-pc" id="${p.id}"${src}${p.open ? ' open' : ''}><summary class="fr-pc-hdr"><span class="fr-pc-rank">${p.rank}</span><span class="fr-pc-title">${meta}<span dir="auto" class="fr-pc-title-txt">${esc(p.title)}</span></span><span class="fr-pc-chev" aria-hidden="true">${CHEVRON_SVG}</span></summary><div class="fr-pc-body">${zoneHtml(allZones.slice(0, at))}${drafts}${zoneHtml(allZones.slice(at))}${cycle}${p.extraHtml || ''}</div></details>`;
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

    // Card header meta: segments joined by a middot; the dimension segment carries a class the mobile CSS
    // hides (timing stays visible). Each separator sits inside its own segment, so none is left dangling.
    function metaSegments(list) {
      return (list || []).filter(x => x && x[0]).map((x, i) => `<span class="fr-meta-seg${x[1] ? ' ' + x[1] : ''}">${i ? ' &middot; ' : ''}${x[0]}</span>`).join('');
    }

    // Normal-route priority level pill: level word plus "priority", level colour class.
    function levelPill(level) {
      const key = String(level || '').trim().toLowerCase();
      return key ? pill(`${String(level).trim()} priority`, 'fr-pill-' + key) : '';
    }

    const kit = { esc, md, boldFirst, timingLabel, takeSentences, prose, paragraphs, limitParagraphs, verifyList, limitsBox, researchBriefing, numbering, toc, sub, intro, advisory, infoBox, section, closing, meter, scorecard, ratingRows, priorityCard, cards, disclosure, checkItems, pill, levelPill, metaSegments, stripTagNotes };
    return Object.assign(kit, {
      renderNormal: data => renderNormal(kit, data),
      renderClimate: (reader, opts) => renderClimate(kit, reader, opts),
    });
  }

  // Curated WBG resources (source: output/20261107_normal-guidance-list.json). The three climate reports
  // are pinned on the climate route only; the normal route lists the FCV items in file order (max 7).
  const PINNED_CLIMATE_GUIDANCE = [
    { title: "Maximizing the Peace and Social Dividends of Climate Action", url: "https://www.worldbank.org/en/topic/fragilityconflictviolence/publication/maximizing-the-peace-and-social-dividends-of-climate-action", use: "Use this source to identify how climate action can strengthen peace and social outcomes, and where project design can maximize those dividends." },
    { title: "FCV-Sensitive Climate Action Framework", url: "https://www.worldbank.org/en/topic/fragilityconflictviolence/publication/framework-for-promoting-fcv-sensitive-climate-action", use: "Use this source to stress-test whether climate action is conflict-sensitive, avoids harm and remains deliverable in fragile settings." },
    { title: "Defueling Conflict", url: "https://www.worldbank.org/en/topic/environment/publication/defueling-conflict-environment-and-natural-resource-management-as-a-pathway-to-peace", use: "Use this source to assess how environmental and natural-resource governance can reduce conflict risks and create incentives for cooperation." },
  ];
  const NORMAL_GUIDANCE = [
    { title: "A World Bank Group Strategy for Engaging in FCV Settings (2026-2030)", url: "https://www.worldbank.org/en/topic/fragilityconflictviolence/publication/a-wbg-strategy-for-engaging-in-fcv-settings-2026-2030", use: "The current framework for FCV engagement, built on four shifts: anticipate better, adopt a differentiated approach, deliver as one WBG on jobs, and strengthen the toolkit, partnerships and staffing." },
    { title: "Classification of Fragile and Conflict-Affected Situations", url: "https://www.worldbank.org/en/topic/fragilityconflictviolence/brief/classification-of-fragile-and-conflict-affected-situations", use: "Confirms whether the country is on the current FCS list, which shapes the policy flexibilities and financing that may apply." },
    { title: "Pathways for Peace: Inclusive Approaches to Preventing Violent Conflict", url: "https://www.worldbank.org/en/topic/fragilityconflictviolence/publication/pathways-for-peace-inclusive-approaches-to-preventing-violent-conflict", use: "The joint UN and World Bank study on how exclusion drives conflict risk; useful when framing targeting, inclusion and prevention choices." },
    { title: "Environmental and Social Framework", url: "https://www.worldbank.org/en/projects-operations/environmental-and-social-framework", use: "The standards behind risk assessment, stakeholder engagement and grievance arrangements (including ESS1 and ESS10), with links to the supporting good practice notes." },
    { title: "Good Practice Note: Addressing SEA/SH in Human Development Operations", url: "https://thedocs.worldbank.org/en/doc/e2ff01be0f07c82d73bc0c5e7ddf394f-0290032022/original/ESF-Good-Practice-Note-on-Addressing-SEA-SH-in-HD-Operations-First-Edition-September-16-2022.pdf", use: "Advisory guidance on preventing and responding to sexual exploitation, abuse and harassment in health, education and social protection operations." },
    { title: "Good Practice Note: Addressing SEA/SH in Investment Project Financing involving Major Civil Works", url: "https://thedocs.worldbank.org/en/doc/6f3d9ddc6010c4221315dd1282958e41-0290032022/original/SEA-SH-Civil-Works-GPN-Third-Edition-Final-October-12-2022.pdf", use: "Advisory guidance on SEA/SH risk screening, codes of conduct and survivor-centred response where projects finance civil works." },
    { title: "Forced Displacement", url: "https://www.worldbank.org/en/topic/forced-displacement", use: "Bank resources on refugees, internally displaced people and host communities; relevant where returnees or displaced people are among the beneficiaries." },
  ];

  function guideKey(text) {
    return String(text || '').toLowerCase().replace(/\s+/g, ' ').trim();
  }

  // One guidance entry: title link, curated blurb and an optional "Relevant to this project" line.
  function guideItem(k, g, relHtml) {
    const url = safeUrl(g.url);
    const title = url ? `<a class="fr-guide-title" href="${k.esc(url)}" target="_blank" rel="noopener noreferrer">${k.esc(g.title)}</a>` : `<span class="fr-guide-title">${k.esc(g.title)}</span>`;
    const blurb = String(g.practical_value || g.project_use || g.use || '').trim();
    return `<div class="fr-guide">${title}${blurb ? `<p dir="auto" class="fr-p">${k.esc(blurb)}</p>` : ''}${relHtml ? `<p class="fr-guide-rel">Relevant to this project: ${relHtml}</p>` : ''}</div>`;
  }

  const NORMAL_LIMITATION = 'Findings are based on the text of the project documents and may miss arrangements described elsewhere. Ratings and priorities are advisory and should be confirmed through project and country expertise.';

  const SCORECARD_LEAD = 'The ratings below are a high-level AI assessment based on insights from the project package. They do not reflect a formal WBG or FCV Group designation. Read them as a general guide, alongside the more detailed overview and assessment that follows.';

  // Zero gets no line: an empty list can mean a withheld or incomplete stage, not "none needed".
  function countDef(n, one, many) {
    if (!n) return '';
    return n === 1 ? `1 ${one} is identified by the FCV Screener.` : `${n} ${many} are identified by the FCV Screener.`;
  }

  function priorityTitle(title) {
    return String(title || 'Priority action').replace(/^\s*Priority\s+\d+\s*(?:[·•:.\-–]\s*)?/i, '').trim() || 'Priority action';
  }

  function countPills(items, keyOf, labels, prefix) {
    const counts = {};
    items.forEach(item => { const k = keyOf(item); if (k) counts[k] = (counts[k] || 0) + 1; });
    return labels.filter(l => counts[l.key]).map(l => ({ text: `${prefix || ''}${counts[l.key]} ${l.text}`, cls: l.cls }));
  }

  function renderNormal(k, data) {
    const verifyNotes = [];
    const d = scrubDeep(data || {}, verifyNotes);
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

      // Display order only (High, Medium, Low); extras keep the original index for Go Deeper and warnings.
      const cards = orderByLevel(priorities).map(({ p, index }, i) => {
        const actions = Array.isArray(p.actions) ? p.actions : [];
        const actionsHtml = actions.length ? `<ol class="fr-actions">${actions.map(a => `<li>${a.document_element ? `<strong>${k.esc(a.document_element)}:</strong> ` : ''}${k.esc(stripTagNotes(a.guidance))}</li>`).join('')}</ol>` : '';
        const cycleText = stripTagNotes(p.implementation_note || (p.project_cycle && p.project_cycle.primary_text) || '');
        const cycleLabel = p.implementation_note ? 'Implementation note' : ((p.project_cycle && p.project_cycle.primary_label) || 'When to address');
        const sup = k.metaSegments([[k.levelPill(p.risk_level)], [k.esc(FOCUS_LABELS[p.tag] || p.tag || '')], [k.esc(p.fcv_dimension || ''), 'fr-meta-dim'], [k.esc(k.timingLabel(p.action_timing)), 'fr-meta-time']]);
        return k.priorityCard({
          id: `fr-priority-${i + 1}`, rank: i + 1, open: i === 0, supHtml: sup, title: priorityTitle(p.title), srcIndex: index,
          zones: [{ label: 'The gap', html: k.prose(stripTagNotes(p.the_gap)) }, { label: 'Why it matters', html: k.prose(stripTagNotes(p.why_it_matters)) }, { label: 'Suggested actions', html: actionsHtml }],
          drafts: actions.map(a => ({ label: 'Suggested Text', forText: a.document_element || '', text: a.suggested_language || '' })),
          cycle: { label: cycleLabel, text: cycleText },
          extraHtml: typeof d.priorityExtras === 'function' ? d.priorityExtras(p, index) : '',
        });
      }).join('');
      html += k.section('fr-cards-sec', h('Priority Actions for the Task Team') + intro + k.cards(cards, n));
    }

    const smaller = (Array.isArray(d.smallerPoints) ? d.smallerPoints : []).filter(x => x && x.title);
    if (smaller.length) {
      html += k.section('fr-checks', h('Smaller Points to Check During Preparation')
        + k.disclosure('Smaller checks for the project team to confirm', '<p class="fr-intro">These sit alongside the main priorities above. None is a reason to stop the project.</p>' + k.checkItems(smaller)));
    }

    if (d.watchHtml) {
      html += k.section('fr-watch', h('Watch List for Supervision')
        + k.disclosure('Risks to monitor during implementation', '<p class="fr-intro">These are FCV risks or dynamics the team cannot act on now but should monitor during implementation. They do not affect the FCV ratings above.</p>' + d.watchHtml));
    }
    html += d.tailHtml || '';

    const guides = NORMAL_GUIDANCE.map(g => guideItem(k, g, '')).join('');
    if (guides) html += k.section('fr-guidance', h('Relevant WBG Guidance') + k.disclosure('Selected WBG resources for the team', guides));

    const files = (Array.isArray(d.fileNames) ? d.fileNames : []).map(displayFileName).filter(Boolean);
    const retrieved = researchDate(d.researchBrief);
    const limits = [
      files.length ? `Documents uploaded for this run: ${files.join(', ')}.` : '',
      retrieved ? `Background research was retrieved on ${retrieved}; events after that date are not reflected.` : '',
      d.partial ? 'This run is partial; some sections may be missing.' : '',
      NORMAL_LIMITATION,
    ];
    html += k.section('fr-limits-sec', h('Limitations') + k.limitsBox(limits, verifyNotes));
    if (d.researchHtml) html += `<details class="fr-disc fr-research"><summary class="fr-disc-sum">Background research and sources</summary><div class="fr-disc-body out-body">${d.researchHtml}</div></details>`;
    return `<article class="fr-readout fr-route-fcv">${head}${k.toc(h.list)}${html}${k.closing()}</article>`;
  }
  const THEME_QUESTIONS = {
    'Climate risks, design and delivery': 'Does the project address interacting climate and FCV risks in design and delivery?',
    'Wider peace and social dividends': 'Could the project generate wider peace and social benefits, and how could these be strengthened?',
    'Access, inclusion and potential harm': 'Will people benefit fairly, and could delivery create exclusion or harm?',
  };

  // Mirrors _assessment_themes in sector_lenses/climate_verified_render.py (core question -> theme title).
  const CORE_THEME_TITLES = {
    cq1_interaction: 'Climate risks, design and delivery', cq2_maladaptation: 'Climate risks, design and delivery', cq6_adaptive: 'Climate risks, design and delivery',
    cq4_inclusion: 'Access, inclusion and potential harm', cq5_institutions: 'Access, inclusion and potential harm', cq3_dividends: 'Wider peace and social dividends',
    driver_tenure: 'Access, inclusion and potential harm', driver_representation: 'Access, inclusion and potential harm',
    driver_rents: 'Access, inclusion and potential harm', driver_value_chain: 'Access, inclusion and potential harm',
  };

  function coreThemeTitle(q) {
    if (q.question_id === 'cq2-access-path-dependence' || q.question_id === 'cq3-shared-benefit') return 'Access, inclusion and potential harm';
    return CORE_THEME_TITLES[q.theme] || 'Climate risks, design and delivery';
  }

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

  // Fallback overview text saved before the wording change; shown with the current sentence instead.
  const FALLBACK_OVERVIEW = 'A short summary is not shown for this run because it could not be checked against the project documents. The findings and priorities below remain available; read them alongside the limitations at the end of this note.';
  const LEGACY_FALLBACK_OVERVIEW = [
    'The automated Summary could not be independently verified. The operational context and assessment findings provide the available analysis.',
    'Use the ranked operational priorities and points to check as the basis for review. Confirm the stated evidence limitations before relying on the brief.',
  ];

  function renderClimate(k, reader, opts) {
    const verifyNotes = [];
    // Scrubbed copy for display only; the stored reader is never changed.
    const r = reader && typeof reader === 'object' ? scrubDeep(reader, verifyNotes) : {};
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
      { key: 'high', text: 'high', cls: 'fr-pill-conf fr-pill-conf-high' }, { key: 'medium', text: 'medium', cls: 'fr-pill-conf fr-pill-conf-medium' }, { key: 'low', text: 'low', cls: 'fr-pill-conf fr-pill-conf-low' }], 'Confidence: ') });

    const overview = (Array.isArray(r.summary_overview) ? r.summary_overview : [r.summary_overview]).map(t => String(t || '').trim()).filter(Boolean)
      .map(t => LEGACY_FALLBACK_OVERVIEW.includes(t) ? FALLBACK_OVERVIEW : t).filter((t, i, list) => list.indexOf(t) === i);
    let snapshot = '';
    let contextHtml = '';
    let fallbackNote = '';
    if (r.summary_overview_status === 'generated' && overview.length) {
      snapshot = overview[0];
      contextHtml = k.paragraphs(overview.slice(1, 3));
    } else if (r.reader_contract === 'final-reader-v1') {
      // Fallback text explains why no summary is shown; it opens the Limitations box, not the Overview.
      fallbackNote = overview.join(' ');
    } else {
      const paras = splitParagraphs(r.executive_readout);
      const split = k.takeSentences(paras[0] || '', 2);
      snapshot = split.head;
      contextHtml = k.paragraphs([split.rest, paras[1]].filter(Boolean));
    }
    const working = (Array.isArray(r.existing_responses) ? r.existing_responses : []).map(x => x && x.description).filter(Boolean).slice(0, 4);
    const gaps = (Array.isArray(r.summary_gaps) ? r.summary_gaps : []).map(x => x && x.text).filter(Boolean).slice(0, 5);
    const themeList = Array.isArray(r.assessment_themes) ? r.assessment_themes : [];
    // Overview is always section 01, so Assessment Findings (when it renders) is section 02.
    const findingsId = 'fr-s02';
    // Findings and priorities carry the gaps; the Overview lists them only when no findings render.
    const showGaps = gaps.length && !themeList.length;
    let html = k.section('fr-exec', h('Overview')
      + (snapshot ? k.infoBox('Assessment snapshot', `<strong>${k.esc(snapshot)}</strong>`) : '')
      + contextHtml
      + (working.length ? k.sub('What is already working') + k.paragraphs(working) : '')
      + (showGaps ? k.sub('Key gaps at this stage') + k.paragraphs(gaps) : ''));

    const rankIndex = new Map();
    priorities.forEach((p, i) => { const n = Number(p.rank); if (Number.isInteger(n) && !rankIndex.has(n)) rankIndex.set(n, i + 1); });
    const themes = themeList.map(t => {
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
        const paras = splitParagraphs(stripTagNotes(p.narrative));
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
          id: `fr-priority-${rank}`, rank, open: i === 0, title: priorityTitle(p.title), draftsAt: 2,
          supHtml: [confidencePill(k, p.confidence, ' confidence'), lead ? `Lead: ${k.esc(lead)}` : '', k.esc(target)].filter(Boolean).join(' &middot; '),
          zones: [{ label: 'Why this matters', html: k.paragraphs(why) }, { label: 'What the team could do', html: k.paragraphs(act) },
            { label: 'Practical considerations', html: k.paragraphs([practical.join(' ')]) },
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

    // Pinned reports always show; the stored reader is never changed (the export snapshot compares it exactly).
    const server = (Array.isArray(r.guidance_items) ? r.guidance_items : []).filter(g => g && g.title).slice(0, 4);
    const isPinned = g => PINNED_CLIMATE_GUIDANCE.some(c => guideKey(c.title) === guideKey(g.title));
    const guideList = PINNED_CLIMATE_GUIDANCE.map(c => server.find(g => guideKey(g.title) === guideKey(c.title)) || c)
      .concat(server.filter(g => !isPinned(g)));
    // A core question whose source is this item points to the Assessment Findings question it feeds.
    const coreQuestions = Array.isArray(r.core_questions) ? r.core_questions : [];
    // Short theme names read cleanly in a sentence; the full questions are in section 02.
    const shownQuestion = title => {
      const t = themeList.find(x => x && x.title === title);
      return t ? (t.title || '') : '';
    };
    const guides = guideList.map(g => {
      const labels = [];
      if (themes) {
        coreQuestions.filter(q => q && guideKey(q.source) === guideKey(g.title)).forEach(q => {
          const label = shownQuestion(coreThemeTitle(q));
          if (label && !labels.includes(label)) labels.push(label);
        });
      }
      const rel = labels.length ? `informs the findings on ${labels.slice(0, 2).map(l => `<a href="#${findingsId}">${k.esc(l.charAt(0).toLowerCase() + l.slice(1))}</a>`).join(' and on ')} (section 02).` : '';
      return guideItem(k, g, rel);
    }).join('');
    if (guides) html += k.section('fr-guidance', h('Relevant WBG Guidance') + k.disclosure('Selected WBG resources for the team', guides));

    const trail = r.evidence_trail || {};
    const limits = Array.isArray(trail.limitations) ? trail.limitations.filter(Boolean).join(' ') : String(trail.limitations || '').trim();
    const limitsText = limits || 'This automated screening is advisory and is limited by the coverage and detail of the uploaded documents. The team should confirm material findings through project and country expertise.';
    html += k.section('fr-limits-sec', h('Limitations') + k.limitsBox([fallbackNote, limitsText, r.advisory_notice], verifyNotes));
    const saysAlready = /does not constitute/i.test(`${limitsText} ${r.advisory_notice || ''}`);
    return `<article class="fr-readout fr-route-climate">${head}${k.toc(h.list)}${html}${saysAlready ? '' : k.closing()}</article>`;
  }

  const api = { FCV_SCALE, CLIMATE_SCALE, FOCUS_LABELS, DEFINITIONS, CLOSING_LINE, CHEVRON_SVG, PINNED_CLIMATE_GUIDANCE, NORMAL_GUIDANCE, parseStage3Sections, parseSupplementaryPoints, researchDate, researchSources, orderByLevel, stripTagNotes, extractVerifyNotes, cleanVerifyNote, displayFileName, create };
  root.FcvReadout = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
