import re
import json
from typing import List, Dict, Any

# 주요 개념 사전 (원하는 만큼 추가/수정)
CONCEPTS = [
    "傷官格", "관살제압", "귀격", "공망", "재살격", "적포구조", "정인격", "편인격",
    "재성격", "관성격", "합", "충", "파", "형", "묘", "공망운", "왕지", "조후",
    "용신", "희신", "기신", "운", "인성", "비겁"
]

def extract_concepts(text: str):
    return [c for c in CONCEPTS if c in text]

def extract_condition_result(text: str):
    """조건/결과 분리"""
    condition_patterns = [
        r"(.*가 .*를 제압하는.*구조)",
        r"(.*운에서.*)",
        r"(.*합.*|.*충.*|.*형.*|.*파.*|.*묘.*|.*공망.*|.*格.*|.*格은.*|.*용신.*)"
    ]
    result_patterns = [
        r"(.*발생한다)",
        r"(.*성공한다)",
        r"(.*발재한다)",
        r"(.*된다)",
        r"(.*좋다)",
        r"(.*불길하다)",
        r"(.*문제가 발생한다)",
        r"(.*관재.*|.*사업.*|.*이혼.*|.*합격.*|.*취업.*)"
    ]
    조건, 결과 = [], []
    for line in text.split('\n'):
        for pat in condition_patterns:
            m = re.match(pat, line)
            if m:
                조건.append(m.group(1))
        for pat in result_patterns:
            m = re.match(pat, line)
            if m:
                결과.append(m.group(1))
    return 조건, 결과

def extract_interpretation(text: str):
    """기존명리 vs 차별적 해석 구분"""
    기존, 차별 = [], []
    for line in text.split('\n'):
        if re.search(r"(기존명리|전통|교과서적|상식)", line):
            기존.append(line)
        elif re.search(r"(차별|특이|새로운|이 연구|본 연구|저자|집단)", line):
            차별.append(line)
    return 기존, 차별

def blockify(lines: List[str], filename: str) -> List[Dict[str, Any]]:
    """사례별/개념별/조건-결과/해석구분 포함 블록 구조"""
    blocks, block = [], None
    curr_page = None
    for line in lines:
        page_match = re.match(r".*page\s*(\d+)", line, re.IGNORECASE)
        if page_match:
            curr_page = int(page_match.group(1))
            continue
        if re.match(r'^<사례\s*\d+>|^사례\d*[\):]', line):
            if block: blocks.append(block)
            block = {
                "id": f"case-{len(blocks)+1:03d}",
                "type": "사례",
                "title": line,
                "concept": [],
                "팔자": [],
                "대운": [],
                "혼인관계": "",
                "자식관계": "",
                "본문": [],
                "조건": [],
                "결과": [],
                "기존명리해석": [],
                "차별적해석": [],
                "tags": [],
                "meta": {
                    "source": filename,
                    "page": curr_page
                }
            }
        elif block:
            block["concept"].extend(extract_concepts(line))
            block["본문"].append(line)
            # 팔자, 대운, 혼인관계, 자식관계 추출은 필요시 추가
        else:
            pass  # 사례 시작 전 해설문 등

    if block: blocks.append(block)

    # 조건-결과, 해석구분 추출 후 중복제거
    for b in blocks:
        all_text = "\n".join(b["본문"])
        b["조건"], b["결과"] = extract_condition_result(all_text)
        b["기존명리해석"], b["차별적해석"] = extract_interpretation(all_text)
        b["concept"] = list(set(b["concept"]))
        if "tags" in b: b["tags"] = list(set(b["tags"]))

    return blocks

def save_blocks_json(blocks: List[Dict], out_path: str):
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(blocks, f, ensure_ascii=False, indent=2)

def parse_file_to_blocks(txt_path):
    with open(txt_path, encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    filename = txt_path.split("/")[-1]
    return blockify(lines, filename)

if __name__ == "__main__":
    txt_path = "book5_v2.md"
    blocks = parse_file_to_blocks(txt_path)
    save_blocks_json(blocks, "book5_v2_분석_블록.json")
    print(f"총 {len(blocks)}건 저장 완료!")
