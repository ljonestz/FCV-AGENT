# Climate Verified Operational Routing Design

**Date:** 2026-08-13  
**Status:** Approved by user direction to proceed  
**Policy basis:** GitHub Copilot/CoWork review of the authoritative OPCS corpus supplied in the handover attachment. Codex did not access that restricted corpus.

## Problem

The verified Climate-FCV Express path runs before the generic Stage 1 metadata extraction. As a result, it often receives `Unknown` document and instrument values, yet the guidance selector currently treats an unknown instrument as IPF. The same gap prevents reliable multi-country bank guarding and leaves users unable to see the assumptions that shaped the readout.

## Required outcome

Resolve an operational context from the uploaded project document before country-bank selection and verified analysis. Use that context to select only instrument- and document-compatible guidance, pass it through the model stages, and show it in the reader. If a safe route cannot be established, withhold document-targeted drafting guidance and say why.

## Design

### 1. Server-derived operation context

Add a typed verified-operation context containing:

- base instrument: IPF, PforR, DPF, or Unknown;
- document type: PCN, PAD, PID, Project Paper, Program Paper, Program Document, or Unknown;
- MPA wrapper flag and resolved base instrument;
- country scope: single or multi-country;
- preparation regime and processing model when strongly evidenced;
- environmental and social regime when strongly evidenced;
- warning codes and evidence notes.

Filename markers and document headings are authoritative inputs. Browser-supplied structured values are hints only. Ambiguous detections resolve to `Unknown`, not a convenient default.

### 2. Instrument-correct routing

- IPF: ESF/ESS-oriented targets only when the operation is routed to IPF and the ES regime supports them.
- PforR: Program Paper/PAD, ESSA, Program Action Plan, DLI and verification targets; never ESCP/SEP/ESS drafting as if IPF.
- DPF: Program Document, prior actions/policy matrix, poverty and social impact, and environmental/forest/natural-resource analysis; never ESS instruments.
- MPA: retain the program wrapper while routing through the detected base lending instrument. If the base is unresolved, guidance is withheld.

Unknown instrument or document type selects no operational guidance. This is a deliberate fail-closed behavior.

### 3. Regime handling

Use instrument-specific preparation boundaries from the supplied OPCS review: IPF and PforR operations on or after 17 April 2026, and DPF operations on or after 18 April 2026, enter the new preparation model. Strong document markers can identify the model when a reliable date is unavailable. MPA does not itself determine an ES regime; its base instrument does.

### 4. Country-bank safety

Resolve explicit regional or multi-country markers before bank selection. The current country bank remains single-country only, so regional operations receive no country package until a safe multi-country selection contract is implemented.

### 5. Reader transparency

Show a compact “How this operation was routed” block in the full and summary views, including instrument, document, preparation model, E&S regime, and MPA status. Any unresolved field that suppresses guidance must be visible in plain language.

## Scope boundary

This increment does not redesign Additional Financing, restructuring, implementation-stage review, or multi-country evidence aggregation. It may recognize those document labels, but it will withhold unsupported drafting destinations rather than invent them.

## Verification

Tests must cover document/instrument detection, DPF abbreviation handling, MPA base routing, hybrid PforR-with-IPF-component handling, multi-country bank suppression, fail-closed unknown guidance, regime boundaries, propagation into prompts/output, and visible reader context.
