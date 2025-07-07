import streamlit as st
import pandas as pd
import sqlite3
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import openai

st.title("② 군집분석 + 챗봇 + 요약 + 자동 태깅 + DB 저장/검색")

openai_api_key = st.secrets.get("openai_key", "")  # 실제 서비스시 Secrets에 입력 필요

def load_file_to_df(file):
    ext = file.name.split('.')[-1].lower()
    if ext in ["txt", "md"]:
        text = file.read().decode("utf-8")
        df = pd.DataFrame([{"본문": t} for t in text.split('\n') if t.strip()])
    elif ext == "csv":
        df = pd.read_csv(file)
    elif ext in ["xlsx", "xls"]:
        df = pd.read_excel(file)
    else:
        df = pd.DataFrame()
    return df

def simple_rule_match(text: str, rule_patterns: dict):
    return [rule_patterns[k] for k in rule_patterns if k in text]

def run_clustering(cases, n_clusters=5):
    vectorizer = TfidfVectorizer(max_features=60)
    X = vectorizer.fit_transform(cases["case_text"])
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cases["군집"] = kmeans.fit_predict(X)
    return cases

def ai_summary(text):
    if not openai_api_key:
        return "(OpenAI API키 없음: 샘플 요약)\n" + (text[:80] + "..." if len(text) > 80 else text)
    try:
        openai.api_key = openai_api_key
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"아래 명리 텍스트를 2줄로 요약:\n{text}"}]
        )
        return completion.choices[0].message['content'].strip()
    except Exception as e:
        return f"(AI 요약 오류) {e}"

def auto_tags(text, tag_patterns=None):
    if tag_patterns is None:
        tag_patterns = [
            "공망", "귀격", "상관격", "입묘", "관성", "식신", "재살", "적포", "왕지", "인성", "비겁",
            "합", "충", "파", "형", "묘", "관재", "사업", "이혼", "취업", "합격"
        ]
    tags = [tag for tag in tag_patterns if tag in text]
    return tags

# --- 파일 업로드
file = st.file_uploader("파일 업로드", type=["txt", "md", "csv", "xlsx", "xls"])
if file:
    df = load_file_to_df(file)
    st.dataframe(df)
    st.session_state["df"] = df

if st.session_state.get("df", None) is not None:
    df = st.session_state["df"]
    texts = df.iloc[:,0].dropna().astype(str).tolist()
    cases = [t.strip() for t in texts if len(t.strip()) > 10]
    cases_df = pd.DataFrame({'case_text': cases})

    # 규칙 태깅
    rule_patterns = {
        "허투": "허투는 성별/유무 변동",
        "입묘": "입묘시 성별변화/무자식 가능",
        "공망": "공망은 자식운 약화",
        "관성": "관성은 자식성(남명)",
        "식신": "여명은 식신/상관이 자식"
    }
    cases_df['matched_rules'] = cases_df['case_text'].apply(lambda x: simple_rule_match(x, rule_patterns))
    cases_df['joined_rules'] = cases_df['matched_rules'].apply(lambda x: "; ".join(x) if x else "")

    # AI 요약 및 자동 태깅
    with st.spinner("AI 요약/태깅 중..."):
        cases_df['요약'] = cases_df['case_text'].apply(ai_summary)
        cases_df['자동태그'] = cases_df['case_text'].apply(auto_tags)

    n_clusters = st.slider("군집 개수", 2, min(10, len(cases_df)), 5)
    cases_df = run_clustering(cases_df, n_clusters)
    st.dataframe(cases_df)

    # 챗봇(심플) - 텍스트 검색 기반
    st.markdown("### 💬 사례 챗봇/검색")
    chat_q = st.text_input("궁금한 점, 키워드, 질문을 입력")
    if chat_q:
        found = cases_df[cases_df['case_text'].str.contains(chat_q)]
        if not found.empty:
            st.write("관련 사례(상위 3개):")
            for i, row in found.head(3).iterrows():
                st.info(f"사례 {i+1}\n\n{row['요약']}")
        else:
            st.warning("해당 키워드를 포함하는 사례가 없습니다.")

    # DB 자동 저장
    db_name = "analysis.db"
    table_name = "case_analysis"
    with sqlite3.connect(db_name) as con:
        cases_df.to_sql(table_name, con, if_exists="replace", index=False)
    st.success(f"DB에 자동 저장 완료: {db_name} [{table_name}]")

    st.markdown("### 🔍 DB 저장 데이터 즉시 검색")
    with sqlite3.connect(db_name) as con:
        query = st.text_input("DB에서 검색어(본문/요약/태그/룰 등)")
        q = f"SELECT * FROM {table_name}"
        if query:
            q += f" WHERE case_text LIKE '%{query}%' OR joined_rules LIKE '%{query}%' OR 요약 LIKE '%{query}%' OR 자동태그 LIKE '%{query}%'"
        result_df = pd.read_sql(q, con)
        st.dataframe(result_df)
        st.bar_chart(result_df['군집'].value_counts())

    st.download_button("분석결과(Excel) 다운로드", cases_df.to_csv(index=False), file_name="분석결과.csv")
else:
    st.info("파일 업로드 후 군집분석을 실행하세요.")
