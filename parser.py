import re
import pandas as pd

def parse_cases_from_lines(lines):
    cases = []
    case = None
    # 마크다운, <사례 n>, 사례 n) 등 다양한 패턴 지원
    case_start = re.compile(r'^<사례\s*\d+>|^사례\s*\d+[)번:：]?|^#{1,3}\s*사례\s*\d+')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if case_start.match(line):
            if case:
                cases.append(case)
            case = {"title": line, "body": []}
        elif case:
            case["body"].append(line)
    if case:
        cases.append(case)
    return cases

def split_case_body(body_lines):
    gan_str, ji_str, gender = "", "", ""
    daewoon_ages = ""
    daewoon_gans = ""
    daewoon_jis = ""
    gongmang = ""
    jaeap = ""
    hunin = ""
    jasik = ""
    goong = ""
    seong = ""
    maintext = []

    for i, line in enumerate(body_lines):
        line_strip = line.strip()
        # (1) 천간 4글자 (예: 甲戊己乙)
        if re.match(r"^[甲乙丙丁戊己庚辛壬癸]{4}", line_strip) and not gan_str:
            gan_str = line_strip[:4]
            m = re.search(r"\((남|여|乾|坤)\)", line_strip)
            if m:
                gender = m.group(1)
        # (2) 지지 4글자 (예: 寅辰卯巳)
        elif re.match(r"^[子丑寅卯辰巳午未申酉戌亥⺒⾠]{4}$", line_strip) and not ji_str:
            ji_str = line_strip[:4]
        # (3) 공망
        elif "공망" in line_strip or "空亡" in line_strip:
            gongmang = line_strip
        # (4) 대운 나이 (공백으로 구분된 8개 숫자)
        elif re.match(r"^\d{1,2}(\s+\d{1,2}){7,}", line_strip):
            daewoon_ages = line_strip
        # (5) 대운 천간 (연속 8글자)
        elif re.match(r"^[甲乙丙丁戊己庚辛壬癸]{8}$", line_strip):
            daewoon_gans = line_strip
        # (6) 대운 지지 (연속 8글자)
        elif re.match(r"^[子丑寅卯辰巳午未申酉戌亥⺒⾠]{8}$", line_strip):
            daewoon_jis = line_strip
        # (7) 제압방식
        elif "제압방식" in line_strip or "방식" in line_strip:
            jaeap = line_strip.replace("제압방식", "").replace("방식", "").replace(":", "").strip()
        # (8) 혼인관계
        elif line_strip.startswith("혼인관계"):
            hunin = line_strip.replace("혼인관계", "").replace(":", "").strip()
        # (9) 자식관계
        elif line_strip.startswith("자식관계"):
            jasik = line_strip.replace("자식관계", "").replace(":", "").strip()
        # (10) 궁
        elif line_strip.startswith("궁:"):
            goong = line_strip.replace("궁:", "").strip()
        # (11) 성
        elif line_strip.startswith("성:"):
            seong = line_strip.replace("성:", "").strip()
        # (12) 그 외(설명/해설문 등)
        else:
            maintext.append(line_strip)

    # 사주명국: 원본 천간/지지 각 줄 그대로 줄바꿈 포함 저장
    if gan_str and ji_str:
        saju_str = f"{gan_str}\n{ji_str}"
    elif gan_str:
        saju_str = gan_str
    elif ji_str:
        saju_str = ji_str
    else:
        saju_str = ""

    # 대운(3줄)
    if daewoon_ages and daewoon_gans and daewoon_jis:
        daewoon_str = f"{daewoon_ages}\n{daewoon_gans}\n{daewoon_jis}"
    else:
        daewoon_str = ""

    # 혼인관계 칸에 궁과 성 같이 표기
    hunin_full = ""
    if goong and seong:
        hunin_full = f"{goong} / {seong} / {hunin}"
    elif goong:
        hunin_full = f"{goong} / {hunin}"
    elif seong:
        hunin_full = f"{seong} / {hunin}"
    else:
        hunin_full = hunin

    return {
        "사주명국": saju_str,
        "성별": gender,
        "대운": daewoon_str,
        "공망": gongmang,
        "제압방식": jaeap,
        "혼인관계": hunin_full,
        "자식관계": jasik,
        "본문": "\n".join(maintext)
    }

def parse_book5_to_dataframe(txt_path):
    with open(txt_path, encoding="utf-8") as f:
        lines = f.readlines()
    cases = parse_cases_from_lines(lines)
    rows = []
    for case in cases:
        split_result = split_case_body(case["body"])
        row = {"사례명": case["title"]}
        row.update(split_result)
        rows.append(row)
    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    # 분석할 파일명만 바꾸면 됨 (txt/md 모두 지원)
    txt_path = "book5_v2.md"
    df = parse_book5_to_dataframe(txt_path)
    print(df.head(5))
    df.to_excel("book5_v2_분석_최종.xlsx", index=False)
    print("엑셀 저장 완료: book5_v2_분석_최종.xlsx")
