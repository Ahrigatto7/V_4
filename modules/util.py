import pandas as pd
import json
import re

def blocks_to_df(blocks):
    return pd.DataFrame(blocks)

def save_blocks(blocks, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(blocks, f, ensure_ascii=False, indent=2)

def txt_to_json(txt_path, json_path):
    """#으로 시작하는 구문을 키로 삼아 JSON(문단별/제목별)으로 변환"""
    with open(txt_path, encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    data = {}
    curr = None
    for line in lines:
        m = re.match(r'#\s?(.+)', line)
        if m:
            curr = m.group(1).strip()
            data[curr] = []
            continue
        if curr:
            data[curr].append(line)
    # 값이 1개면 단일 값으로 축약
    for k, v in data.items():
        data[k] = v[0] if len(v) == 1 else v
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

def highlight_terms(text, guides, maxlen=100):
    """guides의 키가 text에 있으면 HTML 하이라이트"""
    for k in guides:
        if k in text:
            tip = guides[k] if isinstance(guides[k], str) else (guides[k][0] if isinstance(guides[k], list) else str(guides[k]))
            tip = str(tip)[:maxlen]
            text = text.replace(k, f"<span title='{tip}' style='background:#FFFBCC'>{k}</span>")
    return text
