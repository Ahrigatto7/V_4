# 1. 필요 라이브러리 임포트
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# 2. 데이터 준비
texts = [
    "오늘 경기에서 손흥민 선수가 환상적인 골을 넣었습니다.",
    "정부의 새로운 부동산 정책이 발표되었습니다.",
    "AI 기술이 미래 산업의 핵심 동력이 될 것입니다.",
    "이번 월드컵 예선전은 치열한 접전이 예상됩니다.",
    "반도체 시장의 동향과 전망에 대한 분석 보고서입니다.",
    "여야는 예산안 처리를 두고 강하게 대립하고 있습니다."
]
labels = [0, 1, 2, 0, 2, 1]  # 0: 스포츠, 1: 정치, 2: IT/과학
category_names = {0: '스포츠', 1: '정치', 2: 'IT/과학'}

# 3. 한국어 토큰화 함수 정의
okt = Okt()
def okt_tokenizer(text):
    # 명사만 추출하여 반환
    return okt.nouns(text)

# 4. TF-IDF 벡터화
# 훈련 시 사용될 Vectorizer 객체를 전역적으로 생성
tfidf_vect = TfidfVectorizer(tokenizer=okt_tokenizer)
X_tfidf = tfidf_vect.fit_transform(texts)

# 5. 모델 훈련 및 평가
# 데이터를 훈련용과 테스트용으로 분리
# 샘플이 적어 전체 데이터로 훈련하고 테스트는 새로운 문장으로만 진행하겠습니다.
model = LogisticRegression()
model.fit(X_tfidf, labels)

print("모델 훈련이 완료되었습니다.")
print("-" * 30)


# 6. 새로운 문장 분류 함수
def classify_new_sentence(sentence):
    # 중요: 새로운 문장도 훈련 시 사용했던 동일한 TfidfVectorizer 객체로 변환
    sentence_tfidf = tfidf_vect.transform([sentence])
    prediction = model.predict(sentence_tfidf)
    return category_names[prediction[0]]

# 7. 분류 테스트
new_sentence1 = "이재용 회장이 새로운 AI 비전을 제시했다."
new_sentence2 = "국회에서 필리버스터가 시작되었다."
new_sentence3 = "이번 시즌 프로야구 우승팀은 어디일까?"

print("새로운 문장 분류 테스트:")
print(f"입력: '{new_sentence1}' \n-> 예측 결과: {classify_new_sentence(new_sentence1)}")
print(f"입력: '{new_sentence2}' \n-> 예측 결과: {classify_new_sentence(new_sentence2)}")
print(f"입력: '{new_sentence3}' \n-> 예측 결과: {classify_new_sentence(new_sentence3)}")