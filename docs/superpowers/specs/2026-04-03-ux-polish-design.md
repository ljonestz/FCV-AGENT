# FCV Project Screener — UX Polish Design Spec

**Date:** 2026-04-03
**Version:** v7.4 → v7.5 (UX polish)
**Scope:** CSS/HTML/JS changes in `index.html` only (no backend changes)

---

## Context

The FCV Project Screener v7.4 is functionally complete with express mode working. A live walkthrough in Chrome revealed 12 targeted UX improvements needed to make the app more professional, polished, and appropriate for World Bank staff. The existing design foundation (WB palette, Open Sans, card layout) is solid — these are refinements, not a redesign.

---

## Changes

### Area 1: Landing Page Polish

#### 1. Custom Styled File Upload Zones
**Problem:** Raw browser `<input type="file">` shows default "Choose Files | N...n" styling — looks unprofessional.

**Fix:** Hide the native file input. Style the existing drag-and-drop zones with:
- Upload icon (existing Lucide icon or SVG)
- "Drag & drop or browse" text
- A styled "Browse files" button that triggers the hidden input on click
- Keep existing drag-and-drop JS functionality unchanged

**Files:** `index.html` — CSS for `.upload-zone` area + HTML for upload zone markup + JS click handler

#### 2. Mode Card Badges
**Problem:** Express shows "DEFAULT" and Step-by-Step shows "RECOMMENDED" — conflicting signals since Express is the intended default.

**Fix:** Express keeps "DEFAULT" badge. Remove "RECOMMENDED" badge from Step-by-Step entirely (no badge).

**Files:** `index.html` — HTML in mode card section

#### 3. Hero Text Trim
**Problem:** 4-sentence body paragraph in the hero section is too dense; users skip it.

**Fix:** Condense to 2 sentences max. Example:
> "Screen draft WBG project documents for FCV dynamics and generate actionable recommendations. Upload your documents and review the AI's analysis at each stage."

Keep the AI disclaimer notice, S/R definitions, and "How this tool works" link unchanged.

**Files:** `index.html` — HTML in `#landing-hero`

#### 4. Session Bar Cleanup
**Problem:** "No active session" takes space but provides no value on first load.

**Fix:** Hide "No active session" text on initial load. Show session name only when a session is actively named/saved. Keep "View / Edit Prompts" and "Load session" always visible.

**Files:** `index.html` — CSS/JS for `.session-bar` initial state

---

### Area 2: Express Progress Screen

#### 5. Informative Sub-Step Status on Stage Cards
**Problem:** Stage cards only show a single static message (e.g., "Extracting FCV context from your documents..."). Users don't see what's happening during the 5-7 minute wait.

**Fix:** Append sub-step status lines below the spinner text as events arrive:
- Stage 1 events already sent by backend: `research_status` ("Searching FCV context: Honduras..."), `preprocess` ("Identifying project country...")
- Display these as small muted lines below the main spinner text, replacing the previous sub-step
- Stage 2 and 3 have no sub-events — keep single message as-is

**Implementation:** In `runExpress()` SSE handler, when `research_status` or `preprocess` events arrive, update a sub-status element inside the active stage card.

**Files:** `index.html` — JS in express mode SSE handler + HTML for sub-status element in stage cards

#### 6. Smart Time Estimate
**Problem:** "Estimated total: 4-5 minutes" stays static even at 7+ minutes, causing user anxiety.

**Fix:** In `updateEpTimer()`, when elapsed exceeds 300 seconds (5 minutes):
- Replace "Estimated total: 4-5 minutes" with "Taking a little longer than usual"
- When elapsed exceeds 420 seconds (7 minutes): show "Almost done — finalising"
- Never show a specific number once the estimate is exceeded

**Files:** `index.html` — JS in `updateEpTimer()` function

#### 7. Add Informative Messages to Rotation Pool
**Problem:** Rotating messages are a mix of casual and informative. Want to keep both but add more informative ones.

**Fix:** Add these to the `EP_MESSAGES[]` array alongside existing casual messages:
- "Searching trusted sources for country-specific FCV context"
- "Cross-referencing against 12 OST operational standards"
- "Aligning recommendations with WBG FCV Strategy priorities"
- "Tailoring guidance to your project's lifecycle stage"
- "Drawing on FCV Playbook for operational tools and flexibilities"

Keep existing casual messages ("Go grab a coffee", "In FCV settings, nothing good happens quickly", etc.)

**Files:** `index.html` — JS `EP_MESSAGES[]` array

#### 8. Remove Redundant Bottom Note
**Problem:** "Keep this tab open. You'll be able to review each stage's findings once the analysis is complete." repeats info from rotating messages and is always visible.

**Fix:** Replace with a single subtle line: "Do not close or refresh this tab." Smaller font (11px), muted color.

**Files:** `index.html` — HTML/CSS for `.ep-bottom-note`

---

### Area 3: Stage 3 Output Cleanup

#### 9. Condense Instruction Callout
**Problem:** The green callout box has 4 lines of "What you are reading" text that most users skip.

**Fix:** Reduce to a single line: **"Stage 3 of 3 · Recommendations Note — ready to copy"**. Remove the multi-line explanation paragraph. The AI disclaimer below already covers the caveats.

**Files:** `index.html` — JS in `renderOut()` for stage 3 callout generation

#### 10. Remove Repeated S/R Definition Box at Stage 3
**Problem:** The S/R definition box (FCV Sensitivity / FCV Responsiveness definitions) is shown at Stage 2 AND Stage 3. At Stage 3, it wastes vertical space before the actual content.

**Fix:** Do not render the S/R definition box at Stage 3. Keep it at Stage 2 only. Keep the tag legend ("Reading this assessment" — explains [S], [R], [S+R] badges) at Stage 3 since it's a compact quick-reference.

**Files:** `index.html` — JS in `renderOut()` for stage 3 S/R box rendering

#### 11. Hide "view prompt" on Stage Headings
**Problem:** "view prompt" link next to stage headings (e.g., "Recommendations Note view prompt") is a developer feature exposed to all users.

**Fix:** Remove the "view prompt" link from stage heading rendering. Users can still access prompts via "View / Edit Prompts" in the session bar.

**Files:** `index.html` — JS in stage heading render logic

#### 12. Priority Stepper Text Readability
**Problem:** Priority titles in the horizontal stepper are 9px uppercase — hard to read, especially for long titles.

**Fix:** Bump `.ps-label` font-size from 9px to 10px. Add `text-overflow: ellipsis` and `max-height` to prevent titles from wrapping to 3-4 lines. Show full title on hover via `title` attribute.

**Files:** `index.html` — CSS for `.ps-label`

---

## Files to Modify

| File | Changes |
|---|---|
| `index.html` | All 12 fixes — CSS (~lines 8-1516), HTML (~lines 1539-1897), JS (~lines 1962-4683) |

No changes to `app.py`, `background_docs.py`, or any backend files.

---

## Verification

After implementing all changes:
1. Navigate to the app in Chrome
2. Verify landing page: styled upload zones, correct mode badges, trimmed hero, clean session bar
3. Upload a test document and run Express Analysis
4. Verify progress screen: informative sub-steps on Stage 1 card, smart timer at 5+ minutes, mixed casual+informative messages, shortened bottom note
5. After completion, verify Stage 3 output: no S/R definition box, condensed callout, no "view prompt" links, readable priority stepper
6. Test that "View / Edit Prompts" still works from session bar
7. Test step-by-step mode still works (no regressions)
8. Check mobile view at 375px width for obvious breakages
