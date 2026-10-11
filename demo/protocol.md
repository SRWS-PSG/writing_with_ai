# Study protocol: Cardiac rehabilitation after acute myocardial infarction and 1-year readmission

> **Note for workshop participants**
> これは "Writing with AI" WS のデモ用に作った最小の研究計画書です。実在のデータではありません。
> 中身を細かく読み込まず、**「PECO・デザイン・解析が書いてあるな」** くらいで先に進んでください。

## 1. Background

Cardiac rehabilitation (CR) is recommended after acute myocardial infarction (AMI), but uptake among older adults is low. Whether outpatient CR participation reduces 1-year cardiovascular readmission in patients aged 65 years or older is unclear in our setting.

## 2. Research question (PECO)

| | |
|---|---|
| **P** | 65歳以上、急性心筋梗塞 (AMI) で入院し生存退院した患者 |
| **E** | 退院後3か月以内に外来心臓リハビリに **1回以上** 参加 |
| **C** | 退院後3か月以内に外来心臓リハビリに参加していない |
| **O** | 退院後1年以内の心血管系再入院 (yes/no) |

## 3. Study design

Single-center retrospective cohort study using electronic medical records.

## 4. Setting

Cardiology department, single tertiary care hospital in Japan.
Study period: discharges between 2022-04-01 and 2024-03-31.

## 5. Participants

**Inclusion**

- Age ≥ 65 years at admission
- Primary diagnosis of acute myocardial infarction (ICD-10: I21.x)
- Discharged alive during the study period

**Exclusion**

- Death during the index admission
- Transfer to another hospital
- Missing data on CR participation or readmission status

## 6. Exposure

Outpatient CR participation = attended **≥ 1** outpatient CR session within 3 months of discharge (billing codes).

## 7. Outcome

Cardiovascular readmission within 365 days of discharge = unplanned admission with a primary cardiovascular diagnosis (ICD-10: I00–I99).

## 8. Covariates

- Age (years, continuous)
- Sex (male / female)
- Diabetes mellitus (yes / no)

## 9. Sample size

All eligible patients in the study period are included (convenience sample). No formal sample size calculation.

## 10. Statistical analysis

1. **Table 1**: baseline characteristics by exposure group. Continuous variables as mean (SD); categorical as n (%).
2. **2×2 table**: exposure × outcome.
3. **Unadjusted risk ratio (RR)** with 95% confidence interval from the 2×2 table.
4. **Logistic regression**: outcome regressed on exposure adjusted for age, sex, and diabetes. Report odds ratios (OR) with 95% CI.
5. **Missing data**: complete-case analysis.

## 11. Ethics

Approved by the institutional review board (protocol #XXXX). Opt-out consent.
