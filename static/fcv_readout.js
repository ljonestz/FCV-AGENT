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
    return { deps };
  }

  const api = { FCV_SCALE, CLIMATE_SCALE, FOCUS_LABELS, parseStage3Sections, create };
  root.FcvReadout = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
