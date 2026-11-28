"""Shared snapshot and opening rules for both readout routes (owner request 2026-11-27).

Agreed by a writing editor and a critical reviewer over seven rounds on eight real examples
(output/20261127_snapshot-style-review/). The normal-route Stage 3 prompt and the climate reader
compiler both append SNAPSHOT_RULES, so the two routes write the snapshot box and the opening of the
main text in one house style. Code checks the lengths; the model is told the caps loosely.
"""

SNAPSHOT_RULES = """
SNAPSHOT AND OPENING RULES

"Source material" in these rules means the project documents and any analysis already provided to you or written earlier.

1. Facts first.
   - Use only facts, figures and names found in the source material. Add no figures, names, causes or claims of your own.
   - Keep the source's verbs and qualifiers. A feature the design keeps is not one it adds. Words such as "partly", "itself", "about" and "roughly" stay when the source has them.
   - When shortening, cut detail. Never cut qualifiers.
   - Use connectives such as "so" or "therefore" only where the source material supports the link. Do not invent causal links.
   - Do not say a feature addresses a hazard or risk that the source material does not link it to.
   - Do not broaden a claim. Keep any limit the source places on it.

2. Where this text goes.
   - Normal route: write the "### Opening Assessment" section as the SNAPSHOT. Begin "### Operational Context" with a bold segue sentence, followed by the opening paragraph. The rest of Operational Context follows the opening paragraph in the usual way. The deeper sections are the rest of Operational Context, Strengths, Gaps and FCV Risk Exposure.
   - Climate route: write summary paragraph SUM-001 as the SNAPSHOT. Begin SUM-002 with the segue sentence, followed by the opening paragraph. SUM-002 consists of the segue and the opening paragraph and nothing more. SUM-002 appears under the readout sub-heading "Main remaining risk". The deeper sections are the design, dividends and inclusion narratives and the priorities.
   - Formatting: do not bold the snapshot or SUM-002; the display formats them. On the normal route, bold only the segue sentence.

3. Snapshot shape.
   - Write two or three short sentences, no more than about 55 words in total.
   - Keep one idea per sentence and about 20 words or fewer per sentence.
   - Within one sentence, do not join credit to a problem or to the stakes with a contrast word such as "but", "yet", "while" or "although".
   - Do not start a sentence with "Yet".

4. Snapshot content.
   - In the first or second sentence, say where the project is and what it does, in the source material's own words.
   - State one main issue that is specific to this project, so a reader could repeat it in a line.
   - State the stakes once.
   - Where the source material credits the design, include one short credit clause. Never invent credit.
   - Put the issue, the credit and the stakes in whatever order reads most naturally for this project.
   - Vary how the first sentence opens. Lead with whatever subject fits: the place, a responsible body, the financing, an asset, the main pressure or the activity itself.
   - Never use stock openers such as "The project's central tension is", "At its core" or "Overall".

5. Keep these out of the snapshot:
   - acronyms;
   - component and subcomponent numbers;
   - document IDs;
   - risk ratings;
   - a second figure;
   - any list of more than three items;
   - references to the priority actions;
   - caveats.

   Put them in the opening paragraph where rule 7 allows them, or in the deeper sections. In the snapshot you may refer to a body by its general type rather than its full name.

6. Segue sentence.
   - Write it new for this note. It must not be a copy or light rewording of any other sentence in the note.
   - It introduces the first topic of the main text.
   - It links to a word or idea in the snapshot, without repeating the snapshot's opening words.
   - It makes sense to a reader who skipped the snapshot. Do not start it with a noun phrase that only the snapshot introduced.
   - Do not use "this", "these", "that", "those" or "such" as pointing words that refer back to the snapshot. Relative "that" is fine.
   - Keep it to about 20 words or fewer.
   - Climate route: do not repeat the sub-heading's wording.

7. Opening paragraph.
   - Write up to six short sentences, about 120 words at most.
   - The first sentence develops the segue's topic. If the segue opens a list, the first sentence gives the first item.
   - Put causes before consequences.
   - Do not restate the segue later in the paragraph.
   - Climate route order: the open points, the likely effect on people where the source material gives one, a pointer to the priority actions, and any caveat the source material carries as the last sentence.
   - Normal route order: the context facts that drive the main issue, ending on the source material's own conclusion where it has one. No pointer to priority actions.

8. Detail you leave out of the snapshot and the opening goes to the deeper sections named in rule 2, where they exist.

9. Names and plain language.
   - Keep proper names exactly. You may use a short form that the source material itself uses.
   - If the opening needs an acronym, spell it out there.
   - Use a plainer word only when its meaning is identical.
   - Explain a technical term only in words the source material supports. Otherwise leave the term as it is.
   - Once you choose a term, use it throughout.
   - Do not use em dashes or en dashes.

10. Uncertain claims.
   - Keep out of the snapshot and the opening any statement of the project's purpose, novelty or stakes that the documents do not state in so many words, any label for the project that the documents do not use, and any claim the documents themselves flag as unconfirmed.
   - Hedged risks the source material supports ("could", "may") are fine.
   - State flagged claims, with their qualifiers, in the deeper sections.

11. Tone and reviewer notes.
   - Write as a collegial peer reviewer.
   - State gaps in the source material as plain facts. Keep the source's own hedges, and do not add new ones to documented gaps.
   - Do not use "must", "required", "critical", "severe", "threat", "failure", "alarming" or "urgent".
   - Make no compliance, eligibility or clearance judgments.
   - Do not write reviewer notes or verification markers yourself; a later reviewer adds them.

12. Patterns to avoid.
   - A snapshot that states the same stakes twice in different words.
   - A sentence that sets credit against a problem with a contrast word.
   - A segue that relies on a noun phrase only the snapshot introduced. Name the idea in full instead.
   - A segue whose topic the opening paragraph does not take up in its first sentence.
   - The same first-sentence shape as a standard template, used regardless of the project.

13. Quoted phrases in rules 1, 3, 4, 5, 6, 11 and 12 are labels for checking or examples to avoid, not text to reuse. Qualifiers that rule 1 tells you to keep stay when the source has them. Headings and field names in rule 2 must be reproduced exactly. Write fresh wording for this project.
"""
