# 「富岳」を中核とするHPCIの利用支援事例集

## 概要

「富岳」を中核とするHPCIの利用支援で蓄積された事例をJSONおよびMarkdown形式で整理したリポジトリです。

### カテゴリ別件数

- 性能分析: 44件
- 性能改善: 99件
- 移植: 36件

**総事例数: 179件**

---

## 技術タグ統計

| 技術タグ | 件数 |
|-----------|------:|
| PerformanceAnalysis | 109 |
| OpenMP | 71 |
| Porting | 69 |
| Communication | 67 |
| Memory | 66 |
| MPI | 65 |
| IO | 38 |
| LoadBalance | 36 |
| Compiler | 30 |
| Scalability | 30 |
| Solver | 16 |
| FFT | 15 |
| Cache | 7 |
| MD | 4 |
| CFD | 3 |
| Prefetch | 2 |

---

## ディレクトリ構成

```text
cases/
├── performance_improvement/
├── performance_analysis/
└── porting/

markdown/
├── performance_improvement/
├── performance_analysis/
└── porting/

tools/
├── html2json.py
├── json2md.py
├── readme_generator.py
└── viewer.py

docs/
├── index.html
├── assets/
│   ├── style.css
│   └── app.js
└── data/
    └── cases.json

scripts/
└── build_pages_data.py
```

---

## 代表事例

- No.1 (性能分析) :OSS の FFT ライブラリの性能が不足のため、FFT ライブラリの性能調査を依頼。
ソフトウェア評価...
- No.2 (性能分析) :PC クラスタと「京」で実行したが、「京」では途中から計算結果が変わり収束しないため、原因調査。
移植・環境適応
実行支援・動作検証...
- No.3 (性能分析) :「京」においてプログラムの実行時間が実行毎にブレが生じ、性能が出ない。ブレの原因を調査。
I/O・メモリ最適化...
- No.4 (性能分析) :利用者コードの性能分析方法を知りたい。
ソフトウェア評価...
- No.5 (性能分析) :利用者コードの「京」上で性能分析した結果を知りたい。また、性能が妥当かどうかの評価について
ソフトウェア評価...
