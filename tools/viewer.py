from pathlib import Path
import json
import pandas as pd
import streamlit as st

BASE_DIR = Path("../cases")

#BASE_DIR = Path("cases")

#st.write("Current dir:", Path(".").resolve())
#st.write("Cases dir:", BASE_DIR.resolve())
#st.write(
#    "JSON files:",
#    len(list(BASE_DIR.rglob("*.json")))
#)

st.set_page_config(
    page_title="利用支援事例ビューア",
    layout="wide"
)


@st.cache_data
def load_cases():

    records = []

    for json_file in BASE_DIR.rglob("*.json"):

        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            records.append(data)

        except Exception as e:
            print(e)

    return pd.DataFrame(records)


df = load_cases()
#st.write("件数:", len(df))
#st.write(df)
#st.write("Columns:")
#st.write(df.columns.tolist())
#st.write(df["document"].head())

if "technical_tags" not in df.columns:
    df["technical_tags"] = [[] for _ in range(len(df))]

st.title("利用支援事例ビューア")

st.sidebar.header("検索条件")

#
# キーワード検索
#
keyword = st.sidebar.text_input(
    "キーワード"
)

#
# 種別
#
#case_types = sorted(
#    df["case_type"].dropna().unique()
#)
if "case_type" not in df.columns:
    df["case_type"] = "unknown"

case_types = sorted(
    df["case_type"].dropna().unique()
)

selected_types = st.sidebar.multiselect(
    "種別",
    case_types,
    default=case_types
)

#
# 技術タグ
#
all_tags = set()

if "technical_tags" in df.columns:
    
    for tags in df["technical_tags"].dropna():

        if isinstance(tags, list):
            all_tags.update(tags)

selected_tags = st.sidebar.multiselect(
    "技術タグ",
    sorted(all_tags)
)

#
# 高速化倍率
#
min_speedup = st.sidebar.number_input(
    "高速化倍率",
    min_value=0.0,
    value=0.0
)

#
# 最大ノード数
#
min_nodes = st.sidebar.number_input(
    "ノード数",
    min_value=0,
    value=0
)

#
# 絞込み
#
filtered = df.copy()

filtered = filtered[
    filtered["case_type"].isin(
        selected_types
    )
]

if keyword:

    search_column = "document"

    if search_column not in filtered.columns:
        search_column = "problem"
    
    mask = (
        filtered[search_column]
        .fillna("")
        .str.contains(
            keyword,
            case=False,
            regex=False
        )
    )

    filtered = filtered[mask]

if (
    selected_tags
    and "technical_tags" in filtered.columns
):

    filtered = filtered[
        filtered["technical_tags"].apply(
            lambda x:
            any(
                tag in x
                for tag in selected_tags
            )
            if isinstance(x, list)
            else False
        )
    ]

if "speedup" in filtered.columns:

    filtered = filtered[
        (
            filtered["speedup"].fillna(0)
            >= min_speedup
        )
    ]

if "max_nodes" in filtered.columns:

    filtered = filtered[
        (
            filtered["max_nodes"].fillna(0)
            >= min_nodes
        )
    ]

st.write(
    f"検索結果: {len(filtered)}件"
)

#
# 表形式
#
show_cols = [
    col
    for col in [
        "case_id",
        "case_type",
        "classification",
        "speedup",
        "max_nodes"
    ]
    if col in filtered.columns
]

st.dataframe(
    filtered[show_cols],
    use_container_width=True
)

st.divider()

#
# 詳細表示
#
for _, row in filtered.iterrows():

    #title = (
    #    f"No.{row['case_id']} "
    #    f"[{row['case_type']}]"
    #)
    title = (
        f"No.{row.get('case_id', '-')}"
        f" [{row.get('case_type', 'unknown')}]"
    )

    with st.expander(title):

        #st.markdown(
        #    f"### 課題\n\n{row['problem']}"
        #)

        st.subheader("課題とタグ")
        st.text(
            row.get("problem", "")
        )

        st.markdown(
            f"### 分類\n\n"
            f"{row['classification']}"
        )

        #st.markdown(
        #    f"### 支援内容\n\n"
        #    f"{row['support_content']}"
        #)

        st.subheader("支援内容")
        st.text(
            row.get("support_content", "")
        )

        st.subheader("支援結果")
        st.text(
            row.get("support_result", "")
        )

        #st.markdown(
        #    f"### 支援結果\n\n"
        #    f"{row['support_result']}"
        #)

        #st.markdown(
        #    f"### 技術タグ\n\n"
        #    f"{', '.join(row['technical_tags'])}"
        #)
        technical_tags = row.get(
            "technical_tags",
            []
        )

        st.markdown(
            "### 技術タグ\n\n"
            + ", ".join(technical_tags)
        )

        if pd.notna(row.get("speedup")):

            st.markdown(
                f"### 高速化倍率\n\n"
                f"{row['speedup']}倍"
            )

        #if row.get("max_nodes"):

        #    st.metric(
        #        "最大利用ノード数",
        #        f"{int(row['max_nodes']):,}"
        #    )

        if pd.notna(row.get("max_nodes")):

            st.markdown(
                f"### 最大利用ノード数\n\n"
                f"{int(row['max_nodes'])}"
            )

for col in [
    "problem",
    "classification",
    "support_content",
    "support_result"
]:
    if col not in df.columns:
        df[col] = ""

df["document"] = (
    df["problem"].fillna("")
    + "\n"
    + df["classification"].fillna("")
    + "\n"
    + df["support_content"].fillna("")
    + "\n"
    + df["support_result"].fillna("")
)
