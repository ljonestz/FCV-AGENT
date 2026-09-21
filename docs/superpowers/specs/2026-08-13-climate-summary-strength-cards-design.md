# Climate Summary Strength Cards Design

## Goal

Make the three "What is already working" cards understandable to a non-specialist without expanding the summary into a second detailed analysis.

## Design

The verified Climate-FCV analysis will continue to use `existing_responses` as the single source for the cards. Each response description will contain two or three plain-language sentences. The first sentence will be a short, self-contained statement of the project response, suitable for use as the card heading. The remaining sentence or sentences will name a concrete project anchor and explain why the response matters for climate-FCV risk, resilience, inclusion, or delivery.

The summary renderer will split the description at the first sentence boundary when no explicit title is supplied. It will render the first sentence as the heading and the remainder as the explanatory body. For older or repaired payloads containing only one sentence, it will retain the existing safe fallback and show that sentence as both the derived heading and card text. It will no longer shorten headings to eleven words or append an ellipsis.

The layout remains a three-card responsive grid. Headings wrap naturally and remain fully visible; card text uses a readable line height. No new fields, delimiters, schemas, dependencies, or generic FCV behavior are introduced.

## Data Flow

1. The verified analysis prompt asks for grounded two-to-three-sentence `description` values.
2. Existing validation and reader-model projection preserve each description.
3. `climateSummaryStrengths` derives a heading and explanatory body for the summary.
4. `renderClimateVerifiedSummary` renders the same three-card structure with full headings.

## Error Handling and Compatibility

- Empty descriptions remain excluded.
- Duplicate descriptions remain deduplicated.
- A supplied response title takes precedence and leaves the full description in the body.
- One-sentence legacy descriptions remain readable through the current fallback.
- The detailed HTML and DOCX readouts are unchanged.

## Verification

- Prompt test: the analysis prompt requires a short first sentence and additional explanation of the anchor and significance.
- Frontend test: a multi-sentence description becomes a full heading plus non-duplicated explanatory text, with no generated ellipsis.
- Compatibility test: a one-sentence response still produces a usable card.
- Targeted climate prompt/frontend suites and the relevant verified-render tests pass.
