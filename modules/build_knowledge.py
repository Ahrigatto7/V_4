import os
import re
import json

def read_lines(filename):
    with open(filename, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def blockify(lines, filename):
    blocks, block = [], None
    for line in lines:
        if re.match(r'^<사례\s*\d+>|^사례\d*[\):]', line):
            if block: blocks.append(block)
            block = {"type":"사례", "title":line, "팔자":[], "대운":[], "본문":[], "tags":[], "meta":{"source":filename}}
        elif block:
            if re.match(r"^[甲乙丙丁戊己庚辛壬癸⼀-⿕]+.*[(乾)(坤)]?$", line): block["팔자"].append(line)
            elif re.match(r"^[戌亥子丑寅卯申未午酉辰巳⺒]+$", line): block["팔자"].append(line)
            elif line.startswith("대운"): continue
            elif re.match(r"^[甲乙丙丁戊己庚辛壬癸⼀-⿕]+", line): block["대운"].append(line)
            elif re.match(r"^[戌亥子丑寅卯申未午酉辰巳⺒]+", line): block["대운"].append(line)
            elif "제압방식" in line or "구조" in line or "格" in line:
                block["tags"].extend(re.findall(r"[傷官印財比劫官殺格構造제압적포귀격합충파형穿墓공망운응기생극화허투]", line))
                block["본문"].append(line)
            else: block["본문"].append(line)
        else:
            blocks.append({"type":"해설문", "text":line, "meta":{"source":filename}})
    if block: blocks.append(block)
    for b in blocks:
        if "tags" in b: b["tags"] = list(set(b["tags"]))
    return blocks

def merge_blocks(existing, new):
    seen, merged = set(), []
    for b in existing + new:
        key = json.dumps(b, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            merged.append(b)
            seen.add(key)
    return merged

def main():
    # 분석할 파일 리스트(같은 폴더)
    input_files = [
        "Book2.txt",  # 예시
        # "Book3.md", ...
    ]
    output_file = "명리_사례_해설_군집.json"

    # 이전 누적결과 불러오기
    if os.path.exists(output_file):
        with open(output_file, encoding="utf-8") as f:
            existing_blocks = json.load(f)
    else:
        existing_blocks = []

    new_blocks = []
    for fname in input_files:
        lines = read_lines(fname)
        new_blocks.extend(blockify(lines, fname))
    merged = merge_blocks(existing_blocks, new_blocks)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"{output_file}에 {len(merged)}건 저장됨.")

if __name__ == "__main__":
    main()
