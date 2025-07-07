import streamlit as st
import openai
import pandas as pd
import os

st.title("③ 사례별 AI 해설/수정/편집/태깅")

# OpenAI API KEY 불러오기 (환경변수/Streamlit secrets 우선)
api_key = os.environ.get("OPENAI_API_KEY", "") or st.secrets.get("openai_key", "")
if api_key:
    openai.api_key = api_key

cases_df = st.session_state.get('cases_df', None) or st.session_state.get("df", None)

if cases_df is not None and not cases_df.empty:
    st.info(f"분석된 사례 수: {len(cases_df)}")

    idx = st.selectbox("AI 해설/편집할 사례 선택", cases_df.index, format_func=lambda i: cases_df.loc[i, "case_text"][:80] + "...")
    row = cases_df.loc[idx]

    st.write("**본문**", row["case_text"])
    st.write("**매칭된 규칙**", row.get("joined_rules", ""))
    st.write("**AI 자동 요약**", row.get("요약", ""))
    st.write("**자동 태그**", ", ".join(row.get("자동태그", [])) if "자동태그" in row else "")

    # AI 해설 생성 프롬프트
    prompt = f"""다음은 명리학 실전 사례와 해석 규칙/요약/태그입니다.
사례: {row['case_text']}
적용 규칙: {row.get('joined_rules', '')}
자동 요약: {row.get('요약', '')}
자동 태그: {', '.join(row.get('자동태그', [])) if '자동태그' in row else ''}
이 명조의 자식/성별/유무/운에 대한 해설을 전문가처럼 5줄 이내로 설명해줘."""

    if st.button("AI 해설 생성"):
        with st.spinner("AI 해설 생성 중..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",  # "gpt-4o" 또는 "gpt-3.5-turbo"
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=600,
                )
                answer = response.choices[0].message.content
                st.success("AI 해설 결과 👇")
                st.write(answer)
            except Exception as e:
                st.error(f"AI 호출 오류: {e}")

    # 추가 편집 기능 (예시)
    with st.expander("📝 이 사례를 직접 수정/메모"):
        new_text = st.text_area("본문 수정", row["case_text"])
        new_rules = st.text_input("규칙/룰(수정)", row.get("joined_rules", ""))
        new_tags = st.text_input("태그(콤마로)", ", ".join(row.get("자동태그", [])) if "자동태그" in row else "")
        if st.button("수정 내용 저장"):
            cases_df.at[idx, "case_text"] = new_text
            cases_df.at[idx, "joined_rules"] = new_rules
            cases_df.at[idx, "자동태그"] = [t.strip() for t in new_tags.split(",") if t.strip()]
            st.session_state['cases_df'] = cases_df
            st.success("수정 완료!")

    st.dataframe(cases_df)
else:
    st.warning("2페이지(군집분석)에서 사례/룰 분석 먼저 진행하세요!")
