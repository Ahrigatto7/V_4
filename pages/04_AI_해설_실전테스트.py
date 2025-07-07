import streamlit as st
import openai
import pandas as pd
import time

st.title("④ AI 해설/룰 실전 테스트+챗봇+로그")

api_key = st.text_input("OpenAI API KEY를 입력하세요", type="password", value=st.session_state.get("openai_api_key", ""))
if api_key:
    st.session_state["openai_api_key"] = api_key
    openai.api_key = api_key

# AI 해설/챗봇 로그
if "ai_logs" not in st.session_state:
    st.session_state["ai_logs"] = []

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# 실전 AI 해설
prompt = st.text_area("AI 해설 프롬프트 입력", height=100)
if st.button("AI 해설 생성"):
    if not api_key or not prompt.strip():
        st.error("API 키와 프롬프트 모두 입력해 주세요!")
    else:
        with st.spinner("AI 해설 생성 중..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=600,
                )
                answer = response.choices[0].message.content
                st.success("AI 해설 👇")
                st.write(answer)
                # 로그 저장
                st.session_state["ai_logs"].append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "prompt": prompt,
                    "answer": answer,
                })
            except Exception as e:
                st.error(f"AI 호출 오류: {e}")

# 로그 다운로드/분석
st.markdown("---")
st.markdown("### 📜 AI 해설 로그")
if st.session_state["ai_logs"]:
    logs_df = pd.DataFrame(st.session_state["ai_logs"])
    st.dataframe(logs_df)
    st.download_button("로그 CSV 다운로드", logs_df.to_csv(index=False), file_name="ai_해설_로그.csv")
    kw = st.text_input("로그 키워드 분석")
    if kw:
        kw_logs = logs_df[logs_df['answer'].str.contains(kw, case=False, na=False)]
        st.write(f"{kw} 포함 로그 개수:", len(kw_logs))
        st.dataframe(kw_logs)

# 실시간 챗봇
st.markdown("---")
st.markdown("### 💬 명리 챗봇(대화 자동화)")
chat_query = st.text_area("챗봇 질문", key="chat_input")
if st.button("챗봇 질의"):
    messages = [{"role": "system", "content": "명리학 전문가로 답변해줘."}]
    for qa in st.session_state["chat_history"]:
        messages.append({"role": "user", "content": qa["question"]})
        messages.append({"role": "assistant", "content": qa["answer"]})
    messages.append({"role": "user", "content": chat_query})
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=600,
    )
    ai_ans = response.choices[0].message.content
    st.session_state["chat_history"].append({"question": chat_query, "answer": ai_ans})
    st.success("AI 답변: " + ai_ans)

st.markdown("#### 🗨️ 챗봇 대화 기록")
for i, qa in enumerate(st.session_state["chat_history"]):
    st.write(f"Q{i+1}: {qa['question']}")
    st.write(f"A{i+1}: {qa['answer']}")

