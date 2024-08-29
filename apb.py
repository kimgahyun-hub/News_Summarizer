import streamlit as st
import requests
from bs4 import BeautifulSoup
import ollama

# 네이버 API 키 설정 (비공개로 관리해야 합니다)
client_id = 'xIpH54vcwURuvzz8t0vl'
client_secret = 'dfHi2SP3CQ'

# Ollama API 설정
client = openapi(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)

# 뉴스 기사에서 텍스트 추출 함수
def extract_text_from_url(url):
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            st.error(f"웹 페이지를 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")
            return ""
        soup = BeautifulSoup(response.content, 'html.parser')
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        text = soup.get_text(separator=' ')
        text = ' '.join(text.split())
        return text
    except requests.exceptions.RequestException as e:
        st.error(f"요청 중 오류 발생: {str(e)}")
        return ""

# Streamlit 애플리케이션 디자인
st.title("뉴스 요약 및 번역기")

# 카테고리 매핑
categories = {
    '경제': '경제',
    'IT': 'IT',
    '과학': '과학',
    '사회': '사회',
    '문화': '문화',
    '스포츠': '스포츠',
    '건강': '건강'
}

# 사용자로부터 카테고리 선택 받기
selected_category = st.selectbox('뉴스 카테고리 선택', list(categories.keys()))

# API 요청 URL
url = 'https://openapi.naver.com/v1/search/news.json'

# 파라미터 설정
params = {
    'query': categories[selected_category],
    'display': 5,
    'sort': 'date'
}

# 헤더 설정
headers = {
    'X-Naver-Client-Id': client_id,
    'X-Naver-Client-Secret': client_secret
}

if st.button('뉴스 요약 및 번역'):
    with st.spinner('뉴스를 검색하고 있습니다. 잠시만 기다려 주세요...'):
        # API 요청
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        # 뉴스 정보 출력
        if 'items' in data:
            articles = data['items']
            for i, article in enumerate(articles, 1):
                title = article['title']
                description = article['description']
                link = article['link']
                pub_date = article['pubDate']

                # 기사 내용 추출 및 요약
                extracted_text = extract_text_from_url(link)
                if extracted_text:
                    article_text = extracted_text[:3000]

                    # 요약 요청
                    try:
                        summary_response = client.chat(
                            model=ollama_model,
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"Please analyze the text and summarize it around the important parts: {article_text}",
                                },
                            ],
                        )
                        summary1 = summary_response["message"]["content"]

                        # 번역 요청
                        translation_response = client.chat(
                            model=ollama_model,
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"Please translate this into Korean: {summary1}",
                                },
                            ],
                        )
                        summary2 = translation_response["message"]["content"]

                        # 결과 출력
                        st.subheader(f"뉴스 {i}:")
                        st.write(f"제목: {title}")
                        st.write(f"내용: {summary2}")
                        st.write(f"URL: {link}")
                        st.write(f"발행일: {pub_date}")
                        st.write("---")
                    except Exception as e:
                        st.error(f"API 요청 중 오류 발생: {str(e)}")
                else:
                    st.write(f"기사를 추출할 수 없습니다.")
        else:
            st.write("뉴스를 가져오는데 실패했습니다.")