from pathlib import Path
from collections import Counter
import json

# JSONファイルを格納したディレクトリ
BASE_DIR = Path("../cases")

# 表示名
CATEGORY_NAMES = {
    "performance_improvement": "性能改善",
    "performance_analysis": "性能分析",
    "porting": "移植"
}


def count_cases():
    """カテゴリごとの件数を集計"""

    stats = {}
    total = 0

    for category_dir in BASE_DIR.iterdir():

        if not category_dir.is_dir():
            continue

        count = len(list(category_dir.glob("*.json")))

        stats[category_dir.name] = count
        total += count

    return stats, total


def collect_tags():
    """technical_tags を集計"""

    counter = Counter()

    for json_file in BASE_DIR.rglob("*.json"):

        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        for tag in data.get("technical_tags", []):
            counter[tag] += 1

    return counter


def collect_examples(max_examples=5):
    """代表事例を収集"""

    examples = []

    for json_file in sorted(BASE_DIR.rglob("*.json")):

        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            examples.append(
                {
                    "case_id": data["case_id"],
                    "type": data["case_type"],
                    "problem": data["problem"][:80]
                }
            )

            if len(examples) >= max_examples:
                break

        except Exception:
            pass

    return examples


def create_readme():

    stats, total = count_cases()
    tags = collect_tags()
    examples = collect_examples()

    lines = []

    lines.append("# 「富岳」を中核とするHPCIの利用支援事例集")
    lines.append("")

    lines.append("## 概要")
    lines.append("")
    lines.append(
        "「富岳」を中核とするHPCIの利用支援で蓄積された事例をJSONおよびMarkdown形式で整理したリポジトリです。"
    )
    lines.append("")
    lines.append("### カテゴリ別件数")
    lines.append("")

    for category, count in sorted(stats.items()):

        display_name = CATEGORY_NAMES.get(
            category,
            category
        )

        lines.append(f"- {display_name}: {count}件")

    lines.append("")
    lines.append(f"**総事例数: {total}件**")
    lines.append("")

    lines.append("---")
    lines.append("")

    lines.append("## 技術タグ統計")
    lines.append("")

    lines.append("| 技術タグ | 件数 |")
    lines.append("|-----------|------:|")

    for tag, count in tags.most_common():
        lines.append(f"| {tag} | {count} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## ディレクトリ構成")
    lines.append("")

    lines.append("```text")
    lines.append("cases/")
    lines.append("├── performance_improvement/")
    lines.append("├── performance_analysis/")
    lines.append("└── porting/")
    lines.append("")
    lines.append("markdown/")
    lines.append("├── performance_improvement/")
    lines.append("├── performance_analysis/")
    lines.append("└── porting/")
    lines.append("")
    lines.append("tools/")
    lines.append("├── html2json.py")
    lines.append("├── json2md.py")
    lines.append("├── readme_generator.py")
    lines.append("└── viewer.py")

    lines.append("```")

    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 代表事例")
    lines.append("")

    for ex in examples:

        display_name = CATEGORY_NAMES.get(
            ex["type"],
            ex["type"]
        )

        lines.append(
            f"- No.{ex['case_id']} ({display_name}) :"
            f"{ex['problem']}..."
        )

    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## JSONフォーマット")
    lines.append("")

    lines.append("```json")
    lines.append("{")
    lines.append('  "case_id": 1,')
    lines.append('  "case_type": "performance_improvement",')
    lines.append('  "problem": "...",')
    lines.append('  "classification": "...",')
    lines.append('  "support_tags": ["..."],')
    lines.append('  "technical_tags": ["MPI","IO"],')
    lines.append('  "support_content": "...",')
    lines.append('  "support_result": "...",')
    lines.append('  "document": "..."')
    lines.append("}")
    lines.append("```")

    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 利用例")
    lines.append("")
    lines.append("- GitHub上での事例検索")
    lines.append("- RAGの知識ベース")
    lines.append("- LangChain/LlamaIndexへのインポート")
    lines.append("- OpenWebUI、Difyのデータセット")
    lines.append("- Microsoft Copilot等への参照データ")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 事例確認ツール (Streamlit)")
    lines.append("")

    lines.append(
        "JSON変換結果や技術タグを確認するための"
        "簡易検索ツールを提供しています。"
    )

    lines.append("### インストール")

    lines.append("")
    lines.append("```bash")
    lines.append("pip install streamlit pandas")
    lines.append("```")

    lines.append("")

    lines.append("### 起動")

    lines.append("")
    lines.append("```bash")
    lines.append("cd tools")
    lines.append("streamlit run viewer.py")
    lines.append("```")

    lines.append("### 主な機能")

    lines.append("")
    lines.append("- キーワード検索")
    lines.append("- 技術タグ検索")
    lines.append("- 種別による絞り込み")
    lines.append("- 高速化倍率による絞り込み")
    lines.append("- ノード数による絞り込み")

    return "\n".join(lines)


def main():

    readme_content = create_readme()

    with open(
        "README.md",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(readme_content)

    print("README.md generated")


if __name__ == "__main__":
    main()
