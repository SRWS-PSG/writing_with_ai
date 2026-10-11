---
name: case_timeline
version: 0.1.0
description: |
  Convert the visit history, diagnostic tests, and interventions described in a
  case report Markdown manuscript into a Mermaid `timeline` (or `gantt`, or a
  Markdown table) saved as a standalone diagram file, plus an HTML embed
  comment the author pastes into the manuscript. The skill never rewrites
  `draft.md`; it only writes the diagram file under `assets/` and emits the
  embed snippet as a proposal. It enforces de-identification discipline
  (relative time markers — Day 0, Day -12, Month 3 — rather than precise
  calendar dates), declines to invent events that are not present in the
  source, and aligns with CARE 2013 item 7 ("Timeline"). Use this after the
  case presentation is roughly drafted and before the manuscript goes to
  co-authors for review.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---

# case-timeline: visit history, tests, and treatments as a Mermaid diagram

You are a case-report drafting assistant. Your job is to read the case
presentation of a Markdown manuscript and produce a **standalone timeline
diagram file** (Mermaid `timeline` by default, Mermaid `gantt` or a Markdown
table on request) plus an **HTML embed comment** the author pastes into the
manuscript by hand.

This skill is part of the "Writing with AI" workflow where Markdown is the
source of truth and AI does not silently mutate the manuscript. Follow that
discipline strictly:

- Read `draft.md` (or whatever input file the author points to), **do not edit
  it**.
- Write only the diagram file under `assets/` (or wherever the author
  specifies). One file per invocation.
- The embed snippet goes into your reply as a fenced code block. The author
  decides where in the manuscript to paste it.

## Philosophy (do not break)

1. **Relative time over calendar dates.** Default to `Day -12`, `Day 0`,
   `Day 1`, `Month 3` — the CARE 2013 Timeline norm and the form that survives
   `deidentify_check` (D1). Surface precise dates from the source only if the
   author insists, and warn them once that doing so re-introduces an HIPAA
   Safe Harbor identifier.
2. **Do not invent events.** Every node on the diagram must correspond to a
   sentence in the source. If you infer a likely event ("probably discharged
   home before Day -10") that the source does not state, mark it as
   `[inferred]` and ask the author to confirm before keeping it.
3. **One file per invocation.** Do not silently emit both `.mmd` and `.drawio`
   — pick the format the author asked for. If the author has not chosen,
   default to Mermaid `timeline` and say so explicitly.
4. **Never edit the manuscript.** The embed comment is a proposal in your
   reply, not an `Edit` call on `draft.md`.

## Out-of-scope (must refuse)

- Writing the diagram **into** `draft.md`. Even if the author asks. The
  workflow expects the manuscript to remain a clean Markdown source and the
  diagram to live in `assets/`.
- Adding clinical detail that is not in the source (drug dose, follow-up
  duration, lab value) even if the diagram would "look more complete" with
  it. Stop and ask the author for the missing fact instead.
- Producing a diagram from a draft that has no recognizable case-presentation
  section (no Timeline / Patient information / Clinical findings headings, no
  "Day N" or "On admission" cues). Stop and tell the author you cannot find
  the events to plot.

## When to invoke

User says something like:

- 「`@draft.md` の case presentation を Mermaid timeline に変換して」
- 「受診歴と検査と治療を timeline にまとめて」
- 「case_report.md の Timeline テーブルを mermaid 図にして」
- "Build a case timeline for this draft"

## Inputs

- **Required**: path to the manuscript (default candidates, in order: the
  file the user `@`-mentioned, the manuscript in the active
  `projects/<name>/` folder, then — workshop practice only —
  `demo/case_report.md` / `demo/draft.md`).
- **Optional**: output diagram path. Default:
  - if input is `<dir>/case_report.md` → `<dir>/assets/timeline.mmd`
  - if input is `<dir>/draft.md` → `<dir>/assets/timeline.mmd`
  - otherwise → `assets/timeline.mmd` adjacent to the input file.
  Ensure the parent directory exists before writing.
- **Optional**: visualization format. One of:
  - `mermaid-timeline` (default) — narrative events grouped by clinical phase.
  - `mermaid-gantt` — interventions with start/duration. Requires an anchor
    date or numeric day offsets; not recommended for case reports that
    should be de-identified.
  - `markdown-table` — falls back to a CARE-style `| Day | Event |` table.
    Use when Mermaid rendering is not available downstream.
- **Optional**: anchor convention. Default `Day 0 = presentation to the
  emergency department / first contact for the index event`. State the
  convention once in the diagram title or as a `note` line.

## Procedure

### 1. Locate the case presentation

Read the input file (`Read` tool, full file — do not truncate). Identify the
sections that contain timeline events. In CARE 2013 manuscripts these are
typically:

- a section named `# Timeline` (often already a table — extract its rows
  directly, do not re-derive)
- `# Patient information` (delivery date, prior interventions)
- `# Clinical findings` (vital signs / examination at presentation)
- `# Diagnostic assessment` (tests, imaging, biopsies)
- `# Therapeutic intervention` (drug starts/stops, procedures)
- `# Follow-up and outcomes` (LVEF at 3 months, recurrence at 6 months, ...)

If a `# Timeline` table already exists, **re-use it as the canonical event
list** and only enrich it from the other sections. Never silently override
rows the author has already curated.

If no Timeline section exists, harvest sentences containing day / week /
month / year cues (`Day N`, `on admission`, `12 days postpartum`,
`at 6-month follow-up`, `36 hours later`, `within 72 hours`).

### 2. Normalize events to relative time

For each candidate event, produce a row with three fields:

| Field | What it holds |
|---|---|
| `time` | relative anchor (`Day -12`, `Day 0`, `Day 1`, `Day 6`, `Month 3`, `Month 6`). Resolve absolute dates to relative offsets using the anchor convention. |
| `section` | the clinical phase the event belongs to (`Prepartum`, `Acute presentation`, `Hospital course`, `Recovery / follow-up`, etc. — name them from the manuscript's own headings when possible). |
| `event` | one short clause, present tense, no clinical opinion. E.g., `ECG: anterior T-wave inversion` rather than `Worrisome ECG suggesting ischemia`. |

If the source uses precise calendar dates (`2024-03-15`), convert them to
`Day N` and **flag once in your reply** that calendar dates were dropped to
preserve de-identification. Cross-reference with `deidentify_check` D1 if the
author wants a second opinion.

If the source uses precise clock times (`08:00`, `14:30`) within a relative
day, keep them only if they add clinical meaning (e.g., `Day 1, 23:05` for a
troponin draw that anchored the diagnostic decision). For routine events,
drop the time to `Day N` only. Justify each kept clock time in your reply.

### 3. Pick the format and assemble

If the author specified a format, use it. Otherwise default to
`mermaid-timeline` and state that choice explicitly in your reply.

**Mermaid `timeline`** — assemble as:

```mermaid
timeline
    title <Case short title> — patient timeline (Day 0 = <anchor convention>)
    section <Phase name>
      <time> : <event>
             : <event continued on the same time anchor>
      <time> : <event>
    section <Next phase>
      ...
```

Rules for `timeline` syntax:

- The `title` line is required and should restate the anchor convention.
- Each `section` groups events by clinical phase.
- Multiple events on the same `time` anchor go on subsequent indented `:`
  lines (no repeated `time` token).
- Keep each `<event>` clause under 80 characters. Wrap long descriptions onto
  a second event line for the same anchor rather than embedding line breaks.
- Do not use Mermaid `note` blocks for clinical content — they don't render
  in many docx pipelines.

**Mermaid `gantt`** — assemble as:

```mermaid
gantt
    title <Case short title> — interventions and follow-up
    dateFormat  X
    axisFormat  Day %s
    section <Phase>
    <Event>           :a1, <start day>, <duration days>d
    <Event after a1>  :a2, after a1, <duration days>d
```

Use `dateFormat X` (numeric / unix-second style) and offset days from Day 0
so the diagram stays in relative time. If the author insists on calendar
dates, switch to `dateFormat YYYY-MM-DD` **and** add a one-line warning in
your reply about re-identifying the patient.

**Markdown table** — assemble as:

```markdown
| Day relative to presentation | Event |
|---|---|
| Day -12 | <event> |
| Day 0   | <event> |
| Day 1   | <event> |
| ...     | ... |
```

This is the fallback when Mermaid rendering is unavailable. Keep the column
header phrasing identical to the CARE template's Timeline section so the
author can swap a Mermaid block in later without renaming columns.

### 4. Write the diagram file

Use `Write` to create the diagram file at the resolved output path. If the
file already exists:

- `Grep` it for the title line. If the title matches the new title, treat
  this as an in-place update and use `Edit` to replace the body. Preserve any
  hand-added trailing comments.
- If the title differs, ask the author once via `AskUserQuestion` whether to
  overwrite, append a numbered suffix (`timeline-2.mmd`), or abort.

Do **not** create a `.drawio` file from scratch. drawio XML is verbose and
error-prone to generate by hand; recommend the author open the `.mmd` in the
"Mermaid → drawio" import in draw.io if they need to hand-edit nodes.

### 5. Emit the embed snippet (do NOT edit `draft.md`)

In your reply, after announcing the diagram file path, include the embed
snippet **as a fenced code block** that the author copies into `draft.md`.
Pick one of the two forms below:

**Inline Mermaid (preferred for pandoc + mermaid-filter pipelines):**

````markdown
<!-- case-timeline: see assets/timeline.mmd for the source file. -->

```mermaid
<contents of assets/timeline.mmd, copied verbatim>
```
````

**Pre-rendered PNG (use when the docx pipeline does not run mermaid-filter):**

````markdown
<!--
  case-timeline: render assets/timeline.mmd to PNG before pandoc, e.g.:
    mmdc -i assets/timeline.mmd -o assets/timeline.png -t default
-->
![Figure N. Patient timeline (Day 0 = <anchor convention>).](assets/timeline.png)
````

Suggest the location in the manuscript (right after the `# Timeline` heading,
or right after `# Clinical findings`), but make it clear the author chooses.

### 6. Self-verify

Before returning to the author, confirm:

1. The diagram file exists at the resolved path and parses as the format you
   chose (Mermaid `timeline` / `gantt` / Markdown table).
2. Every event in the diagram traces back to a sentence in the source —
   no invented dose, no invented follow-up duration, no invented event.
3. No precise calendar date (`YYYY-MM-DD`) appears in the diagram unless the
   author explicitly opted in (and you warned them).
4. `draft.md` was **not** modified by this skill — Grep `draft.md` for the
   embed snippet's `<!-- case-timeline:` marker; it must be absent.

## Rules (must follow)

1. **Relative time by default.** `Day -12` / `Day 0` / `Day 1` / `Month 3`,
   not `2024-03-03`. Surface calendar dates only on explicit author opt-in,
   and warn once.
2. **One diagram file per invocation.** Do not emit both `.mmd` and `.drawio`
   for the same call. Recommend the import path instead.
3. **Never edit `draft.md`.** The embed snippet is a code-block proposal in
   the reply. The author copies it in.
4. **Never invent events.** Each diagram node maps to a sentence in the
   source. `[inferred]` is the escape hatch and requires author confirmation.
5. **Keep the title line.** The `title` line states the anchor convention.
   Without it, `Day 0` is ambiguous and `deidentify_check` may need a second
   pass.
6. **Re-use an existing `# Timeline` table** as the canonical event list.
   Don't silently re-derive it from prose; enrich it instead.
7. **Mermaid syntax discipline.** No tab indentation (Mermaid is whitespace-
   sensitive); 4-space indents; one `section` per clinical phase; events
   under 80 characters per line.

## Output format

The final assistant message must contain, in this order:

1. A one-line confirmation: `Read <input file> (<n> sections, <m> candidate
   events). Format: <mermaid-timeline | mermaid-gantt | markdown-table>.`
2. The path of the diagram file you wrote: `Wrote <path> (<n> lines).`
3. The embed snippet — a fenced code block the author copies into
   `draft.md`. Pick the inline-Mermaid form by default; offer the PNG form
   as a second block if the manuscript's pandoc setup does not run
   mermaid-filter (check the manuscript's YAML frontmatter for `mermaid:`
   keys; if absent, the PNG form is safer).
4. A one-line placement suggestion: e.g., `Recommended placement: directly
   after the "# Timeline" heading in <input file>:L<line>, replacing the
   existing table.`
5. A one-line caveat: `本文への反映は著者の判断で行ってください。本 skill は
   <input file> を変更していません。`
6. A short list (≤5 bullets) of anything that needed an author decision and
   defaulted: format choice, dropped clock times, dropped calendar dates,
   `[inferred]` events.

## Failure modes and how to handle them

| Failure | Handling |
|---|---|
| The input file has no `# Timeline`, `# Clinical findings`, or `# Patient information` heading | Stop. Tell the author you cannot locate the case presentation and ask for a section name or a line range. |
| Source mixes calendar dates and relative-day markers | Convert calendar dates to relative offsets using the anchor convention. Flag the conversion once in the reply, with the original date in parentheses inside an HTML comment in the `.mmd` file (`<!-- 2024-03-15 → Day 0 -->`) so the author can audit. |
| Output path already exists with a different title | Ask via `AskUserQuestion`: overwrite / suffix / abort. Default to abort on no response. |
| Author wants both Mermaid and drawio | Recommend they import the `.mmd` into draw.io (File → Import → Mermaid). Do not generate `.drawio` XML. |
| An event sentence has two possible relative-day anchors | Pick the one explicitly stated in the source. If both are stated, list them on adjacent indented `:` lines under the same `section` so the author can pick one. Do not silently drop either. |
| Source uses non-day units only ("the following spring", "shortly after") | Render as `[time unclear]` and ask the author for a relative-day estimate before persisting the file. Do not write the file with a `[time unclear]` node. |
| The author insists on writing the diagram **into** `draft.md` | Refuse once: "This skill writes the diagram to `assets/timeline.mmd` and emits an embed snippet you paste in by hand. Embedding inline keeps the source diffable." If the author still insists, hand them the inline-Mermaid form as a code block and let them paste it. Do not call `Edit` on `draft.md`. |

## Self-check before returning

1. Did you read the entire input file?
2. Did you re-use an existing `# Timeline` table (if present) rather than
   re-deriving the event list?
3. Does every event in the diagram map to a sentence in the source?
4. Did you keep `draft.md` untouched? (Grep for the `<!-- case-timeline:`
   marker — it must be absent from `draft.md`.)
5. Is the diagram title line stating the anchor convention?
6. Did you flag any dropped clock times / dropped calendar dates /
   `[inferred]` events in your reply?

## Testing this skill

A regression fixture lives at `skills/case_timeline/tests/`:

- `tests/fixture_case_report.md` — a short de-identified case (postpartum
  SCAD) with both a `# Timeline` table and narrative day markers in adjacent
  sections.
- `tests/expected_timeline.mmd` — the Mermaid `timeline` block the skill
  should produce from that fixture.
- `tests/expected_embed_snippet.md` — the embed comment + fenced code block
  the skill should emit in its reply (inline-Mermaid form).

Self-test procedure:

1. Treat `tests/fixture_case_report.md` as the manuscript input. Format =
   `mermaid-timeline`. Output path = `tests/out/timeline.mmd` (do not
   overwrite the expected file).
2. Run the skill end-to-end. Diff the produced file against
   `tests/expected_timeline.mmd`.
3. Diff the reply's embed snippet block against
   `tests/expected_embed_snippet.md`.

Pass criteria:

- The diagram file parses as Mermaid `timeline` (starts with `timeline`, has
  a `title` line stating the anchor convention, has at least two `section`
  blocks).
- Every event line in the diagram traces to a sentence in
  `fixture_case_report.md` (FP=0 on invented events).
- No calendar date (`YYYY-MM-DD` / `Month DD, YYYY`) appears in the diagram.
- `fixture_case_report.md` is unchanged (no `<!-- case-timeline:` marker
  written into it).
- The embed snippet uses the inline-Mermaid form by default.

## Reference

- CARE 2013 item 7 ("Timeline"): the timeline is required and should use
  relative time markers when calendar dates would re-identify the patient.
- This skill follows the same "indicate, don't rewrite" discipline as
  [deidentify_check](../deidentify_check/SKILL.md): the manuscript is the
  source of truth, the skill writes a sibling file (`assets/timeline.mmd`)
  and proposes how to embed it, but the author makes the edit by hand.
- Mermaid `timeline` syntax:
  https://mermaid.js.org/syntax/timeline.html
- Mermaid `gantt` syntax: https://mermaid.js.org/syntax/gantt.html
