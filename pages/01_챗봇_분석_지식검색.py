import streamlit as st
import pandas as pd
import json
import re
import os
from modules.parsers import parse_file_to_blocks
from modules.util import blocks_to_df, save_blocks

st.title("① 문서/파일 업로드 + 챗봇/질문/지식검색")

# (1) 문서 업로드 및 구조화 (블록 단위)
uploaded_file = st.file_uploader(
    "데이터 파일 업로드(pdf/docx/txt/csv/json/md/xlsx)", 
    type=["pdf", "docx", "txt", "csv", "json", "md", "xls", "xlsx"]
)

def parse_txt(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return [{"문장": line} for line in lines]

def parse_md(text): return parse_txt(text)

def parse_pdf(file):
    import pdfplumber
    with pdfplumber.open(file) as pdf:
        text = "\n".join([page.extract_text() or "" for page in pdf.pages])
    return parse_txt(text)

def parse_docx(file):
    from docx import Document
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return parse_txt(text)

def parse_any_file(file):
    ext = file.name.split('.')[-1].lower()
    if ext == "txt":
        text = file.read().decode("utf-8")
        return parse_txt(text)
    elif ext == "md":
        text = file.read().decode("utf-8")
        return parse_md(text)
    elif ext == "csv":
        df = pd.read_csv(file)
        return df.to_dict(orient="records")
    elif ext == "json":
        data = json.load(file)
        return data if isinstance(data, list) else [data]
    elif ext in ["xls", "xlsx"]:
        df = pd.read_excel(file)
        return df.to_dict(orient="records")
    elif ext == "pdf":
        file.seek(0)
        return parse_pdf(file)
    elif ext == "docx":
        file.seek(0)
        return parse_docx(file)
    else:
        return []

cases = []
block_cases = []

if uploaded_file:
    # 임시 저장 (block_parser용)
    tmp_path = f"./tmp/{uploaded_file.name}"
    os.makedirs("./tmp", exist_ok=True)
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.read())
    # (A) block_parser 구조화
    block_cases = parse_file_to_blocks(tmp_path)
    st.session_state["doc_blocks"] = block_cases
    save_blocks(block_cases, "자료_통합.json")
    st.success(f"🔗 블록 구조화 완료: {len(block_cases)}건")
    st.dataframe(blocks_to_df(block_cases))
    # (B) 간단 파일 구조화 (문장/테이블 단위)
    try:
        uploaded_file.seek(0)  # 재사용 위해 파일 포인터 초기화
        cases = parse_any_file(uploaded_file)
    except Exception as e:
        st.error(f"파일 파싱 오류: {e}")
    if cases:
        df = pd.DataFrame(cases)
        st.session_state["upload_df"] = df
        st.success(f"자동 구조화 {len(df)}건")
        st.dataframe(df)
        keyword = st.text_input("키워드로 검색(표)")
        if keyword:
            st.dataframe(df[df.apply(lambda row: row.astype(str).str.contains(keyword), axis=1)])
    else:
        st.warning("구조화 가능한 데이터가 없습니다.")
else:
    st.info("분석할 사주/명리/데이터 파일을 업로드하세요.")

st.markdown("---")
st.subheader("텍스트(팔자/질문/키워드) 직접 입력")
query = st.text_area("질문/팔자/텍스트 직접 입력", height=80)
if st.button("분석/검색"):
    st.write("질문 내용:", query)
    st.session_state["last_query"] = query

# 추후 챗봇/AI검색 연동(예: OpenAI, 사전/룰 DB 등) 이 아래에 추가
