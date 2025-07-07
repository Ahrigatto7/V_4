import streamlit as st
from modules.parsers import parse_json_rule_file
from modules.pdf_utils import df_to_pdf
from modules.db_utils import save_rule_df_to_db, load_rule_df_from_db
import pandas as pd

st.set_page_config(page_title="관계별 룰 분석 자동화", layout="wide")
st.title("관계별 룰 분석: PDF/DB 자동화")

# A. 파일 업로드
uploaded = st.file_uploader("관계 분석 룰 JSON 업로드", type=["json"])
if not uploaded:
    st.stop()

# B. 데이터 파싱
df = parse_json_rule_file(uploaded)

st.markdown("### 📋 데이터 미리보기")
st.dataframe(df)

# C. 카드 UI
st.markdown("### 🗂️ 카테고리별 카드")
for cat, subdf in df.groupby("카테고리"):
    st.subheader(f"🟦 {cat}")
    for _, row in subdf.iterrows():
        st.markdown(
            f"<div style='background:#F4F4F9;padding:10px;border-radius:9px;margin-bottom:7px;'>"
            f"<b>{row['구분']}: {row['용어/이름']}</b><br>"
            f"{row['설명']}<br>"
            f"{'예시: ' + row['예시'] if row['예시'] else ''}"
            "</div>", unsafe_allow_html=True
        )

# D. PDF/Excel/CSV/DB
if st.button("📄 PDF 보고서 생성/다운로드"):
    pdf = df_to_pdf(df)
    pdf_output = pdf.output(dest="S").encode("latin1")
    st.download_button(
        "PDF 다운로드",
        pdf_output,
        file_name="관계별_명리_룰_보고서.pdf",
        mime="application/pdf"
    )

st.download_button("Excel 다운로드", df.to_excel(index=False), file_name="관계별_명리_룰.xlsx")
st.download_button("CSV 다운로드", df.to_csv(index=False), file_name="관계별_명리_룰.csv")

db_path = "명리관계룰.db"
save_rule_df_to_db(df, db_path)
df_db = load_rule_df_from_db(db_path)
st.markdown("### 🔍 DB에서 불러온 룰(즉시 확인)")
st.dataframe(df_db)
