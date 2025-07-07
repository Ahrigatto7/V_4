import pandas as pd
from modules.pdf_utils import df_to_pdf

def test_df_to_pdf_creates_pdf(tmp_path):
    data = {
        "카테고리": ["A", "B"],
        "구분": ["단계", "사례요약"],
        "용어/이름": ["용어1", "조건1"],
        "설명": ["설명1", "해석1"],
        "예시": ["예시1", ""]
    }
    df = pd.DataFrame(data)
    pdf = df_to_pdf(df)
    output_path = tmp_path / "output.pdf"
    pdf.output(str(output_path))
    assert output_path.exists()
    assert output_path.stat().st_size > 0
