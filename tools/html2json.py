from bs4 import BeautifulSoup
from pathlib import Path
import json
import re
import sys


TAG_RULES = {

    "MPI": [
        "MPI",
        "MPI_Barrier",
        "MPI_Allreduce"
    ],

    "OpenMP": [
        "OpenMP",
        "スレッド",
        "スレッド並列"
    ],

    "LoadBalance": [
        "インバランス",
        "負荷分散",
        "負荷不均衡",
        "データ分配"
    ],

    "Communication": [
        "通信",
        "同期"
    ],

    "IO": [
        "I/O",
        "ファイル出力",
        "ファイルI/O",
        "Lustre",
        "ステージング"
    ],

    "Memory": [
        "メモリ",
        "メモリアクセス"
    ],

    "Cache": [
        "キャッシュ",
        "キャッシュミス",
        "セクタキャッシュ"
    ],

    "Prefetch": [
        "プリフェッチ"
    ],

    "Compiler": [
        "コンパイラ",
        "最適化オプション",
        "最適化レベル"
    ],

    "Solver": [
        "ソルバー",
        "CG法",
        "行列ベクトル積"
    ],

    "FFT": [
        "FFT"
    ],

    "Porting": [
        "移植",
        "ビルド",
        "環境構築"
    ],

    "PerformanceAnalysis": [
        "性能分析",
        "性能評価",
        "プロファイル",
        "プロファイラ"
    ],

    "Scalability": [
        "大規模実行",
        "高並列",
        "スケーラビリティ"
    ],

    "MD": [
        "AMBER",
        "分子動力学"
    ],

    "CFD": [
        "FrontFlow"
    ]
}


def extract_speedup(text):

    patterns = [

        r'全体.*?([0-9]+(?:\.[0-9]+)?)倍',

        r'全体で.*?([0-9]+(?:\.[0-9]+)?)倍',

        r'支援前.*?([0-9]+(?:\.[0-9]+)?)倍'
    ]

    for pattern in patterns:

        m = re.search(pattern, text)

        if m:
            return float(m.group(1))

    values = []

    for m in re.finditer(
        r'([0-9]+(?:\.[0-9]+)?)倍',
        text
    ):
        values.append(
            float(m.group(1))
        )

    return max(values) if values else None


def extract_percent_improvement(text):

    patterns = [

        r'([0-9]+(?:\.[0-9]+)?)%\s*短縮',

        r'([0-9]+(?:\.[0-9]+)?)%\s*向上',

        r'([0-9]+(?:\.[0-9]+)?)%\s*改善'
    ]

    values = []

    for pattern in patterns:

        for m in re.finditer(pattern, text):

            values.append(
                float(m.group(1))
            )

    return max(values) if values else None


def extract_max_nodes(text):

    pattern = r'([0-9,]+)\s*ノード'

    nodes = []

    for m in re.finditer(pattern, text):

        value = int(
            m.group(1).replace(",", "")
        )

        nodes.append(value)

    return max(nodes) if nodes else None


def extract_max_threads(text):

    pattern = r'([0-9]+)\s*スレッド'

    values = []

    for m in re.finditer(pattern, text):

        values.append(
            int(m.group(1))
        )

    return max(values) if values else None


def extract_technical_tags(text):

    tags = set()

    lower_text = text.lower()

    for tag, keywords in TAG_RULES.items():

        for keyword in keywords:

            if keyword.lower() in lower_text:
                tags.add(tag)
                break

    return sorted(tags)


def get_text(elem):

    if elem is None:
        return ""

    return elem.get_text("\n", strip=True)


def extract_support_sections(detail_tr):

    support_content = ""
    support_result = ""

    if detail_tr is None:
        return support_content, support_result

    strong_tags = detail_tr.find_all("strong")

    for strong in strong_tags:

        title = strong.get_text(strip=True)

        parent = strong.find_parent("p")

        if parent is None:
            continue

        next_p = parent.find_next_sibling("p")

        if next_p is None:
            continue

        text = next_p.get_text("\n", strip=True)

        if title == "支援内容":
            support_content = text

        elif title == "支援結果":
            support_result = text

    return support_content, support_result


def extract_cases(html_file, case_type):

    with open(html_file, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    id_cells = soup.find_all(
        "td",
        id=re.compile(r"^id_\d+$")
    )

    cases = []

    for id_td in id_cells:

        html_id = id_td["id"]

        suffix = html_id.replace("id_", "")

        problem_td = soup.find("td", id=f"problem_{suffix}")
        overview_td = soup.find("td", id=f"overview_{suffix}")
        detail_tr = soup.find("tr", id=f"detail_{suffix}")

        case_id = int(id_td.get_text(strip=True))

        support_tags = []

        if problem_td:

            support_tags = [
                span.get_text(strip=True)
                for span in problem_td.find_all("span")
            ]

        problem_text = get_text(problem_td)
        classification = get_text(overview_td)

        support_content, support_result = \
            extract_support_sections(detail_tr)

        full_text = "\n".join([
            problem_text,
            classification,
            support_content,
            support_result
        ])

        technical_tags = extract_technical_tags(full_text)
        speedup = extract_speedup(
            support_result
        )
        improvement = extract_percent_improvement(
            support_result
        )
        max_nodes = extract_max_nodes(
            support_result
        )
        max_threads = extract_max_threads(
            support_result
        )

        document = f"""
【課題】
{problem_text}

【分類】
{classification}

【支援内容】
{support_content}

【支援結果】
{support_result}
""".strip()

        case = {

            "case_id": case_id,

            "case_type": case_type,

            "problem": problem_text,

            "classification": classification,

            "support_tags": support_tags,

            "technical_tags": technical_tags,

            "support_content": support_content,

            "support_result": support_result,

            "document": document,
            "speedup": speedup,
            "performance_improvement_percent": improvement,
            "max_nodes": max_nodes,
            "max_threads": max_threads

        }

        cases.append(case)

    return cases


def save_cases(cases, output_dir):

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for case in cases:

        filename = output_dir / \
            f"{case['case_id']:04d}.json"

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                case,
                f,
                ensure_ascii=False,
                indent=2
            )


def main():

    if len(sys.argv) != 4:

        print(
            "usage: python html2json.py "
            "<html_file> <case_type> <output_dir>"
        )

        return

    html_file = sys.argv[1]
    case_type = sys.argv[2]
    output_dir = Path(sys.argv[3])

    cases = extract_cases(
        html_file,
        case_type
    )

    save_cases(
        cases,
        output_dir
    )

    print(
        f"{len(cases)} cases exported."
    )


if __name__ == "__main__":
    main()
