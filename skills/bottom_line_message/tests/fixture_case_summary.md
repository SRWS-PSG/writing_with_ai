# Fixture case summary (de-identified)

Toy case mirrored from the `similar_cases_search` fixture so the same two
PubMed entries (`pmid99999001`, `pmid99999002`) serve as anchor + support.

## Case presentation (synthetic, de-identified)

A patient in their 70s with a history of methicillin-resistant *Staphylococcus
aureus* (MRSA) bacteremia was started on intravenous daptomycin (6 mg/kg
daily). On day 5 of therapy, the patient developed fever (38.6°C), dry cough,
and progressive hypoxemia (SpO2 88% on room air). Chest CT showed bilateral
peripheral ground-glass opacities with eosinophilic predominance on
bronchoalveolar lavage (BAL eosinophils 42%). Peripheral blood eosinophilia
was 18%. Daptomycin was discontinued and intravenous methylprednisolone
1 mg/kg/day was started. Symptoms resolved within 72 hours, and CT findings
cleared by day 14. The patient was discharged on day 21 with no recurrence at
6-month follow-up.

## Author notes (used by the regression fixture to drive the dialogue)

These notes simulate the answers the author would give across phases 1–3 of
the bottom-line-message dialogue. The skill's expected artifact in
`expected_artifact.md` is what the skill should produce given **these** notes
plus `fixture_refs.bib`.

### Phase 1 — basic understanding

- 概要: 70 代、MRSA 菌血症に対する daptomycin 投与中の day 5 で eosinophilic
  pneumonia (EP) を発症。
- 特徴的所見: 末梢血好酸球 18%、BAL 好酸球 42%、両肺末梢のすりガラス陰影。
- 通常経過との相違: 文献的には daptomycin-EP は投与開始 2–4 週で発症することが
  多いが、本症例は **day 5** と顕著に早い。
- 治療・転帰: daptomycin 中止 + メチルプレドニゾロン 1 mg/kg/day。72 時間で
  症状寛解、14 日で CT 改善。6 ヶ月再発なし。

### Phase 2 — surprise mining

- 最も驚いた点: 発症が day 5 と非常に早期だったこと (典型例 2–4 週との乖離)。
- 典型例との違い: `pmid99999001` の症例報告でも発症は数週単位だった。本症例は
  桁が違う早期。
- 臨床的教訓: daptomycin 開始後早期 (1 週以内) でも好酸球性肺炎を鑑別に挙げる。
- 今後の診療への活用: daptomycin 投与 1 週時点での好酸球数 + SpO2 モニタリング
  を提案。

### Phase 3 — clinical-significance analysis

- S1 (早期発症): 診療方針への影響 = 監視時期の前倒し / 実臨床応用 = day 5–7
  での好酸球+SpO2 チェック / 教育的価値 = 教科書記述の修正候補。Anchor: pmid99999001。
- S2 (中止+ステロイドで急速寛解): 診療方針への影響 = 治療パターンの確認 /
  実臨床応用 = 中止単独でも改善する場合の判断材料 / 教育的価値 = 他抗菌薬関連
  EP との共通治療戦略。Anchor/Support: pmid99999002。

両方とも 発見1 / 発見2 として採用 (3 つ目の候補なし)。
