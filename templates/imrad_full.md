---
title: "論文タイトル"
author: "著者名"
date: "2025年4月22日"
bibliography: references.bib
csl: templates/vancouver-brackets.csl
---

<!-- 
注意: Pandoc 3.x以降で変換する場合は、必ず --citeproc オプションを指定してください
例: pandoc paper.md --citeproc -o paper.docx
-->

# IMRaD形式の論文テンプレート

このテンプレートは、IMRaD（Introduction, Methods, Results, and Discussion）形式の論文を執筆するためのものです。医学論文の標準的な構成に従っています。

## 要旨

**背景**: 研究の背景と目的を簡潔に述べます。なぜこの研究が重要なのかを説明します。

**方法**: 研究デザイン、対象者、介入、主要評価項目、統計解析方法などを簡潔に述べます。

**結果**: 主要な結果を数値データとともに示します。統計的有意性も含めます。

**結論**: 結果から導かれる結論と臨床的意義を述べます。

## 序論（Introduction）

### 研究の背景

研究テーマの重要性と現在の知見について説明します。この部分では、以下の点を含めるとよいでしょう：

- 研究テーマの疫学的・臨床的重要性
- 現在までに分かっていること
- 現在の知見の限界や課題
- 知識のギャップ

例：「2型糖尿病は世界的な健康問題であり、その有病率は年々増加している[^1]。薬物療法は血糖コントロールに有効であるが、副作用や医療費の問題がある[^2]。」

### 研究の目的

研究の具体的な目的と仮説を明確に述べます。

例：「本研究の目的は、2型糖尿病患者における運動療法と薬物療法のHbA1c低下効果を比較することである。我々は、運動療法が薬物療法と同等のHbA1c低下効果を示すという仮説を立てた。」

## 方法（Methods）

### 研究デザイン

研究のデザインを明確に述べます（例：ランダム化比較試験、コホート研究、症例対照研究など）。

### 対象者

対象者の選択基準と除外基準、リクルート方法、サンプルサイズの根拠などを述べます。

例：「20歳から65歳までの2型糖尿病患者100名を対象とした。選択基準は、HbA1c 7.0-9.0%、BMI 23-30 kg/m²、糖尿病の罹病期間が5年以内の患者とした。除外基準は、インスリン治療中、重篤な合併症を有する患者とした。」

### 介入または曝露

介入研究の場合は介入の詳細、観察研究の場合は曝露の評価方法を述べます。

例：「対象者を無作為に運動療法群（n=50）と薬物療法群（n=50）に割り付けた。運動療法群は週3回、1回60分の有酸素運動と筋力トレーニングを12週間実施した。薬物療法群はメトホルミン500mgを1日2回、12週間服用した。」

### アウトカム評価

主要評価項目と副次的評価項目、その測定方法を述べます。

例：「主要評価項目はHbA1cの変化量とした。副次的評価項目は空腹時血糖値、インスリン抵抗性指数（HOMA-IR）、体重、BMI、腹囲とした。これらの指標はベースラインと介入12週後に測定した。」

### 統計解析

使用した統計手法、有意水準、サンプルサイズの計算方法などを述べます。

例：「群間比較にはt検定またはMann-WhitneyのU検定を用いた。群内の前後比較には対応のあるt検定またはWilcoxonの符号順位検定を用いた。有意水準は5%とした。統計解析にはSPSS version 25.0を使用した。」

### 倫理的配慮

研究倫理委員会の承認、インフォームドコンセント、個人情報保護などについて述べます。

例：「本研究は○○大学医学部倫理委員会の承認を得て実施した（承認番号：XXXX）。すべての対象者から書面によるインフォームドコンセントを得た。」

## 結果（Results）

### 対象者の基本特性

対象者の基本特性（年齢、性別、BMI、合併症など）を表で示します。

例：「表1に示すように、運動療法群と薬物療法群の間で、年齢、性別、BMI、HbA1c、罹病期間に有意差はなかった。」

### 主要アウトカム

主要評価項目の結果を図表とともに示します。統計的有意性も含めます。

例：「図1に示すように、HbA1cはベースラインから12週後に運動療法群で0.8±0.3%、薬物療法群で0.9±0.4%低下した（群間差 0.1%, 95%CI -0.2-0.4, p=0.45）。」

### 副次的アウトカム

副次的評価項目の結果を図表とともに示します。

例：「表2に示すように、空腹時血糖値は両群で有意に低下した（運動療法群: -15.3 mg/dL, p<0.01; 薬物療法群: -18.2 mg/dL, p<0.01）。体重は運動療法群でのみ有意に減少した（-2.1 kg, p<0.01）。」

### サブグループ解析

事前に計画されたサブグループ解析の結果を示します（該当する場合）。

## 考察（Discussion）

### 主要な知見

研究の主要な知見を要約します。ボトムラインメッセージを強調します。

例：「本研究の主要な知見は、2型糖尿病患者において、運動療法が薬物療法と同等のHbA1c低下効果を示したことである。」

### 先行研究との比較

本研究の結果を先行研究と比較し、一致点や相違点を考察します。

例：「この結果は、Smithらの研究[^3]と一致している。彼らも12週間の運動療法がメトホルミンと同等のHbA1c低下効果を示したことを報告している。一方、Jonesらの研究[^4]では運動療法の効果がより小さかったが、これは介入期間が短かったことが影響している可能性がある。」

### 結果の解釈

結果の生物学的・臨床的意義を解釈します。

例：「運動療法によるHbA1c低下効果は、骨格筋のインスリン感受性の改善、筋肉量の増加、内臓脂肪の減少などの複数のメカニズムによるものと考えられる[^5]。」

### 研究の強みと限界

研究の強みと限界を客観的に述べます。

例：「本研究の強みは、ランダム化比較試験であること、脱落率が低かったこと（5%未満）、客観的な評価指標を用いたことである。限界としては、単一施設での研究であること、長期的な効果を評価していないこと、盲検化が不完全であったことが挙げられる。」

### 臨床的意義

研究結果の臨床的意義と実践への応用について述べます。

例：「本研究の結果は、2型糖尿病の初期治療として、薬物療法だけでなく運動療法も有効な選択肢となり得ることを示唆している。特に薬物療法に抵抗感がある患者や副作用が懸念される患者には、運動療法を積極的に推奨できる可能性がある。」

### 今後の研究課題

今後の研究課題や方向性について述べます。

例：「今後は、運動療法の長期的効果、様々な運動種類や強度の比較、薬物療法との併用効果などを検討する研究が必要である。」

## 結論

研究の主要な結論と意義を簡潔に述べます。

例：「2型糖尿病患者において、12週間の運動療法は薬物療法と同等のHbA1c低下効果を示した。運動療法は2型糖尿病の血糖コントロールに有効な治療選択肢となり得る。」

## 謝辞

研究に貢献した個人や団体、資金提供者などに謝意を表します。

## 利益相反

利益相反の有無を明記します。

例：「著者らは本研究に関連する利益相反はない。」

## 参考文献

[^1]: 参考文献1
[^2]: 参考文献2
[^3]: 参考文献3
[^4]: 参考文献4
[^5]: 参考文献5
