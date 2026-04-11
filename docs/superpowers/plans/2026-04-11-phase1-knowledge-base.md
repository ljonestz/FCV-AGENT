# Phase 1: Knowledge Base — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the knowledge foundation (WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, broadened existing constants) that Phases 2-4 consume.

**Architecture:** Three new constants added to `background_docs.py`, plus targeted broadening of existing constants. All new constants are structured as Python dicts so they can be sliced per-instrument or per-term at injection time. A new helper function `get_instrument_slice()` in `app.py` returns the relevant instrument's knowledge for prompt injection.

**Tech Stack:** Python (background_docs.py constants), Flask (app.py helper functions)

**Spec:** `docs/superpowers/specs/2026-04-11-colleague-feedback-response-design.md` — Workstream 2 (sections 5.1–5.5)

**This is Plan 1 of 4:**
- Phase 1: Knowledge Base (this plan)
- Phase 2: Prompt Changes
- Phase 3: Frontend UX
- Phase 4: Implementation Review Pipeline

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `background_docs.py` | Modify | Add WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, WB_PROCESS_GUIDE stub; broaden existing constants |
| `app.py` | Modify | Add `get_instrument_slice()`, `get_glossary_terms()` helpers; update imports; add `/api/glossary` endpoint |

---

### Task 1: Research and draft WB_INSTRUMENT_GUIDE — IPF

**Files:**
- Modify: `background_docs.py` (append after STAGE_GUIDANCE_MAP, line ~779)

This is the highest-priority instrument (60-70% of use cases). The guide must cover what IPF can and cannot do, FCV-relevant levers, and common assessment pitfalls — so that later prompt changes can prevent the LLM from judging an IPF for things only possible under other instruments.

- [ ] **Step 1: Research current IPF policy from public WBG sources**

Use web search to find the latest publicly available IPF policy framework, operational policy references, and any FCV-specific IPF guidance. Key sources: World Bank Operations Manual, IPF policy page, FCV Operational Playbook references to IPF. Focus on: what IPF finances (investment activities, not policy reform), how components work, what operational flexibilities are available, what's NOT possible under IPF (no policy conditionality, no results-based disbursement linked to policy reforms).

- [ ] **Step 2: Write the IPF entry in WB_INSTRUMENT_GUIDE**

Add to `background_docs.py` after the `STAGE_GUIDANCE_MAP` closing brace (after line 779):

```python
# ─────────────────────────────────────────────────────────────────────────────
# 9. WB_INSTRUMENT_GUIDE — Instrument-specific knowledge for assessment (~8,000 tokens total)
# Last verified: 2026-04
# Policy-sensitive fields: ESF framework (post-Oct 2018), procurement framework, IDA allocation
# Review trigger: Update when WBG operational policies change
# ─────────────────────────────────────────────────────────────────────────────

WB_INSTRUMENT_GUIDE = {
    "IPF": {
        "name": "Investment Project Financing",
        "description": (
            "IPF supports governments in financing specific investment activities — civil works, "
            "goods, services, capacity building, and institutional strengthening. It is the most "
            "common WBG lending instrument in FCV settings. IPF finances discrete project activities "
            "with defined components, not policy reforms or budget support. Projects have a fixed "
            "closing date and results framework tied to specific deliverables."
        ),
        "fcv_levers": (
            "CERC (zero-dollar emergency component, activatable without Board restructuring); "
            "HEIS (hands-on expanded implementation support for procurement); "
            "TPM (third-party monitoring where direct supervision is impossible); "
            "Geospatial monitoring (GEMS, GIS, geo-localization, satellite imagery, remote sensing); "
            "Phased disbursement (conditions tied to tranches); "
            "Unallocated funds (budget reserve for flexibility); "
            "Framework approach (umbrella design, details in POM); "
            "Para 12 efficiencies (higher retroactive financing up to 40%, increased PPA up to $10M, "
            "condensed procedures) for projects in countries with urgent need or capacity constraints; "
            "CLD (community and local development) for participatory approaches; "
            "Alternative implementation arrangements (UN agencies, NGOs, community-driven mechanisms)."
        ),
        "not_applicable": (
            "IPF CANNOT: set policy conditionality or prior actions (that is DPO); "
            "use results-based disbursement linked to Disbursement-Linked Indicators (that is PforR); "
            "finance recurrent government expenditures or budget support; "
            "mandate government policy or regulatory reform as a condition of disbursement. "
            "When assessing an IPF, do NOT penalise for: absence of policy dialogue mechanisms, "
            "lack of DPO-style reform conditionality, absence of DLIs or program-level results-based "
            "financing, or failure to address macro-level governance reform. These are structurally "
            "outside the IPF instrument's scope."
        ),
        "typical_structure": (
            "Components (typically 2-5) funding specific activities: infrastructure, service delivery, "
            "capacity building, project management. Each component has a budget allocation. "
            "Results Framework with PDO-level and intermediate indicators. "
            "Implementation arrangements: PIU or embedded government unit, procurement plan, "
            "FM arrangements, E&S instruments (ESIA, ESCP, SEP, LMP). "
            "Standard PAD sections: Strategic Context, Project Description, Implementation "
            "Arrangements, Assessment Summary, plus Annexes."
        ),
        "common_fcv_considerations": (
            "IPFs in FCV settings commonly face: weak PIU capacity requiring HEIS or alternative "
            "implementation partners; security constraints limiting supervision (TPM, GEMS needed); "
            "elite capture risk in procurement and beneficiary targeting; need for adaptive design "
            "(CERC, unallocated funds, phased implementation); community engagement challenges "
            "requiring conflict-sensitive stakeholder engagement; fiduciary risk requiring "
            "enhanced FM arrangements. A deliberately simple IPF design (few components, lean RF, "
            "narrow geographic scope) may be an intentional and appropriate FCV strategy — "
            "particularly where implementation capacity is limited or where the team plans "
            "a follow-on AF to scale up. Do not penalise lean design."
        ),
        "preparation_process": (
            "PCN (Concept Note) -> QER (Quality Enhancement Review) -> Appraisal -> "
            "Decision Review/ROC -> Board approval. Key decision points for FCV integration: "
            "PCN stage (embed FCV in ToC and design); QER (confirm FCV elements); "
            "Appraisal (finalise E&S instruments, confirm implementation arrangements). "
            "Para 12 projects may use condensed procedures with accelerated timelines."
        ),
        "supervision_process": (
            "Regular ISR reporting (typically every 6 months). MTR usually at project midpoint. "
            "Restructuring available for component changes, reallocation, indicator revision, "
            "geographic refocusing, closing date extension. AF for scaling up or addressing gaps. "
            "In FCV: more frequent supervision missions recommended; GEMS/TPM for remote monitoring; "
            "adaptive management through repurposing (within project description) or restructuring."
        ),
        "policy_transitions": (
            "Projects approved before October 2018 use the old Operational Safeguards framework "
            "(OP/BP 4.01, 4.04, 4.10, 4.11, 4.12, 4.36, 4.37, 7.50). Projects approved after "
            "October 2018 use the Environmental and Social Framework (ESF) with ESS1-ESS10. "
            "The document's Data Sheet is authoritative for which framework applies. "
            "Do not reference ESF standards when assessing a project that uses old OP/BPs, "
            "and vice versa."
        ),
    },
}
```

- [ ] **Step 3: Verify the constant is syntactically valid**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "import background_docs; print(type(background_docs.WB_INSTRUMENT_GUIDE)); print(list(background_docs.WB_INSTRUMENT_GUIDE.keys()))"`

Expected: `<class 'dict'>` and `['IPF']`

- [ ] **Step 4: Commit**

```bash
git add background_docs.py
git commit -m "feat: add WB_INSTRUMENT_GUIDE with IPF entry"
```

---

### Task 2: Add PforR, DPO, and TA entries to WB_INSTRUMENT_GUIDE

**Files:**
- Modify: `background_docs.py` (add entries to the WB_INSTRUMENT_GUIDE dict)

- [ ] **Step 1: Research PforR, DPO, and TA instruments from public WBG sources**

Use web search for: PforR policy framework (results-based, DLIs, program-level), DPO policy framework (policy conditionality, prior actions, budget support), and TA/ASA (Advisory Services and Analytics) modalities. For each: what it finances, how it differs from IPF, what FCV levers are available, what's NOT applicable.

- [ ] **Step 2: Add PforR entry**

Add after the IPF entry closing brace within `WB_INSTRUMENT_GUIDE`:

```python
    "PforR": {
        "name": "Program-for-Results",
        "description": (
            "PforR links disbursement to achievement of measurable results (Disbursement-Linked "
            "Indicators/DLIs) rather than to specific expenditures. It finances government programs "
            "using country systems. PforR is less common in FCV settings due to capacity requirements "
            "but can be effective where government systems have minimum functionality."
        ),
        "fcv_levers": (
            "DLIs can be designed to incentivise FCV-sensitive outcomes (e.g., service delivery "
            "in conflict-affected areas, inclusive targeting, institutional strengthening); "
            "Program Action Plans can embed FCV risk mitigation; "
            "Verification protocols can include TPM and independent verification agents; "
            "Scalable DLIs allow adaptive targets based on evolving FCV context; "
            "Integrated Fiduciary and E&S Systems Assessment (IFSA/ESSA) can flag FCV risks."
        ),
        "not_applicable": (
            "PforR does NOT: finance specific procurement packages or civil works directly "
            "(those are financed through the government program using country systems); "
            "provide CERC or emergency response components (IPF-specific); "
            "use HEIS for procurement (country systems are used). "
            "When assessing PforR, do NOT penalise for: absence of specific procurement plans "
            "(country systems are used), lack of project-level PIU (program uses existing "
            "institutional structures), or absence of component-level budget breakdowns."
        ),
        "typical_structure": (
            "Program scope definition, DLIs (5-10 typically), Program Action Plan, "
            "IFSA/ESSA, Verification Protocol. DLIs define what the government must achieve "
            "for disbursement. Results are verified before funds are released."
        ),
        "common_fcv_considerations": (
            "PforR in FCV requires: minimum government system capacity for program execution; "
            "robust verification mechanisms (independent agents, TPM) given weak oversight; "
            "DLIs that are achievable in volatile contexts (not over-ambitious); "
            "ESSA that addresses FCV-specific E&S risks through government systems; "
            "risk that government capacity deteriorates during implementation. "
            "PforR may be inappropriate where state capacity is very low or where "
            "government legitimacy is contested."
        ),
        "preparation_process": (
            "Similar to IPF but with Program Systems Assessment (PSA) replacing "
            "standard appraisal. IFSA and ESSA are mandatory. DLI design and "
            "verification protocol are critical preparation outputs."
        ),
        "supervision_process": (
            "DLI verification drives disbursement. Independent Verification Agent (IVA) "
            "confirms achievement. Program Action Plan implementation monitored. "
            "Mid-term review assesses DLI achievability and program trajectory."
        ),
        "policy_transitions": (
            "PforR uses the Environmental and Social Systems Assessment (ESSA), not the "
            "ESF or old OP/BPs. This is a distinct assessment framework. "
            "Do not apply ESF ESS standards to PforR projects."
        ),
    },
```

- [ ] **Step 3: Add DPO entry**

```python
    "DPO": {
        "name": "Development Policy Operation",
        "description": (
            "DPOs provide budget support to governments in exchange for policy and institutional "
            "reforms (prior actions). They finance the government's general budget, not specific "
            "investment activities. DPOs are used when policy reform is the primary development "
            "objective. Less common in FCV settings due to reform capacity requirements, but "
            "used for governance reform, macro-fiscal stability, and enabling environment work."
        ),
        "fcv_levers": (
            "Prior actions can target FCV-relevant reforms (governance transparency, "
            "anti-corruption, resource revenue management, security sector governance, "
            "social protection expansion to FCV-affected populations); "
            "Policy dialogue on FCV drivers (elite capture, exclusion, institutional legitimacy); "
            "Programmatic DPO series can sequence reforms over time, building capacity gradually; "
            "Trigger matrix for indicative prior actions provides flexibility across series."
        ),
        "not_applicable": (
            "DPO does NOT: finance specific investment activities, civil works, goods, or services "
            "(those are IPF); use CERC, HEIS, TPM, or GEMS (these are IPF operational tools); "
            "have a results framework with project-level intermediate indicators in the IPF sense; "
            "have PIU, procurement plans, or component-level implementation arrangements. "
            "When assessing DPO, do NOT penalise for: absence of CERC or emergency components, "
            "lack of TPM or geospatial monitoring, absence of project-level beneficiary targeting, "
            "or missing community engagement/GRM mechanisms (DPOs work through policy, not "
            "direct service delivery). DPO-specific questions (OST Manual Q16-Q19) apply; "
            "IPF-specific questions do not."
        ),
        "typical_structure": (
            "Prior actions (policy/regulatory changes the government must complete before "
            "disbursement), results indicators (expected outcomes of reforms), "
            "policy matrix (for programmatic series showing reform trajectory), "
            "macroeconomic framework assessment, environmental and poverty/social analysis."
        ),
        "common_fcv_considerations": (
            "DPOs in FCV require: analysis of reform context including vested interests, "
            "elite capture risks, and political economy of policy change; assessment of "
            "whether prior actions are conflict-sensitive and won't exacerbate fragility; "
            "realistic expectations about reform pace in FCV settings; "
            "attention to distributional impacts of policy reforms on vulnerable groups. "
            "Key risk: policy reforms can shift power dynamics and trigger backlash "
            "from groups that benefit from the status quo."
        ),
        "preparation_process": (
            "Prior actions agreed with government; macroeconomic assessment; "
            "environmental and poverty/social analysis. No ESF/ESIA — DPOs use "
            "environmental and poverty/social impact analysis instead."
        ),
        "supervision_process": (
            "Disbursement upon completion of prior actions (single-tranche or multi-tranche). "
            "Programmatic series: annual operations with evolving prior actions. "
            "Policy dialogue is continuous. No ISR in the IPF sense — "
            "Implementation Completion Report at series end."
        ),
        "policy_transitions": (
            "DPOs use environmental and poverty/social analysis, not ESF or old OP/BPs. "
            "Do not apply ESF standards or IPF safeguards frameworks to DPO assessments."
        ),
    },
```

- [ ] **Step 4: Add TA entry**

```python
    "TA": {
        "name": "Technical Assistance / Advisory Services and Analytics",
        "description": (
            "TA (often delivered as Advisory Services and Analytics — ASA) provides knowledge, "
            "analytical work, and capacity building without direct lending. TA can be grant-funded "
            "(trust funds) or funded through the Bank's administrative budget. In FCV contexts, "
            "TA supports diagnostics, institutional assessments, and preparation for lending operations."
        ),
        "fcv_levers": (
            "FCV diagnostics and analytics (RRA, sector-specific FCV assessments); "
            "Institutional capacity assessment and strengthening design; "
            "Stakeholder mapping and political economy analysis; "
            "Design support for upcoming lending operations in FCV settings; "
            "Knowledge exchange and peer learning on FCV-sensitive approaches."
        ),
        "not_applicable": (
            "TA does NOT: provide financing for investment activities, policy reform, or budget "
            "support; have the operational flexibilities of IPF (no CERC, HEIS, TPM, GEMS); "
            "require E&S instruments (ESIA, ESCP) unless it involves pilot activities; "
            "have a results framework in the lending-operation sense. "
            "When assessing TA, do NOT apply lending-operation assessment criteria. "
            "Focus on: analytical quality, FCV-relevance of findings, actionability of "
            "recommendations, and contribution to future lending operation design."
        ),
        "typical_structure": (
            "Terms of reference, deliverables (reports, diagnostics, training), "
            "timeline, budget (usually from trust funds or Bank budget). "
            "No PAD, no components, no procurement plan in the IPF sense."
        ),
        "common_fcv_considerations": (
            "TA in FCV: access constraints for field work; security considerations for "
            "consultants and data collection; political sensitivity of analytical findings; "
            "need for conflict-sensitive research methods; stakeholder engagement in "
            "contexts where trust is low."
        ),
        "preparation_process": "Concept note, terms of reference, funding arrangement.",
        "supervision_process": "Deliverable-based supervision. No ISR or MTR.",
        "policy_transitions": "N/A — TA does not trigger safeguards policies.",
    },
}
```

- [ ] **Step 5: Verify all entries are valid**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "import background_docs; ig = background_docs.WB_INSTRUMENT_GUIDE; print(list(ig.keys())); [print(f'  {k}: {len(str(v))} chars') for k,v in ig.items()]"`

Expected: `['IPF', 'PforR', 'DPO', 'TA']` with IPF being the largest entry.

- [ ] **Step 6: Commit**

```bash
git add background_docs.py
git commit -m "feat: add PforR, DPO, TA entries to WB_INSTRUMENT_GUIDE"
```

---

### Task 3: Add FCV_GLOSSARY constant

**Files:**
- Modify: `background_docs.py` (append after WB_INSTRUMENT_GUIDE)

The glossary serves double duty: prompt grounding for consistent definitions in Stage 2, and frontend tooltips via a new API endpoint.

- [ ] **Step 1: Research definitions from WBG and trusted FCV sources**

Use web search to find authoritative WBG definitions for key FCV terms. Priority sources: WBG FCV Strategy, OST Manual, FCV Playbook, World Bank public website. Fallback: OECD States of Fragility, UNDP, UNHCR, ICG.

- [ ] **Step 2: Write the FCV_GLOSSARY constant**

Add after the `WB_INSTRUMENT_GUIDE` closing brace:

```python
# ─────────────────────────────────────────────────────────────────────────────
# 10. FCV_GLOSSARY — Key FCV terms for prompt grounding and frontend tooltips
# Last verified: 2026-04
# Sources: WBG FCV Strategy, OST Manual, FCV Playbook, OECD, UNDP, UNHCR
# ─────────────────────────────────────────────────────────────────────────────

FCV_GLOSSARY = {
    "elite_capture": {
        "term": "Elite Capture",
        "definition": (
            "The process by which public resources, services, or decision-making "
            "are co-opted by politically connected or economically powerful groups "
            "at the expense of intended beneficiaries. In FCV settings, elite capture "
            "can undermine project effectiveness and exacerbate grievances."
        ),
        "measurement": (
            "Assessed through: procurement irregularity patterns, geographic distribution "
            "of benefits vs. need, beneficiary selection audits, stakeholder complaints, "
            "third-party monitoring of resource allocation."
        ),
        "source": "WBG FCV Operational Manual; OECD States of Fragility"
    },
    "social_cohesion": {
        "term": "Social Cohesion",
        "definition": (
            "The quality and strength of relationships between groups in society, "
            "characterised by trust, shared identity, and willingness to cooperate "
            "for mutual benefit. In FCV contexts, weakened social cohesion is both "
            "a driver and consequence of fragility and conflict."
        ),
        "measurement": (
            "Assessed through: inter-group trust surveys, participation in community "
            "organisations, perceptions of equity and inclusion, frequency of inter-group "
            "cooperation or conflict incidents."
        ),
        "source": "WBG FCV Strategy; UNDP Social Cohesion Framework"
    },
    "conflict_analysis": {
        "term": "Conflict Analysis",
        "definition": (
            "Systematic examination of the profile, causes, actors, and dynamics of "
            "conflict in a given context. In WBG operations, typically conducted through "
            "Risk and Resilience Assessments (RRAs) that identify drivers of fragility "
            "and sources of resilience."
        ),
        "measurement": (
            "Quality assessed by: specificity to sector/geography, identification of "
            "root causes vs. symptoms, analysis of key actors and incentives, "
            "actionability of findings for project design."
        ),
        "source": "WBG FCV Operational Playbook — Diagnostics Phase"
    },
    "do_no_harm": {
        "term": "Do No Harm",
        "definition": (
            "The principle that development interventions should not inadvertently "
            "exacerbate conflict, reinforce power asymmetries, or undermine sources "
            "of resilience. Requires active analysis of how project activities interact "
            "with existing FCV dynamics."
        ),
        "measurement": (
            "Assessed against 8 principles: conflict-sensitive targeting, avoiding power "
            "asymmetry reinforcement, preventing inter-group tension exacerbation, equitable "
            "geographic distribution, elite capture safeguards, staff/beneficiary security, "
            "unintended consequence monitoring, accessible grievance mechanisms."
        ),
        "source": "WBG FCV Operational Manual — 8 Do No Harm Principles"
    },
    "third_party_monitoring": {
        "term": "Third-Party Monitoring (TPM)",
        "definition": (
            "Independent verification of project activities by NGOs or research organisations "
            "where direct World Bank supervision is not possible due to insecurity or access "
            "constraints. TPM provides objective assessment of implementation progress, "
            "fiduciary compliance, and E&S risk management."
        ),
        "measurement": (
            "Assessed by: independence and credibility of monitoring agent, coverage of "
            "project areas, frequency of monitoring visits, actionability of findings."
        ),
        "source": "WBG FCV Operational Manual — Rec 6; FCV Playbook — Implementation"
    },
    "grievance_redress_mechanism": {
        "term": "Grievance Redress Mechanism (GRM)",
        "definition": (
            "A system through which project-affected people can raise concerns, complaints, "
            "or grievances about a project and receive a response. In FCV settings, GRMs "
            "should go beyond compliance to actively build state-citizen trust and "
            "institutional accountability."
        ),
        "measurement": (
            "Assessed by: accessibility to all groups including marginalised populations, "
            "anonymity protections, response timeliness, feedback loop closure, "
            "integration of findings into adaptive management."
        ),
        "source": "WBG ESF ESS10; FCV Operational Manual"
    },
    "cerc": {
        "term": "Contingency Emergency Response Component (CERC)",
        "definition": (
            "A zero-dollar financing component included in IPF projects that can be "
            "rapidly activated during crises without Board restructuring. Enables swift "
            "fund reallocation from other components to finance emergency response activities."
        ),
        "measurement": "Presence/absence in project design; activation readiness.",
        "source": "WBG IPF Policy; FCV Operational Playbook — Preparation"
    },
    "heis": {
        "term": "Hands-on Expanded Implementation Support (HEIS)",
        "definition": (
            "Direct procurement support provided by WBG staff to implementing agencies "
            "in FCV settings, bypassing standard timelines. HEIS provides physical "
            "assistance with procurement processes but does not substitute for "
            "Borrower decision-making authority."
        ),
        "measurement": "Presence/absence in implementation arrangements; scope of support.",
        "source": "WBG FCV Operational Manual; FCV Playbook — Preparation"
    },
    "geospatial_monitoring": {
        "term": "Geospatial Monitoring",
        "definition": (
            "The use of geographic and spatial technologies for project monitoring and "
            "supervision. Encompasses GEMS (Geo-Enabling initiative for Monitoring and "
            "Supervision), GIS, geo-localization, satellite imagery, remote sensing, "
            "and spatial data analysis. Enables remote supervision where direct access "
            "is constrained by insecurity."
        ),
        "measurement": (
            "Assessed by: integration into M&E framework, spatial coverage, "
            "frequency of data collection, use for decision-making."
        ),
        "source": "WBG FCV Operational Manual — Rec 6; FCV Playbook — Implementation"
    },
    "rra": {
        "term": "Risk and Resilience Assessment (RRA)",
        "definition": (
            "The WBG's primary diagnostic tool for understanding FCV drivers and sources "
            "of resilience. Conducted in collaboration with the FCV Group to facilitate "
            "holistic understanding and provide differentiated, strategically relevant "
            "recommendations for country engagement and project design."
        ),
        "measurement": (
            "Quality assessed by: comprehensiveness of driver/resilience analysis, "
            "sector relevance, geographic specificity, actionability for operations."
        ),
        "source": "WBG FCV Operational Playbook — Diagnostics Phase"
    },
    "forced_displacement": {
        "term": "Forced Displacement",
        "definition": (
            "The involuntary movement of people from their homes due to conflict, "
            "violence, persecution, or disaster. Includes refugees (crossing international "
            "borders), internally displaced persons (IDPs, within borders), and host "
            "communities affected by displacement. WBG takes a development approach "
            "focusing on medium-to-long-term challenges."
        ),
        "measurement": (
            "Assessed by: displacement population estimates, host community impact, "
            "integration of displaced populations in project targeting, "
            "durable solutions considered."
        ),
        "source": "WBG FCV Policy Para 9; Joint Data Center (JDC); 2023 WDR"
    },
    "fcv_sensitivity": {
        "term": "FCV Sensitivity",
        "definition": (
            "The degree to which a project is aware of and designed for the FCV context. "
            "Demonstrates contextual awareness of FCV drivers, conflict-informed design, "
            "Do No Harm principles, and FCV-adapted operations. Shorthand: does the project "
            "avoid making things worse?"
        ),
        "measurement": (
            "Assessed against 12 OST recommendations and 8 Do No Harm principles. "
            "Rating scale: Extremely Low to Very Well Embedded."
        ),
        "source": "WBG FCV Strategy; FCV Operational Manual"
    },
    "fcv_responsiveness": {
        "term": "FCV Responsiveness",
        "definition": (
            "The degree to which a project actively works to change the FCV situation. "
            "Addresses root causes of fragility, builds resilience, leverages FCV tools "
            "for transformative impact, and connects outcomes to stability and peace "
            "dividends. Shorthand: does the project actively help make fragility better?"
        ),
        "measurement": (
            "Assessed against 4 FCV Refresh strategic shifts (Anticipate, Differentiate, "
            "Jobs & Private Sector, Enhanced Toolkit). Rating scale: Extremely Low to "
            "Very Well Embedded."
        ),
        "source": "WBG FCV Strategy Refresh (January 2026)"
    },
    "fcv_refresh_shifts": {
        "term": "FCV Refresh Strategic Shifts",
        "definition": (
            "Four cross-cutting strategic directions from the WBG FCV Strategy Refresh "
            "(January 2026): Shift A — Anticipate (forward-looking risk monitoring); "
            "Shift B — Differentiate (tailor to FCV classification); "
            "Shift C — Jobs & Private Sector (economic livelihoods as stability pathway); "
            "Shift D — Enhanced Toolkit & Partnerships (operational flexibilities and HDP nexus)."
        ),
        "measurement": (
            "Assessed by: number and depth of shifts actively addressed in project design; "
            "whether shifts are merely mentioned or embedded with concrete measures."
        ),
        "source": "WBG FCV Strategy Refresh (January 2026)"
    },
    "impact_evaluation": {
        "term": "Impact Evaluation (IE)",
        "definition": (
            "Rigorous evaluation using experimental or quasi-experimental methods to "
            "measure the causal impact of a project or intervention. In FCV settings, "
            "IEs face additional challenges (insecurity, displacement, data gaps) but "
            "generate critical evidence on what works. Also referred to as 'IE' in "
            "WBG documents."
        ),
        "measurement": (
            "Assessed by: appropriateness of methodology for FCV constraints, "
            "government ownership, budget allocation, early planning in project cycle."
        ),
        "source": "WBG FCV Operational Manual — Rec 11; FCV Playbook — Closing"
    },
}
```

- [ ] **Step 3: Verify the constant is valid**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "import background_docs; g = background_docs.FCV_GLOSSARY; print(f'{len(g)} terms'); [print(f'  {k}: {v[\"term\"]}') for k,v in g.items()]"`

Expected: `15 terms` with all term names printed.

- [ ] **Step 4: Commit**

```bash
git add background_docs.py
git commit -m "feat: add FCV_GLOSSARY with 15 key terms"
```

---

### Task 4: Broaden existing constants for concept recognition

**Files:**
- Modify: `background_docs.py` — targeted edits to `FCV_OPERATIONAL_MANUAL` and `PLAYBOOK_IMPLEMENTATION`

This addresses the colleague's feedback about narrow keyword matching. Each change broadens a specific term to its concept family.

- [ ] **Step 1: Broaden GEMS reference in FCV_OPERATIONAL_MANUAL (Rec 6)**

In `background_docs.py`, find the Rec 6 text in `FCV_OPERATIONAL_MANUAL` and update:

Find (in `FCV_OPERATIONAL_MANUAL`, around line 129-130):
```
**Rec 6 — Use innovative and digital tools** [Shift D: Enhanced Toolkit]
GEMS (satellite/mobile for remote supervision), TPM (independent verification by NGOs/research organisations), digital data collection. Selection should match operational needs, access constraints, and ethical considerations.
```

Replace with:
```
**Rec 6 — Use innovative and digital tools** [Shift D: Enhanced Toolkit]
Geospatial monitoring and digital tools for remote supervision and data collection. This includes but is not limited to: GEMS, GIS, geo-localization, satellite imagery, remote sensing, spatial data analysis, mobile data collection platforms, and digital payment/feedback systems. TPM (independent verification by NGOs/research organisations, spot checks, remote verification protocols). Selection should match operational needs, access constraints, and ethical considerations. Recognise the concept and intent — any form of technology-enabled monitoring or verification satisfies this recommendation.
```

- [ ] **Step 2: Broaden capacity building reference in FCV_OPERATIONAL_MANUAL (Rec 7)**

Find (around line 134):
```
**Rec 7 — Strengthen in-country M&E capacity and systems** [Shift D: Enhanced Toolkit]
Strengthening client M&E systems should be the guiding principle. Conduct client M&E capacity assessment. Design M&E system with focus on capacity building and sustainability. Avoid parallel systems where possible.
```

Replace with:
```
**Rec 7 — Strengthen in-country M&E capacity and systems** [Shift D: Enhanced Toolkit]
Strengthening client M&E systems should be the guiding principle. Conduct client M&E capacity assessment. Design M&E system with focus on capacity building and sustainability. Avoid parallel systems where possible. Note: capacity building in FCV extends beyond M&E to include institutional strengthening for crisis management, recovery planning, and service delivery resilience. Recognise any systematic capacity building effort (training, institutional strengthening, systems development) as relevant to this recommendation.
```

- [ ] **Step 3: Broaden impact evaluation reference in FCV_OPERATIONAL_MANUAL (Rec 11)**

Find (around line 147):
```
**Rec 11 — Consider pros/cons of impact evaluations** [Shift D: Enhanced Toolkit]
Impact evaluations generate rigorous evidence on FCV operations but need different implementation in FCV. Not suitable for all interventions. Prioritise when: interventions are significant; evidence is scarce or contested; strong government ownership exists. Plan and budget early; explore appropriate methodologies for FCV limitations.
```

Replace with:
```
**Rec 11 — Consider pros/cons of impact evaluations** [Shift D: Enhanced Toolkit]
Impact evaluations (also abbreviated as IE in WBG documents) generate rigorous evidence on FCV operations but need different implementation in FCV. Encompasses experimental design, quasi-experimental methods, and other rigorous evaluation methodologies. Not suitable for all interventions. Prioritise when: interventions are significant; evidence is scarce or contested; strong government ownership exists. Plan and budget early; explore appropriate methodologies for FCV limitations. When reviewing documents, check the Abbreviations/Acronyms section — IE, RCT, and similar abbreviations may refer to impact evaluation activities.
```

- [ ] **Step 4: Broaden GEMS reference in PLAYBOOK_IMPLEMENTATION**

Find in `PLAYBOOK_IMPLEMENTATION` (around line 492-493):
```
### GEMS (Geo-Enabling Initiative for Monitoring and Supervision)
Systematically enhances M&E on client side and portfolio supervision on WB side. Builds capacity for field-appropriate, low-cost, open-source technology for digital real-time data collection. Platforms for remote supervision, real-time risk monitoring, portfolio mapping, and cross-partner coordination.
```

Replace with:
```
### Geospatial Monitoring (including GEMS)
Geospatial monitoring encompasses GEMS (Geo-Enabling Initiative for Monitoring and Supervision), GIS, geo-localization, satellite imagery, remote sensing, and spatial data analysis. GEMS specifically enhances M&E on client side and portfolio supervision on WB side, building capacity for field-appropriate, low-cost, open-source technology for digital real-time data collection. Platforms for remote supervision, real-time risk monitoring, portfolio mapping, and cross-partner coordination. Any form of geospatial or spatial monitoring approach satisfies this operational category.
```

- [ ] **Step 5: Verify the file still imports cleanly**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "import background_docs; print('OK')"`

Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add background_docs.py
git commit -m "feat: broaden recognition vocabulary in existing FCV constants"
```

---

### Task 5: Add helper functions to app.py

**Files:**
- Modify: `app.py` — add `get_instrument_slice()`, `get_glossary_terms()`, update imports, add `/api/glossary` endpoint

These helpers are used by Phase 2 (prompt injection) and Phase 3 (frontend glossary).

- [ ] **Step 1: Update imports in app.py**

Find (line 13-17):
```python
from background_docs import (
    FCV_GUIDE, FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK,
    PLAYBOOK_DIAGNOSTICS, PLAYBOOK_PREPARATION, PLAYBOOK_IMPLEMENTATION,
    PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP
)
```

Replace with:
```python
from background_docs import (
    FCV_GUIDE, FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK,
    PLAYBOOK_DIAGNOSTICS, PLAYBOOK_PREPARATION, PLAYBOOK_IMPLEMENTATION,
    PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP,
    WB_INSTRUMENT_GUIDE, FCV_GLOSSARY
)
```

- [ ] **Step 2: Add get_instrument_slice() function**

Add after the `get_stage_name()` function (after line ~1323):

```python
def get_instrument_slice(instrument_type: str) -> str:
    """Return a formatted text block with instrument-specific knowledge.

    Used for prompt injection — only the relevant instrument's knowledge
    is included, keeping token usage to ~2,000 tokens per stage.
    Falls back to IPF if instrument type is unknown.
    """
    instrument = instrument_type.upper() if instrument_type else 'IPF'
    # Normalise common variations
    normalise = {'INVESTMENT PROJECT FINANCING': 'IPF', 'PROGRAM FOR RESULTS': 'PFORR',
                 'DEVELOPMENT POLICY OPERATION': 'DPO', 'TECHNICAL ASSISTANCE': 'TA',
                 'PROGRAM-FOR-RESULTS': 'PFORR', 'P4R': 'PFORR'}
    instrument = normalise.get(instrument, instrument)
    if instrument not in WB_INSTRUMENT_GUIDE:
        instrument = 'IPF'  # Default to most common instrument

    entry = WB_INSTRUMENT_GUIDE[instrument]
    parts = [
        f"## World Bank Instrument: {entry['name']} ({instrument})",
        f"\n**What it is:** {entry['description']}",
        f"\n**FCV-relevant operational levers:** {entry['fcv_levers']}",
        f"\n**NOT applicable to this instrument (do not penalise for absence):** {entry['not_applicable']}",
        f"\n**Typical structure:** {entry['typical_structure']}",
        f"\n**Common FCV considerations:** {entry['common_fcv_considerations']}",
    ]
    if entry.get('policy_transitions'):
        parts.append(f"\n**Policy transitions:** {entry['policy_transitions']}")
    return '\n'.join(parts)


def get_glossary_for_prompt() -> str:
    """Return a compact glossary string for prompt injection (Stage 2).

    Includes only term + definition (not measurement/source) to stay concise.
    """
    lines = ["## FCV Glossary — Key Term Definitions\n"]
    for key, entry in FCV_GLOSSARY.items():
        lines.append(f"**{entry['term']}:** {entry['definition']}\n")
    return '\n'.join(lines)
```

- [ ] **Step 3: Add /api/glossary endpoint**

Add after the `/api/default-prompts` route (after line ~1702):

```python
@app.route('/api/glossary', methods=['GET'])
def get_glossary():
    """Return the FCV glossary as JSON for frontend tooltips."""
    return jsonify(FCV_GLOSSARY)
```

- [ ] **Step 4: Verify the app starts without errors**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "from app import app, get_instrument_slice, get_glossary_for_prompt; print(get_instrument_slice('IPF')[:200]); print('---'); print(get_glossary_for_prompt()[:200])"`

Expected: First 200 chars of the IPF instrument slice and first 200 chars of the glossary prompt text.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat: add instrument slice and glossary helper functions"
```

---

### Task 6: Add WB_PROCESS_GUIDE stub for future Phase 4

**Files:**
- Modify: `background_docs.py` (append after FCV_GLOSSARY)

This is a minimal stub that Phase 4 will flesh out. Including it now so the import and data structure are established.

- [ ] **Step 1: Add the stub constant**

Add after the `FCV_GLOSSARY` closing brace:

```python
# ─────────────────────────────────────────────────────────────────────────────
# 11. WB_PROCESS_GUIDE — Implementation process knowledge (stub for Phase 4)
# Last verified: 2026-04
# Review trigger: To be populated with MTR/ISR/AF/Restructuring/ICR process knowledge
# ─────────────────────────────────────────────────────────────────────────────

WB_PROCESS_GUIDE = {
    "MTR": {
        "purpose": "Mid-Term Review — assesses project performance at midpoint and recommends adjustments.",
        "scope": "To be expanded with detailed process knowledge in Phase 4.",
        "fcv_considerations": "To be expanded.",
    },
    "ISR": {
        "purpose": "Implementation Status and Results Report — periodic progress assessment.",
        "scope": "To be expanded.",
        "fcv_considerations": "To be expanded.",
    },
    "AF": {
        "purpose": "Additional Financing — scales up or addresses gaps in existing projects.",
        "scope": "To be expanded.",
        "fcv_considerations": "To be expanded.",
    },
    "Restructuring": {
        "purpose": "Restructuring Paper — modifies project design during implementation.",
        "scope": "To be expanded.",
        "fcv_considerations": "To be expanded.",
    },
    "ICR": {
        "purpose": "Implementation Completion Report — assesses project results at closing.",
        "scope": "To be expanded.",
        "fcv_considerations": "To be expanded.",
    },
}
```

- [ ] **Step 2: Update app.py imports to include WB_PROCESS_GUIDE**

Find the import line updated in Task 5:
```python
    WB_INSTRUMENT_GUIDE, FCV_GLOSSARY
```

Replace with:
```python
    WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, WB_PROCESS_GUIDE
```

- [ ] **Step 3: Verify imports**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "from app import WB_PROCESS_GUIDE; print(list(WB_PROCESS_GUIDE.keys()))"`

Expected: `['MTR', 'ISR', 'AF', 'Restructuring', 'ICR']`

- [ ] **Step 4: Commit**

```bash
git add background_docs.py app.py
git commit -m "feat: add WB_PROCESS_GUIDE stub for Phase 4"
```

---

### Task 7: Date-stamp all constants and add maintenance headers

**Files:**
- Modify: `background_docs.py` — add date-stamp headers to all existing constants

- [ ] **Step 1: Add date-stamp headers to existing constants**

Add a verification header comment before each existing constant. Before the `FCV_GUIDE` definition (line 6-8), update the comment:

Find:
```python
# ─────────────────────────────────────────────────────────────────────────────
# 1. FCV_GUIDE — Core FCV framework and screening questions (~3,000 tokens)
# ─────────────────────────────────────────────────────────────────────────────
```

Replace with:
```python
# ─────────────────────────────────────────────────────────────────────────────
# 1. FCV_GUIDE — Core FCV framework and screening questions (~3,000 tokens)
# Last verified: 2026-04
# Policy-sensitive: FCV Refresh shifts (Jan 2026), FCV country classification
# ─────────────────────────────────────────────────────────────────────────────
```

Repeat this pattern for constants 2-8, adding `# Last verified: 2026-04` and relevant `# Policy-sensitive:` notes to each:

- Constant 2 (FCV_OPERATIONAL_MANUAL): `# Policy-sensitive: 12 OST recommendations, 25 key questions, operational flexibilities`
- Constant 3 (FCV_REFRESH_FRAMEWORK): `# Policy-sensitive: 4 strategic shifts, FCV country classification scheme`
- Constant 4 (PLAYBOOK_DIAGNOSTICS): `# Policy-sensitive: RRA methodology, data sources`
- Constant 5 (PLAYBOOK_PREPARATION): `# Policy-sensitive: Para 12, ESF (post-Oct 2018), procurement framework`
- Constant 6 (PLAYBOOK_IMPLEMENTATION): `# Policy-sensitive: Para 12, ESF, TPM, GEMS`
- Constant 7 (PLAYBOOK_CLOSING): `# Policy-sensitive: ICR methodology, impact evaluation guidance`
- Constant 8 (STAGE_GUIDANCE_MAP): `# Policy-sensitive: Document type classifications, stage-specific flexibilities`

- [ ] **Step 2: Verify file is valid**

Run: `cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT" && python -c "import background_docs; print('All constants loaded OK')"`

Expected: `All constants loaded OK`

- [ ] **Step 3: Commit**

```bash
git add background_docs.py
git commit -m "docs: add date-stamp and policy-sensitivity headers to all background constants"
```

---

## Summary

After completing all 7 tasks, the knowledge base is established:

| Constant | Status | Token estimate |
|---|---|---|
| WB_INSTRUMENT_GUIDE (IPF, PforR, DPO, TA) | New | ~8,000 total, ~2,000 per slice |
| FCV_GLOSSARY (15 terms) | New | ~2,000 total |
| WB_PROCESS_GUIDE (5 processes) | Stub | ~500 (to be expanded in Phase 4) |
| Existing constants (broadened) | Updated | ~500 net increase |
| Date-stamp headers | Updated | ~0 (comments only) |

**Phase 2 (Prompt Changes)** can now consume these constants via `get_instrument_slice()` and `get_glossary_for_prompt()`.

**User action required before Phase 2:** Review the WB_INSTRUMENT_GUIDE entries (especially IPF and DPO) for accuracy and completeness. Identify gaps that need supplementation from internal sources. This is step 4 of the 5-step sourcing strategy from the spec.
