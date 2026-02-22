import os
import json
import base64
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
import anthropic

app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB upload limit

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

Now analyze the uploaded project document(s) and produce this structured extraction."""

PROMPT_2 = """# Role
You are an FCV specialist conducting systematic screening analysis for World Bank projects using the FCV Lens framework.

# Task
Using the information extracted in Stage 1, analyze this project across six FCV dimensions. Assess both **risks TO the project** (how FCV context threatens success) and **risks FROM the project** (how project actions might exacerbate conflict/fragility).

For each dimension below, provide:
1. **Risk Assessment:** High/Medium/Low/Not Applicable (with rationale)
2. **Risk TO Project:** How FCV context threatens project delivery
3. **Risk FROM Project:** How project could worsen FCV dynamics

## **Dimension 1: Institutional Legitimacy and Capacity**
## **Dimension 2: Inclusion and Non-Discrimination**
## **Dimension 3: Social Cohesion and Reconciliation**
## **Dimension 4: Security and Rule of Law**
## **Dimension 5: Economic Opportunities and Livelihoods**
## **Dimension 6: Resilience to Shocks and Crises**

End with a Summary Risk Matrix table showing Risk TO Project / Risk FROM Project / Overall Priority (H/M/L/NA) for each dimension.

Quality Guidelines:
- Evidence-based: ground assessments in Stage 1 extraction
- Balanced: consider both positive and negative implications
- Honest about gaps: note where information is insufficient

Now produce this six-dimension analysis."""

PROMPT_3 = """# Role
You are an FCV risk mitigation specialist reviewing project design adequacy.

# Task
Based on the FCV dimension analysis (Stage 2), identify:
1. **Critical gaps** in current project design or documentation (Analytical, Design, and Implementation gaps)
2. **Mitigation measures** for each HIGH risk dimension (Risk Addressed / Mitigation Measure / Responsible Actor / Timeline / Resource Implications)
3. **Do No Harm Checklist** — assess each principle: Non-discrimination in targeting, Conflict-sensitive site selection, Inclusive consultation, Grievance redress, Conflict impact monitoring, Adaptive management
4. **Enhancement Opportunities** — ways the project could actively support peacebuilding beyond do-no-harm
5. **Priority Mitigation Actions** (Top 5) and an **Overall FCV Integration Rating** (Strong/Adequate/Weak/Absent)

Quality Guidelines:
- Actionability: recommendations must be specific and feasible
- Proportionality: match mitigation intensity to risk severity
- Sector-sensitivity: tailor to the actual sector

Now produce this gap analysis and mitigation framework."""

PROMPT_4 = """# Role and Context
You are a senior FCV specialist providing collegial technical input to a World Bank Task Team Leader (TTL). Your tone should be supportive, consultative, and operationally focused — like a trusted peer reviewer.

This is NOT an audit. Write like a thoughtful colleague's memo.

# Document Structure to follow:

## PREAMBLE (50-75 words)
Explain this is an LLM-based FCV review pilot, its purpose, and that it is collegial input not a prescriptive mandate.

## 1. EXECUTIVE SUMMARY

**A. Opening Assessment** — ONE bolded sentence, 25-35 words, summarising overall FCV integration status.

**B. Current Strengths and Gaps** — Two paragraphs (180-250 words total):
- Paragraph 1 (Strengths, 80-120 words): 3-4 concrete strengths in flowing prose
- Paragraph 2 (The Gap, 100-130 words): Main weakness, constructively framed

**C. Operational Context** (150-200 words, one paragraph): 3-4 converging FCV risks creating a uniquely challenging environment. Use forward-looking framing for any post-preparation events ("In hindsight..." or "Looking ahead...").

**D. Strategic Priorities for Preparation** (4-5 priorities, 120-150 words each):
Each priority needs: the gap, why it matters operationally, suggested approach, optional italicised illustrative text, portfolio insights where relevant.
Use consultative language: "Consider...", "The team may want to...", "Would benefit from..."
NO multi-part numbered recommendations. NO specific percentages or dollar amounts.

## 2. TECHNICAL ANNEX (1,200-1,500 words total)
3-4 thematic pillars based on actual risks. For each pillar (300-400 words), present 2-3 risks:

**Risk [X]: [Title]** (30-45 words description)
Options to Consider:
□ Option 1 (35-50 words)
□ Option 2 (35-50 words)

# Citation format: [Document Name Year] — NEVER cite the PCN/PAD being reviewed.
# Total document: 3,500-3,800 words maximum.
# All content must be specific to THIS project — not generic template language.

Now produce the FCV Support Note."""


def get_prompt_for_stage(stage):
    return {1: PROMPT_1, 2: PROMPT_2, 3: PROMPT_3, 4: PROMPT_4}.get(stage)

def get_stage_name(stage):
    return {
        1: "Stage 1: FCV Risk Identification",
        2: "Stage 2: Six-Dimension Analysis",
        3: "Stage 3: Gaps & Mitigation Measures",
        4: "Stage 4: FCV Support Note"
    }.get(stage, f"Stage {stage}")


@app.route('/')
def index():
    # Serve index.html — check multiple locations
    base = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(base, 'static')
    if os.path.exists(os.path.join(static_path, 'index.html')):
        return send_from_directory(static_path, 'index.html')
    return send_from_directory(base, 'index.html')


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/run-stage', methods=['POST'])
def run_stage():
    """Run a stage with streaming. Accepts JSON to avoid Render's multipart size limits."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request — expected JSON.'}), 400

        stage = int(data.get('stage', 1))
        conversation_history = data.get('history', [])
        user_message = data.get('user_message', '').strip()

        messages = list(conversation_history)

        if stage == 1:
            documents = data.get('documents', [])
            if not documents:
                return jsonify({'error': 'Please upload at least one project document.'}), 400

            content_parts = []
            for doc in documents:
                name = doc.get('name', 'document')
                file_type = doc.get('type', 'text')
                content = doc.get('content', '')

                if file_type == 'pdf':
                    content_parts.append({
                        "type": "document",
                        "source": {"type": "base64", "media_type": "application/pdf", "data": content}
                    })
                else:
                    content_parts.append({"type": "text", "text": f"--- Document: {name} ---\n\n{content}"})

            content_parts.append({"type": "text", "text": get_prompt_for_stage(1)})
            messages.append({"role": "user", "content": content_parts})

        elif user_message:
            messages.append({"role": "user", "content": user_message})
        else:
            messages.append({"role": "user", "content": get_prompt_for_stage(stage)})

        def generate():
            collected = []
            try:
                # Send immediate keepalive so Render doesn't drop the connection
                yield f"data: {json.dumps({'ping': True})}\n\n"

                with client.messages.stream(
                    model="claude-sonnet-4-6",
                    max_tokens=8192,
                    messages=messages
                ) as stream:
                    for text_chunk in stream.text_stream:
                        collected.append(text_chunk)
                        # Send each chunk as a server-sent event
                        yield f"data: {json.dumps({'chunk': text_chunk})}\n\n"

                full_text = ''.join(collected)
                updated_messages = messages + [{"role": "assistant", "content": full_text}]
                if len(updated_messages) > 20:
                    updated_messages = updated_messages[-20:]

                # Send final event with full history
                yield f"data: {json.dumps({'done': True, 'result': full_text, 'history': updated_messages, 'stage': stage, 'stage_name': get_stage_name(stage)})}\n\n"

            except anthropic.AuthenticationError:
                yield f"data: {json.dumps({'error': 'Invalid API key.'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream',
                        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
