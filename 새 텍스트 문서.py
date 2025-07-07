import streamlit as st
import pandas as pd
import json

st.title("명리 주제별 사례집 - 소제목/상세목차 자동화")

@st.cache_data
def load_blocks(path="book5_v2_분석_블록.json"):
    with open(path, encoding="utf-8") as f:
        blocks = json.load(f)
    df = pd.DataFrame(blocks)
    df['concept'] = df['concept'].apply(lambda x: x if x else ['기타'])
    df_exploded = df.explode('concept')
    return df, df_exploded

df, df_exploded = load_blocks()

# 1. 주제(카테고리)별 사례수, 사례명(소제목) 자동 추출
st.markdown("### 📚 카테고리별 사례수/소제목 목차")
toc = (
    df_exploded.groupby('concept')
    .agg({'title': ['count', list]})
    .reset_index()
)
toc.columns = ['카테고리', '사례수', '사례목록']
st.dataframe(toc)

# 2. 선택된 카테고리의 소제목(사례명) 목록 보기
cat = st.selectbox("카테고리(주제) 선택", toc['카테고리'])
cat_titles = toc[toc['카테고리'] == cat]['사례목록'].values[0]
st.markdown(f"**[{cat}] 사례 소제목 목록**")
for i, t in enumerate(cat_titles, 1):
    st.markdown(f"{i}. {t}")

# 3. 상세 목차(카테고리>소제목>본문) 마크다운 생성
st.markdown("---")
st.markdown("### 📝 카테고리별 상세 목차/본문 (마크다운)")
md_lines = ["# 명리 실전 사례집 (상세 목차/본문 자동생성)\n"]
for idx, row in toc.iterrows():
    md_lines.append(f"\n## {row['카테고리']} ({row['사례수']}건)\n")
    for i, t in enumerate(row['사례목록'], 1):
        md_lines.append(f"### {i}. {t}")

        # 본문, 조건, 결과, 해석 등 상세 내용
        detail = df_exploded[(df_exploded['concept']==row['카테고리']) & (df_exploded['title']==t)].iloc[0]
        md_lines.append(f"- **본문:** {detail.get('본문','')}")
        md_lines.append(f"- **조건:** {', '.join(detail.get('조건', []))}")
        md_lines.append(f"- **결과:** {', '.join(detail.get('결과', []))}")
        md_lines.append(f"- **기존명리해석:** {', '.join(detail.get('기존명리해석', []))}")
        md_lines.append(f"- **차별적해석:** {', '.join(detail.get('차별적해석', []))}")
        md_lines.append("")  # 줄바꿈

# 마크다운 목차 다운로드
st.download_button(
    "상세 목차/본문(MD) 다운로드",
    "\n".join(md_lines),
    file_name="명리_상세목차_사례집.md"
)
