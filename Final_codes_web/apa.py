import streamlit as st
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from konlpy.tag import Okt
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

# 키워드 추출 함수
def extract_keywords(text, num_keywords=5):
    text = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣\s]', '', text)
    okt = Okt()
    nouns = okt.nouns(text)
    if not nouns:
        return []

    # 명사 리스트를 공백으로 구분된 문자열로 변환
    nouns_text = ' '.join(nouns)

    # TfidfVectorizer를 사용하여 키워드 추출
    vectorizer = TfidfVectorizer(max_features=num_keywords)
    tfidf_matrix = vectorizer.fit_transform([nouns_text])
    feature_names = vectorizer.get_feature_names_out()
    sorted_items = sorted(zip(vectorizer.idf_, feature_names))
    keywords = [item[1] for item in sorted_items[:num_keywords]]
    return keywords

# Streamlit 애플리케이션
st.title('뉴스 요약 및 키워드 추출기')

# 카테고리 선택
user_choice = st.selectbox("카테고리를 선택하세요:", list(categories.keys()))
selected_category = categories[user_choice]

if st.button('뉴스 요약 및 키워드 추출'):
    with st.spinner('뉴스를 검색하고 있습니다. 잠시만 기다려 주세요...'):
        # 파라미터 설정
        params = {
            'query': selected_category,
            'display': 5,  # 최대 5개의 뉴스 표시
            'sort': 'date'
        }

        # 헤더 설정
        headers = {
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secret
        }

        # API 요청 및 응답 처리
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
            data = response.json()

            # 뉴스 정보 출력 및 기사 내용 추출
            if 'items' in data:
                articles = data['items']
                for i, article in enumerate(articles, 1):
                    title = re.sub('<.*?>', '', article['title'])  # HTML 태그 제거
                    link = article['link']
                    pub_date = article['pubDate']

                    st.subheader(f"뉴스 {i}: {title}")
                    st.write(f"URL: {link}")
                    st.write(f"발행일: {pub_date}")

                    # URL에서 기사 텍스트 추출
                    extracted_text = extract_text_from_url(link)

                    if extracted_text:
                        # 요약 기능
                        summary = summarizer(extracted_text, max_length=300, min_length=100, do_sample=False)
                        summary_text = summary[0]['summary_text']
                        st.write("내용 요약:")
                        st.write(summary_text)  # 요약된 텍스트 확인

                        # 키워드 추출 기능
                        keywords = extract_keywords(summary_text, num_keywords=5)
                        st.write("키워드:")
                        st.write(f"{', '.join(keywords)}")  # 추출된 키워드 확인
                    else:
                        st.write("기사를 추출할 수 없습니다.")
                    st.write("---")
            else:
                st.write("뉴스를 가져오는데 실패했습니다.")
        except requests.exceptions.RequestException as e:
            st.write(f"API 요청 중 오류 발생: {e}")
