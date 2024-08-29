# app.py 수정된 코드
import streamlit as st
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# 모델 및 토크나이저 설정
model_name = "lcw99/t5-base-korean-text-summary"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# 네이버 API 키 설정
client_id = 'xIpH54vcwURuvzz8t0vl'
client_secret = 'dfHi2SP3CQ'
url = 'https://openapi.naver.com/v1/search/news.json'

# 카테고리 설정
categories = {
    '경제': '경제',
    'IT': 'IT',
    '과학': '과학',
    '사회': '사회',
    '문화': '문화',
    '스포츠': '스포츠',
    '건강': '건강'
}

# 기사 내용 추출 함수
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return ""
        soup = BeautifulSoup(response.content, 'html.parser')
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        text = soup.get_text(separator=' ')
        text = ' '.join(text.split())
        return text
    except requests.exceptions.RequestException:
        return ""

# 키워드 추출 함수 (새로운 방법 사용)
def extract_keywords(text, num_keywords=5):
    words = re.findall(r'\b[가-힣]{2,}\b', text)
    if not words:
        return []

    vectorizer = TfidfVectorizer(max_features=num_keywords)
    tfidf_matrix = vectorizer.fit_transform([' '.join(words)])
    feature_names = vectorizer.get_feature_names_out()
    sorted_items = sorted(zip(vectorizer.idf_, feature_names))
    keywords = [item[1] for item in sorted_items[:num_keywords]]
    return keywords

# Streamlit 앱 구성
st.title('뉴스 기사 요약 및 키워드 추출기')
st.write('네이버 뉴스 API를 이용하여 기사를 검색하고 요약 및 키워드를 추출합니다.')

# 카테고리 선택 UI
selected_category = st.selectbox('카테고리를 선택하세요:', list(categories.keys()))

# 사용자가 카테고리를 선택하면 실행
if st.button('뉴스 요약 및 키워드 추출'):
    # API 요청 파라미터 설정
    params = {'query': categories[selected_category], 'display': 5, 'sort': 'date'}
    headers = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret}

    # API 요청 보내기
    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    # 뉴스 기사 정보 출력
    if 'items' in data:
        articles = data['items']
        for i, article in enumerate(articles, 1):
            st.write(f"### 뉴스 {i}:")
            st.write(f"**제목:** {article['title']}")
            st.write(f"**URL:** {article['link']}")
            st.write(f"**발행일:** {article['pubDate']}")

            # 기사 내용 추출
            extracted_text = extract_text_from_url(article['link'])

            if extracted_text:
                # 요약 생성
                summary = summarizer(extracted_text, max_length=300, min_length=100, do_sample=False)
                summary_text = summary[0]['summary_text']
                st.write(f"**내용 요약:** {summary_text}")

                # 키워드 추출
                keywords = extract_keywords(summary_text, num_keywords=5)
                st.write(f"**키워드:** {', '.join(keywords)}")
            else:
                st.write("기사를 추출할 수 없습니다.")
            st.write("---")
    else:
        st.write("뉴스를 가져오는데 실패했습니다.")
