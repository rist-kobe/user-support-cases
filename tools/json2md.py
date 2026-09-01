from pathlib import Path
import json
import sys


CASE_TYPE_NAME = {
    "performance_improvement": "性能改善",
    "performance_analysis": "性能分析",
    "porting": "移植"
}


def create_markdown(data):

    case_type = data.get("case_type", "")

    case_type_name = CASE_TYPE_NAME.get(
        case_type,
        case_type
    )

    support_tags = ", ".join(
        data.get("support_tags", [])
    )

    technical_tags = ", ".join(
        data.get("technical_tags", [])
    )
    speedup = data.get("speedup")
    performance_improvement_percent = data.get("performance_improvement_percent")
    max_nodes = data.get("max_nodes")
    max_threads = data.get("max_threads")

    md = f"""# 支援事例 No.{data['case_id']}

## 種別

{case_type_name}

## 課題・問題点

{data.get('problem', '')}

## 分類

{data.get('classification', '')}

## 支援内容

{data.get('support_content', '')}

## 支援結果

{data.get('support_result', '')}

## 支援タグ

{support_tags}

## 技術タグ

{technical_tags}

## 定量的効果

| 項目 | 値 |
|------|------|
"""
#    md += """

#"""

    md += (
        f"| 高速化倍率 | "
        f"{speedup}倍 |\n"
        if speedup is not None
        else "| 高速化倍率 | - |\n"
    )

    md += (
        f"| 性能改善率 | "
        f"{performance_improvement_percent}% |\n"
        if performance_improvement_percent is not None
        else "| 性能改善率 | - |\n"
    )

    md += (
        f"| 最大利用ノード数 | "
        f"{max_nodes:,} |\n"
        if max_nodes is not None
        else "| 最大利用ノード数 | - |\n"
    )

    md += (
        f"| 最大スレッド数 | "
        f"{max_threads} |\n"
        if max_threads is not None
        else "| 最大スレッド数 | - |\n"
    )

    return md


def convert_directory(json_dir, md_dir):

    md_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    json_files = sorted(
        json_dir.glob("*.json")
    )

    for json_file in json_files:

        with open(
            json_file,
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        markdown = create_markdown(data)

        output_file = (
            md_dir /
            f"{json_file.stem}.md"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(markdown)

        print(
            f"generated: {output_file.name}"
        )


def main():

    if len(sys.argv) != 3:

        print(
            "usage: python json2md.py "
            "<json_dir> <output_dir>"
        )

        return

    json_dir = Path(sys.argv[1])
    md_dir = Path(sys.argv[2])

    convert_directory(
        json_dir,
        md_dir
    )


if __name__ == "__main__":
    main()
