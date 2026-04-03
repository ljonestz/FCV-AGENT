# Rating Consistency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an explicit scoring rubric to the Stage 2 prompt so that sensitivity/responsiveness ratings are formula-driven and consistent across repeated runs.

**Architecture:** Insert a structured rubric (count-based baseline + quality gates) into the Stage 2 prompt, add a hidden reasoning block for auditability, update Stage 3 to inherit Stage 2 ratings, and extend `extract_stage2_ratings()` to capture the reasoning.

**Tech Stack:** Python (Flask), prompt engineering in `DEFAULT_PROMPTS` dict

---

### Task 1: Add Scoring Rubric to Stage 2 Prompt

**Files:**
- Modify: `app.py:384-394` (Stage 2 prompt — rating section)

- [ ] **Step 1: Replace the rating instructions in DEFAULT_PROMPTS["2"]**

Find lines 384–394 in `app.py`:
```
# Status Terminology
Use ONLY these terms: "Strongly addressed" / "Partially addressed" / "Weakly addressed" / "Not addressed"

# Ratings Block
After the TTL-facing narrative, emit this block on its own line:

%%%STAGE2_RATINGS_START%%%
{"sensitivity_rating": "[rating]", "responsiveness_rating": "[rating]"}
%%%STAGE2_RATINGS_END%%%

Rating scale (use exactly one of): Extremely Low | Very Low | Low | Adequate | Well Embedded | Very Well Embedded
```

Replace with:
```
# Status Terminology
Use ONLY these terms: "Strongly addressed" / "Partially addressed" / "Weakly addressed" / "Not addressed"

# Rating Rubric — FOLLOW THIS FORMULA, DO NOT USE YOUR GENERAL IMPRESSION

## Sensitivity Rating
Count how many of the 12 OST recommendations are rated "Strongly addressed" or "Partially addressed" in your Under the Hood recs table (Panel 1). "Weakly addressed" and "Not addressed" do NOT count.

| S-relevant recs addressed | Baseline Rating |
|---|---|
| 0–2 | Extremely Low |
| 3–4 | Very Low |
| 5–6 | Low |
| 7–8 | Adequate |
| 9–10 | Well Embedded |
| 11–12 | Very Well Embedded |

Then apply quality gates (most restrictive cap wins):
- If 3 or more Do No Harm principles are rated "Not addressed" in Panel 2 → cap sensitivity at Low
- If the project contains no conflict or security analysis → cap sensitivity at Adequate
- If the project has no geographic specificity in targeting or beneficiary selection → cap sensitivity at Adequate

## Responsiveness Rating
Count how many of the 4 FCV Refresh shifts (Anticipate, Differentiate, Jobs & Private Sector, Enhanced Toolkit) are actively addressed with concrete, specific measures in the project design — not just passing mentions.

| Shifts addressed + active measures | Baseline Rating |
|---|---|
| 0 shifts, no active measures | Extremely Low |
| 1 shift, minimal measures | Very Low |
| 1–2 shifts, some concrete measures | Low |
| 2–3 shifts, concrete measures with specificity | Adequate |
| 3–4 shifts, strong embedded measures | Well Embedded |
| 4 shifts, deeply embedded throughout design | Very Well Embedded |

Then apply quality gates:
- If zero FCV Refresh shifts are aligned → cap responsiveness at Very Low
- If no adaptive M&E for FCV dynamics exists → cap responsiveness at Low

## Rating Reasoning Block
Before emitting the ratings JSON, emit the following reasoning block showing your step-by-step scoring. This block is stripped from display but used for auditing.

%%%RATING_REASONING_START%%%
SENSITIVITY SCORING:
- Recs addressed (Strongly or Partially): [list rec numbers and status] → count: X/12
- Baseline from count: [rating]
- Quality gate checks:
  - DNH principles rated "Not addressed": [count]/8 → [cap at Low / no cap]
  - Conflict/security analysis present: [yes/no] → [cap at Adequate / no cap]
  - Geographic specificity in targeting: [yes/no] → [cap at Adequate / no cap]
- Most restrictive cap: [rating or "none — baseline stands"]
- FINAL SENSITIVITY RATING: [rating]

RESPONSIVENESS SCORING:
- Shifts addressed: [list which shifts with brief evidence] → count: X/4
- Active root-cause measures: [1-2 sentence summary]
- Baseline from shifts + measures: [rating]
- Quality gate checks:
  - Any shift alignment: [yes/no] → [cap at Very Low / no cap]
  - Adaptive M&E for FCV: [yes/no] → [cap at Low / no cap]
- Most restrictive cap: [rating or "none — baseline stands"]
- FINAL RESPONSIVENESS RATING: [rating]
%%%RATING_REASONING_END%%%

# Ratings Block
After the rating reasoning block, emit this block on its own line:

%%%STAGE2_RATINGS_START%%%
{"sensitivity_rating": "[FINAL SENSITIVITY RATING from above]", "responsiveness_rating": "[FINAL RESPONSIVENESS RATING from above]"}
%%%STAGE2_RATINGS_END%%%

Rating scale (use exactly one of): Extremely Low | Very Low | Low | Adequate | Well Embedded | Very Well Embedded
```

- [ ] **Step 2: Verify the edit**

Read back lines 384–450 to confirm the rubric was inserted correctly and the `%%%STAGE2_RATINGS_START%%%` block still follows the rubric.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add structured scoring rubric to Stage 2 prompt"
```

---

### Task 2: Update Stage 3 to Inherit Stage 2 Ratings

**Files:**
- Modify: `app.py:676` (Stage 3 prompt — rating field instruction)

- [ ] **Step 1: Replace the Stage 3 rating instruction**

Find line 676 in `app.py`. It currently says:
```
IMPORTANT: The JSON block must come AFTER all narrative text. Do not include any explanatory text inside the JSON block itself. Use exact field names as shown. The `tag` field must be exactly "[S]", "[R]", or "[S+R]" (with square brackets). The `fcv_rating` and `fcv_responsiveness_rating` must be exactly one of: "Extremely Low" | "Very Low" | "Low" | "Adequate" | "Well Embedded" | "Very Well Embedded". The `refresh_shift` field must be exactly one of: "Shift A: Anticipate" | "Shift B: Differentiate" | "Shift C: Jobs & private sector" | "Shift D: Enhanced toolkit". The `who_acts` field is semicolon-separated (e.g. "TTL; ESF Team"). The `when` field must be exactly one of: "Identification" | "Preparation" | "Appraisal" | "Implementation" | "Restructuring".
```

Replace with:
```
IMPORTANT: The JSON block must come AFTER all narrative text. Do not include any explanatory text inside the JSON block itself. Use exact field names as shown. The `tag` field must be exactly "[S]", "[R]", or "[S+R]" (with square brackets). For `fcv_rating` and `fcv_responsiveness_rating`: use the sensitivity and responsiveness ratings from Stage 2 exactly as provided in the conversation history. Copy them into the JSON fields without modification. Do not re-assess or override the Stage 2 ratings. The `refresh_shift` field must be exactly one of: "Shift A: Anticipate" | "Shift B: Differentiate" | "Shift C: Jobs & private sector" | "Shift D: Enhanced toolkit". The `who_acts` field is semicolon-separated (e.g. "TTL; ESF Team"). The `when` field must be exactly one of: "Identification" | "Preparation" | "Appraisal" | "Implementation" | "Restructuring".
```

The key change: the sentence about `fcv_rating` and `fcv_responsiveness_rating` now says to copy from Stage 2 rather than independently choosing a value.

- [ ] **Step 2: Verify the edit**

Read back the line to confirm the replacement is correct.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: Stage 3 inherits ratings from Stage 2 instead of generating independently"
```

---

### Task 3: Extract Rating Reasoning in Backend

**Files:**
- Modify: `app.py:112-128` (`extract_stage2_ratings()` function)

- [ ] **Step 1: Update extract_stage2_ratings() to also extract the reasoning block**

Find lines 112–128 in `app.py`:
```python
def extract_stage2_ratings(stage2_output):
    """Extract sensitivity and responsiveness ratings from Stage 2 output.
    Looks for %%%STAGE2_RATINGS_START%%%...%%%STAGE2_RATINGS_END%%% block.
    """
    pattern = r'%%%STAGE2_RATINGS_START%%%(.*?)%%%STAGE2_RATINGS_END%%%'
    match = re.search(pattern, stage2_output, re.DOTALL)
    if not match:
        return {'error': True, 'message': 'No ratings block found in Stage 2 output'}
    try:
        ratings = json.loads(match.group(1).strip())
        return {
            'error': False,
            'sensitivity_rating': ratings.get('sensitivity_rating', 'Unknown'),
            'responsiveness_rating': ratings.get('responsiveness_rating', 'Unknown')
        }
    except json.JSONDecodeError as e:
        return {'error': True, 'message': f'Failed to parse ratings JSON: {str(e)}'}
```

Replace with:
```python
def extract_stage2_ratings(stage2_output):
    """Extract sensitivity and responsiveness ratings from Stage 2 output.
    Looks for %%%STAGE2_RATINGS_START%%%...%%%STAGE2_RATINGS_END%%% block.
    Also extracts %%%RATING_REASONING_START%%%...%%%RATING_REASONING_END%%% if present.
    """
    pattern = r'%%%STAGE2_RATINGS_START%%%(.*?)%%%STAGE2_RATINGS_END%%%'
    match = re.search(pattern, stage2_output, re.DOTALL)
    if not match:
        return {'error': True, 'message': 'No ratings block found in Stage 2 output'}
    # Extract rating reasoning block (optional — for auditing)
    reasoning = ''
    reasoning_pattern = r'%%%RATING_REASONING_START%%%(.*?)%%%RATING_REASONING_END%%%'
    reasoning_match = re.search(reasoning_pattern, stage2_output, re.DOTALL)
    if reasoning_match:
        reasoning = reasoning_match.group(1).strip()
    try:
        ratings = json.loads(match.group(1).strip())
        return {
            'error': False,
            'sensitivity_rating': ratings.get('sensitivity_rating', 'Unknown'),
            'responsiveness_rating': ratings.get('responsiveness_rating', 'Unknown'),
            'rating_reasoning': reasoning
        }
    except json.JSONDecodeError as e:
        return {'error': True, 'message': f'Failed to parse ratings JSON: {str(e)}'}
```

- [ ] **Step 2: Add rating_reasoning to the Stage 2 SSE done event (regular mode)**

Find lines 1899–1909 in `app.py` (Stage 2 done_data building). After line 1903 (`done_data['responsiveness_rating'] = ...`), add:
```python
                    done_data['rating_reasoning'] = stage2_ratings.get('rating_reasoning', '')
```

- [ ] **Step 3: Add rating_reasoning to the Stage 2 SSE done event (Express mode)**

Find line 2174 in `app.py` (Express mode Stage 2 done event). This is a long single-line `json.dumps()` call. Add `'rating_reasoning': stage2_ratings.get('rating_reasoning', '')` to the dict being serialized.

- [ ] **Step 4: Strip the reasoning block from Stage 2 display text**

Find the `clean_stage2_output()` function. It already strips `%%%STAGE2_RATINGS_START/END%%%` and `%%%UNDER_HOOD_START/END%%%` blocks. Add stripping for `%%%RATING_REASONING_START/END%%%` using the same pattern:
```python
    # Strip rating reasoning block
    text = re.sub(r'%%%RATING_REASONING_START%%%.*?%%%RATING_REASONING_END%%%', '', text, flags=re.DOTALL)
```

- [ ] **Step 5: Verify the edits**

Read back the modified function and the done_data lines to confirm correctness.

- [ ] **Step 6: Commit**

```bash
git add app.py
git commit -m "feat: extract and pass rating reasoning block for auditing"
```

---

### Task 4: Verification

- [ ] **Step 1: Run the app locally**

```bash
cd "C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT"
python app.py
```

Open `http://localhost:5000` and run an Express Analysis with a test PAD document. Check:
- Stage 2 sidebar shows ratings
- Stage 3 JSON ratings match Stage 2 ratings
- No `%%%RATING_REASONING%%%` blocks visible in displayed text
- The rating reasoning is present in the SSE response (check browser Network tab)

- [ ] **Step 2: Run the same document a second time**

Compare ratings from run 1 and run 2. They should be the same or adjacent (e.g., both "Low", or "Low" and "Adequate" — not "Very Low" and "Well Embedded").

- [ ] **Step 3: Final commit**

```bash
git add app.py
git commit -m "chore: rating consistency rubric complete"
```
