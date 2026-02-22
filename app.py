import os
import json
from flask import Flask, request, jsonify, send_from_directory
import anthropic

app = Flask(__name__, static_folder='static')

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ── Prompt definitions ──────────────────────────────────────────────────────

PROMPT_1 = """# Role
You are an expert FCV (Fragility, Conflict, and Violence) analyst for the World Bank Group, specializing in identifying conflict risks and development challenges in fragile contexts.

# Task
Analyze the provided project document(s) and extract ALL information related to FCV dimensions. Your goal is to create a comprehensive foundation for subsequent FCV screening analysis.

# Document Context
- **Project Stage:** [To be identified from document — PCN or PAD]
- **Sector(s):** [To be identified from document]
- **Country/Region:** [To be identified from document]

# Extraction Categories

## 1. Direct FCV References
Extract any explicit mentions of:
- Fragility, conflict, or violence
- Security concerns or conflict dynamics
- Post-conflict or crisis contexts
- Social cohesion challenges
- Displacement, refugees, or IDPs
- Organized crime, trafficking, or illicit activities

## 2. Implicit FCV Indicators
Identify contextual signals that suggest FCV relevance:
- Weak institutional capacity or governance challenges
- Social exclusion or marginalized groups
- Intercommunal tensions or grievances
- Resource competition or land disputes
- High unemployment, especially among youth
- Historical conflict or recent political instability

## 3. Project Design Elements
Note any project features that may interact with FCV dynamics:
- Beneficiary targeting and selection mechanisms
- Community engagement or participation approaches
- Infrastructure siting decisions
- Employment or livelihood components
- Grievance redress mechanisms
- Stakeholder consultation processes

## 4. Risk Assessments
Extract existing risk analysis:
- Environmental and social risks
- Political economy considerations
- Implementation risks
- Contextual risks mentioned in any section

## 5. Geographic Context
Identify location-specific information:
- Specific regions, provinces, or communities mentioned
- Urban vs. rural focus
- Border areas or contested territories
- Areas with known conflict history

# Output Format

Organize your findings using this structure:

### **Direct FCV References**
[Bulleted list of findings]

### **Implicit FCV Indicators**
[Bulleted list of findings]

### **Project Design Elements with FCV Implications**
[Bulleted list of findings]

### **Existing Risk Assessments**
[Bulleted list of findings]

### **Geographic and Contextual Details**
[Bulleted list of findings]

### **Data Gaps**
[Note any FCV-relevant information that appears missing or inadequately addressed]

# Quality Guidelines
- **Comprehensiveness:** Extract ALL potentially relevant information, even if marginal
- **Accuracy:** Quote or paraphrase precisely; do not infer beyond what's stated
- **Neutrality:** Present information objectively without premature analysis
- **Transparency:** Note when information is ambiguous or contradictory

# Data Security
This analysis is for internal World Bank Group use. Handle all documents according to "Official Use Only" protocols.

---

**Note:** This extraction provides the foundation for subsequent FCV screening analysis. Err on the side of inclusion — downstream prompts will assess relevance.

Now analyze the uploaded project document(s) and produce this structured extraction."""

PROMPT_2 = """# Role
You are an FCV specialist conducting systematic screening analysis for World Bank projects using the FCV Lens framework.

# Task
Using the information extracted in Stage 1, analyze this project across six FCV dimensions. Assess both **risks TO the project** (how FCV context threatens success) and **risks FROM the project** (how project actions might exacerbate conflict/fragility).

# Analysis Framework

For each dimension below, provide:
1. **Risk Assessment:** High/Medium/Low/Not Applicable (with rationale)
2. **Risk TO Project:** How FCV context threatens project delivery
3. **Risk FROM Project:** How project could worsen FCV dynamics
4. **Evidence Base:** Specific references to source documents

---

## **Dimension 1: Institutional Legitimacy and Capacity**
**Guiding Questions:**
- Does the project rely on institutions with limited capacity or contested legitimacy?
- Are there power imbalances among implementing partners?
- Could the project strengthen or undermine institutional credibility?
- Are there exclusionary governance practices?

**Analysis:** [Provide 150-250 word assessment]

---

## **Dimension 2: Inclusion and Non-Discrimination**
**Guiding Questions:**
- Who are the project beneficiaries, and who might be excluded?
- Are there marginalized groups (ethnic, religious, gender, youth, displaced)?
- Could targeting mechanisms create or reinforce divisions?
- Are consultation processes inclusive?

**Analysis:** [Provide 150-250 word assessment]

---

## **Dimension 3: Social Cohesion and Reconciliation**
**Guiding Questions:**
- Are there existing intercommunal tensions or historical grievances?
- Could project benefits be perceived as favoring one group over another?
- Does the project create opportunities for intergroup collaboration?
- Are there risks of elite capture or exclusion?

**Analysis:** [Provide 150-250 word assessment]

---

## **Dimension 4: Security and Rule of Law**
**Guiding Questions:**
- Are there active conflict dynamics or security threats in project areas?
- Could infrastructure or resources create security vulnerabilities?
- Are there risks from organized crime, trafficking, or armed groups?
- Does the project involve security sector engagement?

**Analysis:** [Provide 150-250 word assessment]

---

## **Dimension 5: Economic Opportunities and Livelihoods**
**Guiding Questions:**
- Does the project address unemployment or livelihood challenges?
- Could it create competition over resources or economic benefits?
- Are there risks of labor disputes or exploitation?
- Does it affect land access or resource rights?

**Analysis:** [Provide 150-250 word assessment]

---

## **Dimension 6: Resilience to Shocks and Crises**
**Guiding Questions:**
- Is the project area prone to climate shocks, displacement, or conflict flare-ups?
- Does the project enhance or reduce community resilience?
- Are there adaptive mechanisms for changing conflict dynamics?
- Could project infrastructure be vulnerable to destruction?

**Analysis:** [Provide 150-250 word assessment]

---

# Summary Risk Matrix

| Dimension | Risk TO Project | Risk FROM Project | Overall Priority |
|-----------|-----------------|-------------------|------------------|
| Institutional Legitimacy | [H/M/L/NA] | [H/M/L/NA] | [H/M/L] |
| Inclusion | [H/M/L/NA] | [H/M/L/NA] | [H/M/L] |
| Social Cohesion | [H/M/L/NA] | [H/M/L/NA] | [H/M/L] |
| Security | [H/M/L/NA] | [H/M/L/NA] | [H/M/L] |
| Economic Livelihoods | [H/M/L/NA] | [H/M/L/NA] | [H/M/L] |
| Resilience | [H/M/L/NA] | [H/M/L/NA] | [H/M/L] |

# Quality Guidelines
- **Evidence-based:** Ground assessments in extracted information from Stage 1
- **Balanced:** Consider both positive and negative implications
- **Contextual:** Account for sector and country-specific dynamics
- **Honest about gaps:** Note where information is insufficient for confident assessment

# PAD-Specific Note
For PAD-stage documents, expect more detailed risk analysis and mitigation measures. Assess whether existing ESRS/risk frameworks adequately address FCV dimensions.

Now produce this six-dimension analysis based on the Stage 1 extraction above."""

PROMPT_3 = """# Role
You are an FCV risk mitigation specialist reviewing project design adequacy.

# Task
Based on the FCV dimension analysis (Stage 2), identify:
1. **Critical gaps** in current project design or documentation
2. **Mitigation measures** needed to address identified FCV risks
3. **Enhancement opportunities** where project could actively contribute to peacebuilding/resilience

# Analysis Structure

## **Part A: Critical Gaps**

### **Gap Category 1: Analytical Gaps**
What FCV-relevant analysis is missing from project documents?
- Conflict analysis or political economy assessment
- Stakeholder mapping of conflict actors
- Gender and social inclusion analysis
- Grievance or tension mapping

**Identified Gaps:** [Bulleted list with specific recommendations]

---

### **Gap Category 2: Design Gaps**
What project design features are absent that could mitigate FCV risks?
- Conflict-sensitive beneficiary targeting
- Grievance redress mechanisms
- Adaptive management provisions
- Community engagement protocols
- Do No Harm safeguards

**Identified Gaps:** [Bulleted list with specific recommendations]

---

### **Gap Category 3: Implementation Gaps**
What operational capacities or mechanisms are needed?
- FCV expertise in PIU/implementing team
- Conflict monitoring systems
- Third-party monitoring in insecure areas
- Partnerships with peacebuilding actors

**Identified Gaps:** [Bulleted list with specific recommendations]

---

## **Part B: Recommended Mitigation Measures**

For each dimension with HIGH risk, propose specific, actionable mitigations using this template:

**Risk Addressed:** [Brief description]
**Mitigation Measure:** [Specific action]
**Responsible Actor:** [PIU/TTL/Government/Partner]
**Implementation Timeline:** [Design/Preparation/Implementation]
**Resource Implications:** [Minimal/Moderate/Significant]

---

## **Part C: Do No Harm Checklist**

| Do No Harm Principle | Addressed? | Evidence/Gap |
|----------------------|------------|--------------|
| Non-discrimination in targeting | [Yes/Partial/No] | [Brief note] |
| Conflict-sensitive site selection | [Yes/Partial/No] | [Brief note] |
| Inclusive consultation processes | [Yes/Partial/No] | [Brief note] |
| Grievance redress accessible to all | [Yes/Partial/No] | [Brief note] |
| Monitoring for unintended conflict impacts | [Yes/Partial/No] | [Brief note] |
| Adaptive management for changing context | [Yes/Partial/No] | [Brief note] |

---

## **Part D: Enhancement Opportunities**

Identify ways the project could go beyond "do no harm" to actively support peacebuilding.

**Recommended Enhancements:** [Bulleted list, prioritizing HIGH impact, FEASIBLE interventions]

---

# Output Summary

### **Priority Mitigation Actions** (Top 5)
1. [Action 1]
2. [Action 2]
3. [Action 3]
4. [Action 4]
5. [Action 5]

### **Overall Assessment**
**FCV Integration Rating:** [Strong/Adequate/Weak/Absent]
**Justification:** [2-3 sentences]

# Quality Guidelines
- **Actionability:** Recommendations must be specific and feasible
- **Proportionality:** Match mitigation intensity to risk severity
- **Practicality:** Consider implementation capacity and budget constraints
- **Sector-sensitivity:** Tailor recommendations to sector (infrastructure, health, education, etc.)

Now produce this gap analysis and mitigation framework based on the Stage 2 analysis above."""

PROMPT_4 = """# Role and Context
You are a senior FCV specialist providing collegial technical input to a World Bank Task Team Leader (TTL). Your purpose is to offer constructive guidance to strengthen the PCN or PAD's FCV integration before the Decision Meeting.

This is NOT an audit or compliance checklist. Your tone should be supportive, consultative, and operationally focused — like a trusted peer reviewer offering strategic options.

---

# CRITICAL INSTRUCTION: INDEPENDENT THINKING REQUIRED

The structure provided is a guide only. You MUST:
✅ Analyze the actual project documents and generate context-specific insights
✅ Tailor all content to the specific country, sector, and project characteristics
✅ Create original text based on the actual FCV risks identified in Stages 1-3
✅ Use your analytical judgment to prioritize what matters most for THIS project

❌ DO NOT use generic or placeholder language
❌ DO NOT reference details that don't apply to this specific project

---

# CRITICAL CONTEXTUAL AWARENESS

Always note when the PCN/PAD was prepared. Do not criticize the document for lacking information about events that occurred AFTER its preparation. For post-preparation events, frame as: "In hindsight..." or "Looking ahead to implementation..."

---

# Document Structure

## PREAMBLE (50-75 words)
A brief note explaining this is an LLM-based FCV review pilot, its purpose, and how it should be used. Adapt this template:
"This note provides FCV-focused technical input to support the task team in strengthening the PCN's conflict-sensitivity before the Decision Meeting. It is generated through an LLM-assisted review pilot that synthesizes the project document against [Country]'s formal FCV diagnostic and recent contextual analysis. It is intended as collegial input for team consideration, not a prescriptive mandate."

---

## 1. EXECUTIVE SUMMARY: THE TTL READ

### A. Opening Assessment (25-35 words, SINGLE SENTENCE, BOLD)
A one-sentence summary of the project's overall FCV integration status. This MUST be bold, one sentence, 25-35 words.

### B. Current Strengths and Gaps (180-250 words, TWO PARAGRAPHS)
**Paragraph 1 - Strengths (80-120 words):** 3-4 concrete strengths in flowing prose. Use 2-3 citations to external sources (never cite the PCN/PAD itself).
**Paragraph 2 - The Gap (100-130 words):** The main weakness, constructively framed. 1-2 citations maximum to external sources.

### C. The Operational Context (150-200 words, ONE PARAGRAPH)
Synthesize 3-4 critical converging FCV risks that create a uniquely challenging operating environment. Use forward-looking framing for post-preparation events.

### D. Strategic Priorities for Preparation (4-5 priorities, ~120-150 words each)
Numbered list with consultative, bolded titles. Each priority includes: the gap, why it matters operationally, suggested approach, optional illustrative text (italics), and portfolio insights where relevant.

Requirements:
- NO multi-part numbered recommendations
- NO specific percentages, dollar amounts, or hiring targets
- Use consultative language: "Consider...", "The team may want to...", "Would benefit from..."
- 1-2 citations per priority maximum, never citing the PCN/PAD

---

## 2. TECHNICAL ANNEX: DETAILED RISK ANALYSIS & OPTIONS (1,200-1,500 words total)

Organize under 3-4 thematic pillars based on actual FCV risks identified. For each pillar (300-400 words):

**PILLAR [A/B/C]: [DESCRIPTIVE PILLAR NAME]**

For 2-3 risks per pillar:

**Risk [A1/A2]: [Risk Title]** (30-45 words)
[Description: what the risk is, why it matters, current gap. 0-1 citation, never cite PCN/PAD.]

Options to Consider:
□ [Option 1: 35-50 words, focused on what to strengthen in the PCN]
□ [Option 2: 35-50 words, if applicable]

---

# CITATION FORMAT
Format: [Document Name Year] — e.g., [Honduras RRA 2022]
NEVER cite the PCN or PAD being reviewed.
Keep citations sparse and naturally integrated.

---

# TONE & STYLE
- Conversational, flowing prose
- High-level and strategic (not prescriptive implementation protocols)
- Consultative language throughout
- Total document: 3,500-3,800 words maximum

---

# WORD COUNT TARGETS
| Section | Target |
|---------|--------|
| Preamble | 50-75 words |
| Opening Assessment | 25-35 words (1 sentence) |
| Strengths and Gaps | 180-250 words |
| Operational Context | 150-200 words |
| Strategic Priorities | 480-750 words total |
| Technical Annex | 1,200-1,500 words |
| **TOTAL** | **3,500-3,800 words** |

---

Now produce the FCV Support Note following this exact structure, with content fully tailored to the specific project analyzed in Stages 1-3."""


def get_prompt_for_stage(stage):
    prompts = {1: PROMPT_1, 2: PROMPT_2, 3: PROMPT_3, 4: PROMPT_4}
    return prompts.get(stage)


def get_stage_name(stage):
    names = {
        1: "Stage 1: FCV Risk Identification",
        2: "Stage 2: Six-Dimension Analysis",
        3: "Stage 3: Gaps & Mitigation Measures",
        4: "Stage 4: FCV Support Note"
    }
    return names.get(stage, f"Stage {stage}")


@app.route('/')
def index():
    if os.path.exists(os.path.join('static', 'index.html')):
        return send_from_directory('static', 'index.html')
    return send_from_directory('.', 'index.html')


@app.route('/api/run-stage', methods=['POST'])
def run_stage():
    """Run a specific stage of the FCV analysis."""
    try:
        stage = int(request.form.get('stage', 1))
        conversation_history = json.loads(request.form.get('history', '[]'))
        user_message = request.form.get('user_message', '').strip()

        # Build messages array
        messages = list(conversation_history)

        if stage == 1:
            # First stage: include uploaded documents
            files = request.files.getlist('documents')
            if not files or all(f.filename == '' for f in files):
                return jsonify({'error': 'Please upload at least one project document.'}), 400

            content_parts = []

            for f in files:
                if f.filename == '':
                    continue
                file_bytes = f.read()
                filename = f.filename.lower()

                if filename.endswith('.pdf'):
                    import base64
                    b64 = base64.standard_b64encode(file_bytes).decode('utf-8')
                    content_parts.append({
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": b64
                        }
                    })
                else:
                    # Try to decode as text
                    try:
                        text = file_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            text = file_bytes.decode('latin-1')
                        except Exception:
                            text = f"[Could not decode file: {f.filename}]"
                    content_parts.append({
                        "type": "text",
                        "text": f"--- Document: {f.filename} ---\n\n{text}"
                    })

            content_parts.append({
                "type": "text",
                "text": get_prompt_for_stage(1)
            })

            messages.append({"role": "user", "content": content_parts})

        elif user_message:
            # Follow-on query within a stage
            messages.append({"role": "user", "content": user_message})

        else:
            # Advancing to next stage
            stage_prompt = get_prompt_for_stage(stage)
            messages.append({"role": "user", "content": stage_prompt})

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=8192,
            messages=messages
        )

        assistant_text = response.content[0].text

        # Return updated history (append assistant response)
        messages.append({"role": "assistant", "content": assistant_text})

        # Trim history to avoid context overflow — keep last 20 messages
        if len(messages) > 20:
            messages = messages[-20:]

        return jsonify({
            'result': assistant_text,
            'history': messages,
            'stage': stage,
            'stage_name': get_stage_name(stage)
        })

    except anthropic.AuthenticationError:
        return jsonify({'error': 'Invalid API key. Please check your ANTHROPIC_API_KEY environment variable.'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
