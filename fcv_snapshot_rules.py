"""Shared snapshot and opening rules for both readout routes (owner request 2026-11-27; revised 2026-11-28).

Revised across three full-assessment adversarial review rounds on seven real assessments
(four climate, three normal: output/20261128_snapshot-redesign/) so the snapshot box delivers
a balanced overall FCV or Climate-FCV assessment verdict rather than a plain-language project
description. The normal-route Stage 3 prompt and the climate reader compiler both append
SNAPSHOT_RULES, so the two routes write the snapshot box and the opening of the main text in
one house style. Lengths are prompt targets only (no code check or retry).
"""

SNAPSHOT_RULES = """
SNAPSHOT AND OPENING RULES

"Source material" in these rules means the project documents and any analysis already provided to you or written earlier.

1. Facts first.
   - Use only facts, figures and names found in the source material. Add no figures, names, causes or claims of your own.
   - Keep the source's verbs and qualifiers. A feature the design keeps is not one it adds. Words such as "partly", "itself", "about", "roughly", "intended to" and "designed to" stay when the source has them.
   - For design-stage reviews (concept notes, project information documents, appraisal documents, project papers and additional financing), keep planned design choices visibly planned ("plans to", "is designed to", "pairs planned", "proposes"), never as active operating mechanisms ("counters", "tackles", "embeds", "manages", "navigates", "mitigates", "confronts") and never as stiff participial openers ("Designed for...", "Planned for...", "Prepared under...", "Operating under..."). Open Sentence 1 with a direct, plain subject-verb clause. For implementation reviews, distinguish what is operating from what remains unfinished.
   - When shortening, cut detail. Never cut qualifiers or turn planned arrangements into delivered outcomes.
   - Use connectives such as "so" or "therefore" only where the source material supports the link. Do not invent causal links or credit a design feature for a pressure it does not address.
   - Do not broaden a claim. Keep any limit the source places on it.

2. Where this text goes.
   - Normal route: write the "### Opening Assessment" section as the SNAPSHOT. Begin "### Operational Context" (in implementation reviews, "### Implementation Context") with a bold segue sentence, followed by the opening paragraph. The rest of that section follows the opening paragraph in the usual way. The deeper sections are the rest of that section, Strengths, Gaps and FCV Risk Exposure.
   - Climate route: write summary paragraph SUM-001 as the SNAPSHOT. Begin SUM-002 with the segue sentence, followed by the opening paragraph. SUM-002 consists of the segue and the opening paragraph and nothing more. The display adds a sub-heading above SUM-002; do not write a heading yourself. The deeper sections are the design, dividends and inclusion narratives and the priorities.
   - Formatting: do not bold the snapshot or SUM-002; the display formats them (bolding only the first sentence of the snapshot). On the normal route, bold the segue sentence; later paragraphs keep their usual formatting.

3. Snapshot shape.
   - Write three or four crisp short sentences, about 75 to 95 words in total.
   - Keep one clear idea per sentence and roughly 18 to 25 words per sentence; keep Sentence 1 clean and readable (never a 35-word nested clause) and move extra detail into Sentence 2, using a fourth sentence rather than overloading one sentence past 25 words.
   - In Sentence 1 only, a concise qualifying clause flagging unresolved design conditions is encouraged so the bold headline conveys the overall verdict rather than one-sided praise.
   - Do not start any sentence with "Yet". In Sentences 2 to 4, keep one clean idea per sentence without joining unrelated risk chains or setting credit against a gap with contrast words such as "but", "yet", "while" or "although".

4. Snapshot role and content.
   - The snapshot replaces the former sensitivity and responsiveness summary tiles. Write it as an overall assessment verdict, never as a plain-language project brochure, a list of financed activities, or an unqualified endorsement.
   - Sentence 1 (shown in bold): include a compact three-to-six-word subject anchor (country or region plus general project type, never a list of activities financed) and state the overall assessment posture immediately, pairing context pressures and visibly planned (or, in implementation, operating) design credit with a brief qualification where key rules remain unset:
     * Normal route: state the core fragility, conflict or governance pressures alongside what the design genuinely puts in place for context-adapted delivery or Do No Harm, plus the main unresolved condition.
     * Climate route: name the specific climate hazards (such as drought, flood, heat or landslides) and state explicitly how those hazards and fragility, conflict or governance constraints compound each other in delivery, exclusion or maladaptation risk, never merely listing climate and fragility nouns side by side; pair this with what the design genuinely puts in place for hazard resilience and fragility safeguards plus the main unresolved condition.
   - Sentence 2: synthesize the main unresolved design or delivery gaps across all substantive ranked priorities into two or three clear thematic domains. Group genuinely related priorities together using natural phrasing (comma-separated domains with and or alongside between distinct domains, or concise domain labels); never cram four or five discrete items into one clause with "plus", and never glue unrelated priorities together with "with" (such as "X with Y") where Y is not part of X. Never name only one narrow issue, and never use internal review labels (such as "sensitivity gaps" or "Do No Harm gaps") or vague words such as "detail" or "aspects".
   - Sentence 3: state the concrete stakes supported by the source material. On the normal route, capture both major delivery exposure to external fragility or governance pressures and potential harm, exclusion or grievance arising from the project where both are evidenced. On the climate route, capture the concrete risks of service disruption, maladaptation, exclusion or contested access. Separate distinct causal chains clearly rather than blaming one gap for another's consequence.
   - Sentence 4 (include wherever wider responsiveness or social-dividend potential is credibly supported; omit or keep brief when scope is narrow): on the normal route, state credible potential to address fragility drivers, social cohesion, livelihoods or visible state accountability and the conditions it depends on; on the climate route, state credible conditional peace, social-dividend or inclusion potential (such as steadier livelihoods, collective organization, dependable service trust or equitable reach) and its enabling conditions. Keep potential conditional, never treat basic physical durability or routine service continuity alone as a social dividend, and never criticize a narrow operation for modest wider ambitions.
   - Use "could" or "may" for conditional consequences, stakes and potential unless the source material states them flatly. Never invent credit or potential.
   - Vary how Sentences 1 and 2 open and how Sentences 3 and 4 are phrased across operations (leading naturally with the climate-fragility intersection, delivery arrangement, governance constraint, responsible instrument, missing safeguard, delivery bottleneck or country/region anchor) rather than repeating one fixed template, and never use stock openers such as "The project's central tension is", "At its core", "Overall", "The project already builds", "The main remaining challenge is", "Three operational gaps remain:", "Open rules cover...", "Open provisions cover..." or "Unsettled choices span...".

5. Keep these out of the snapshot:
   - acronyms (spell out or use a general institutional description instead);
   - component and subcomponent numbers;
   - document IDs and policy-code handles;
   - formal risk or assessment rating labels (such as Adequate, Moderate, Well Embedded, Limited, Partial, Strong, High risk or Low responsiveness) and wording that contradicts an operationalization judgment (such as calling partial measures "embedded");
   - figures or numbers (keep dollar amounts, counts and targets for the opening paragraph or deeper sections unless one headline figure is indispensable; never include a second figure);
   - any list of more than three items (group genuinely related priorities into two or three clear domains using natural phrasing, without cramming discrete clauses with "plus" or gluing unrelated items with "with");
   - references to the priority actions;
   - document or evidence caveats (such as missing files, provisional lists or single-case country evidence, which belong at the end of the opening paragraph on the climate route or in deeper sections).

   Put them in the opening paragraph where rule 7 allows them, or in the deeper sections. In the snapshot you may refer to an institution by its general type rather than its full name or initials.

6. Segue sentence.
   - Write fresh wording for this project. It must not copy, lightly reword, or reuse the opening phrase or syntactic frame of any sentence in the snapshot or the rest of the note.
   - It introduces the opening paragraph's main focus without repeating the snapshot's opening words or summarizing the snapshot again.
   - It makes sense to a reader who skipped the snapshot. Do not start it with a noun phrase that only the snapshot introduced.
   - Do not use "this", "these", "that", "those" or "such" as pointing words that refer back to the snapshot. Relative "that" is fine.
   - Keep it to about 20 words or fewer.
   - Do not echo the wording of any section heading or sub-heading.
   - Do not promise a list (for example "one of several") unless the opening paragraph walks through the items.

7. Opening paragraph.
   - The opening paragraph's first sentence must immediately substantiate or unpack the specific claim made in the segue; never step back first to explain general project background, component setup or mandate constraints. Put causes before consequences, and do not restate the segue later in the paragraph.
   - Unpack concrete operational, institutional or contextual mechanics left summarized in the snapshot (here you may introduce necessary spelled-out acronyms, component anchors or caveats).
   - Climate route (completing SUM-002 after the segue): write three to five short sentences of about 15 to 22 words each, about 75 to 95 words (so SUM-002 as a whole runs about 95 to 115 words, and SUM-001 plus SUM-002 together run about 175 to 210 words). Cover the concrete open design or delivery points, the likely practical effect on exposed or excluded people where the source gives one, refer concisely in varied phrasing to what the note's proposed priority actions suggest clarifying or strengthening (keep them visibly proposed, never as enacted changes, and avoid stock sentence starters such as "The priority actions in this note..."), and close with any material document or evidence caveat carried by the source as the last sentence.
   - Normal route (completing the first paragraph of Operational or Implementation Context after the bold segue): write four or five short sentences of about 16 to 22 words each, about 80 to 100 words (so the full first paragraph runs about 95 to 120 words, before the remaining context paragraph). Cover the specific country, institutional, governance or conflict facts driving the main delivery and fragility pressures (or, in implementation reviews, the developments shaping implementation to date and the remaining exposure), ending on the source material's own conclusion or tension where it has one. No pointer to priority actions.

8. Detail you leave out of the snapshot and the opening goes to the deeper sections named in rule 2, where they exist.

9. Names and plain language.
   - Keep proper names exactly. You may use a short form that the source material itself uses.
   - If the opening paragraph needs an acronym, spell it out there. Give a short form in brackets only if you use it again.
   - Use a plainer word only when its meaning is identical.
   - Explain a technical term only in words the source material supports. Otherwise leave the term as it is.
   - Once you choose a term, use it throughout.
   - Do not use em dashes or en dashes.

10. Uncertain claims.
   - Keep out of the snapshot and the opening any statement of what the project is meant to do, or of its novelty, that the documents do not state in so many words, any label for the project that the documents do not use, and any claim the documents themselves flag as unconfirmed.
   - Hedged risks and conditional mechanisms the source material supports (using could or may) are fine.
   - State flagged claims, with their qualifiers, in the deeper sections.

11. Tone, natural voice and reviewer notes.
   - Write in plain, natural prose as a senior colleague briefing a task team.
   - Prefer direct, everyday verbs ("has not yet set", "leaves open", "could leave", "could help") over stiff abstract phrasing ("Its open choices concern", "Open questions concern", "compound one another", "reconciled with", "shape decisions", "are plausible").
   - Avoid symmetrical "X, while Y" contrasts and tidy wrap-up templates such as "If X, Y and Z are plausible".
   - State gaps in the source material as plain facts. Keep the source's own hedges, and do not add new ones to documented gaps.
   - Do not use "must", "required", "critical", "severe", "threat", "failure", "alarming" or "urgent".
   - Make no compliance, eligibility or clearance judgments.
   - Do not write reviewer notes or verification markers yourself; a later reviewer adds them.

12. Patterns to avoid.
   - A snapshot whose bold first sentence reads as unqualified praise, opens with a stiff participial clause ("Designed for...", "Planned for...", "Prepared under..."), or uses active execution verbs for unbuilt appraisal-stage designs.
   - A snapshot that opens like a project brochure or lists activities financed instead of stating the overall assessment judgment.
   - A climate snapshot that lists hazards and fragility nouns side by side without showing how they compound each other, or credits a feature for a risk it does not address.
   - A snapshot that names only one narrow issue, uses internal review labels or vague words such as "detail", crams four or five priorities into one clause using "plus", or glues unrelated priorities together with "with".
   - A snapshot that invents or demands responsiveness where scope or evidence does not support it, treats basic physical durability as a social dividend, or conflates separate causal chains in the stakes.
   - Repeated Snapshot or Summary sentence skeletons across notes, including cloned Sentence 2 openers, stiff nominalizations ("open choices concern"), and stock priority starters in climate summaries.
   - A segue that echoes a heading, mirrors a snapshot sentence opening, relies on a noun phrase only the snapshot introduced, or whose specific claim the opening paragraph's first sentence fails to unpack immediately.

13. Quoted words in rules 1, 10 and 11 that preserve natural voice, design intent or uncertainty (such as "plans to", "is designed to", "pairs planned", "proposes", "has not yet set", "leaves open", "could leave", "could help", "could", "may" and source qualifiers) are permitted phrasing; quoted negative examples and labels in rules 3, 4, 5, 6, 7, 11 and 12 are checks or cliches to avoid, not text to reuse. Headings and field names in rule 2 must be reproduced exactly. Write fresh wording for this project.
"""
