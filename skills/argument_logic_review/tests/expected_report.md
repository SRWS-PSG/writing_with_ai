<!-- Expected argument_logic_review report for fixture.md. Used as a regression
     target. Wording may vary; the PASS CRITERIA are the codes, severities,
     locations, and the restructure moves — not the exact prose. -->

- source: skills/argument_logic_review/tests/fixture.md
- genre: letter to the editor (inferred)
- core thesis: the study measured improvement on a re-tested ECG set, which is
  not the same as durable retention, so a fresh set in a later rotation is
  needed to test whether app practice transfers to students' own reading skill.
- thesis spread: stated once, occupies P2–P4 (one idea across three paragraphs)

## Step 2 — Paragraph map

- **P1 (praise)** — topic sentence present & accurate. Arc `claim (valuable) →
  evidence (authentic rotation / blinded examiners / both outcomes) →
  significance`. One idea. Role: praise. Clean.
- **P2 (limitation + recommendation)** — topic sentence is the recommendation,
  not the limitation (L4/L7). Arc should be `result → how the post-test was
  built → either way it cannot show retention → re-test gain ≠ retention`, but
  the recommendation is stated first and the construction-detail clause
  ("The post-app test was a re-attempt...") interrupts the core argument (L4).
  Multiple roles crammed in (L5-adjacent). Role: limitation — but leaks the
  proposal.
- **P3 (proposed design)** — topic sentence restates P2's proposal. Adds one
  genuinely new element (randomized baseline→app/usual→later paper test), but
  the closing two sentences repeat P2 (L2). Role: proposal.
- **P4 (close)** — three sentences, each restating P1–P3; no new so-what (L8).
  Role: closing.

## Step 5 — Findings

| Loc | Code | Severity | Issue | Fix |
|---|---|---|---|---|
| P2–P4 | L2 | Major | One point ("re-test gain ≠ retention; test on a fresh set") is diluted and restated across three paragraphs. | Collapse to one limitation paragraph + one proposal paragraph. |
| P2 | L7 | Major | The recommendation opens P2, ahead of the rationale that justifies it; the proposal belongs in P3. | Move the recommendation out of P2 into P3; open P2 with the limitation. |
| P2 | L4 | Minor | Conclusion-first ordering and an interrupting construction-detail clause bury the both-directions argument (the real thesis) at the paragraph end. | Reorder: result → how the post-test was built → neither direction shows retention → re-test gain ≠ retention (cite Roediger & Karpicke). |
| P4 | L8 | Minor | Closing restates P1–P3 with no new implication. | Cut to one forward-looking sentence, or drop. |

## Diagnosis (日本語)

実質的な主張は1つ（「再テストの改善は retention ではない。別の新規 ECG セットで
転移を測れ」）なのに、P2・P3・P4 に薄く伸びて反復している（L2）のが最大の問題。
P2 は提案が冒頭に来て論証が後ろに回り（L7）、作問手順の説明が核心の both-directions
論証に割り込んでいる（L4）。P4 は P1–P3 の縮小コピーで新しい含意がない（L8）。
推奨再構成は 3 段落化: P1 称賛 / P2 解釈・限界（提案は入れない）/ P3 提案＋結語。

## Restructured draft

Would write `skills/argument_logic_review/tests/fixture.logic.md` — P2 reordered
to lead with the limitation and end on the both-directions argument
`[L4]`, the proposal moved into P3 `[L7]`, P2–P4's repeated point collapsed
`[L2]`, and P4 surfaced as `> [L8: candidate for cut — restates P1–P3]`.

## Recommended next

Run `proofread-manuscript` on the restructured draft for prose style, then
`letter_review_simulator` for fairness and spin.
