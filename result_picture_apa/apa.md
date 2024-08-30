News_Summarize Use Hugging Face
=============

이 프로젝트는 뉴스 기사를 검색하고, 해당 기사의 내용을 요약한 뒤, 주요 키워드를 추출하는 웹 애플리케이션입니다. 사용자는 선택한 카테고리에서 최신 뉴스를 검색하고, 요약된 내용과 주요 키워드를 확인할 수 있습니다. 이 애플리케이션은 Python을 기반으로 Streamlit을 사용하여 개발되었습니다.

Useage
-------------

자바가 설치되어 있어야 한다

Oracle Java : <https://www.oracle.com/kr/java/technologies/downloads/>

최신 버전의 맞는 os용 Installer를 설치하여 Java 설치 (2024 8월 기준 최신 버전 : 22.0.2)

필요한 라이브러리
-------------

-Streamlit: 웹 애플리케이션을 쉽게 만들기 위한 프레임워크.

-Requests: HTTP 요청을 보내기 위해 사용.

-BeautifulSoup: 웹페이지에서 텍스트를 추출하기 위해 사용.

-Hugging Face Transformers: 사전 훈련된 T5 모델을 사용하여 텍스트 요약.

-KoNLPy (Okt): 한국어 자연어 처리를 위한 라이브러리, 명사 추출에 사용.

-Scikit-learn: TF-IDF를 이용하여 텍스트에서 키워드를 추출.

-re: 정규 표현식을 사용하기 위한 라이브러리로, 텍스트 처리에 사용.

```

import streamlit as st
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
import re

```

네이버 API 키 설정
-------------

-client_id와 client_secret: 네이버에서 제공하는 API 키입니다. 실제 실행 시에는 네이버 개발자 센터에서 발급받은 API 키를 입력해야 합니다.
-url: 네이버 뉴스 검색 API의 엔드포인트입니다.

<pre>
<code>
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
url = 'https://openapi.naver.com/v1/search/news.json'
</code>
</pre>

모델 및 토크나이저 설정
-------------

-model_name: 한국어 텍스트 요약을 위해 사전 훈련된 T5 모델의 이름입니다.
-AutoTokenizer 및 AutoModelForSeq2SeqLM: 해당 모델과 토크나이저를 로드하여 요약 작업을 수행할 수 있도록 설정합니다.
-pipeline: 요약 작업을 수행할 파이프라인을 정의합니다.

```
model_name = "lcw99/t5-base-korean-text-summary"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
```

카테고리 설정
-------------

<pre>
<code>
categories = {
    '경제': '경제',
    'IT': 'IT',
    '과학': '과학',
    '사회': '사회',
    '문화': '문화',
    '스포츠': '스포츠',
    '건강': '건강'
}
</code>
</pre>

기사 내용 추출
-------------

-extract_text_from_url(url): 주어진 URL에서 기사 내용을 추출하는 함수입니다.

-requests.get(url): HTTP GET 요청을 보내 웹페이지의 콘텐츠를 가져옵니다.

-BeautifulSoup: HTML 문서를 파싱하여 텍스트를 추출합니다. script와 style 태그는 제거하여 가독성을 높입니다.

-예외 처리: 요청이 실패한 경우 빈 문자열을 반환합니다.


'''

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
        
'''


키워드 추출
-------------

-extract_keywords(text, num_keywords=5): 주어진 텍스트에서 주요 키워드를 추출하는 함수입니다.

-정규 표현식: 텍스트에서 한글과 공백 이외의 문자를 제거합니다.

-Okt: 텍스트에서 명사만을 추출합니다.

-TF-IDF: 명사들 중에서 중요한 키워드를 추출하기 위해 TF-IDF 알고리즘을 사용합니다.

'''

def extract_keywords(text, num_keywords=5):
    text = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣\s]', '', text)
    okt = Okt()
    nouns = okt.nouns(text)
    if not nouns:
        return []

    nouns_text = ' '.join(nouns)

    vectorizer = TfidfVectorizer(max_features=num_keywords)
    tfidf_matrix = vectorizer.fit_transform([nouns_text])
    feature_names = vectorizer.get_feature_names_out()
    sorted_items = sorted(zip(vectorizer.idf_, feature_names))
    keywords = [item[1] for item in sorted_items[:num_keywords]]
    return keywords
    
'''

Streamlit 애플리케이션
-------------

-st.title: 애플리케이션의 제목을 설정합니다.
-st.selectbox: 사용자가 카테고리를 선택할 수 있는 드롭다운 메뉴를 제공합니다.
-st.button: 버튼을 클릭하면 뉴스 검색, 요약, 키워드 추출 작업이 수행됩니다.
-with st.spinner: 뉴스 검색 중일 때 로딩 스피너를 표시합니다.
-params: 네이버 뉴스 검색 API에 보낼 쿼리 파라미터를 설정합니다. 여기서는 선택된 카테고리로 최신 뉴스 5개를 가져옵니다.
-headers: API 요청에 필요한 헤더를 설정합니다.
-API 요청 및 예외 처리: 뉴스 검색 API 요청을 보내고, 결과를 JSON 형태로 받아옵니다. 예외가 발생할 경우, 오류 메시지를 출력합니다.
-기사 정보 출력: 검색된 각 뉴스 기사에 대해 제목, URL, 발행일을 출력합니다.
-기사 텍스트 추출: 기사 내용이 성공적으로 추출되면, 요약 및 키워드 추출 기능을 수행합니다.
-st.write: 요약된 내용과 추출된 키워드를 화면에 출력합니다.

'''

st.title('뉴스 요약 및 키워드 추출기')

user_choice = st.selectbox("카테고리를 선택하세요:", list(categories.keys()))
selected_category = categories[user_choice]

if st.button('뉴스 요약 및 키워드 추출'):
    with st.spinner('뉴스를 검색하고 있습니다. 잠시만 기다려 주세요...'):
        params = {
            'query': selected_category,
            'display': 5,
            'sort': 'date'
        }

        headers = {
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secret
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            if 'items' in data:
                articles = data['items']
                for i, article in enumerate(articles, 1):
                    title = re.sub('<.*?>', '', article['title'])
                    link = article['link']
                    pub_date = article['pubDate']

                    st.subheader(f"뉴스 {i}: {title}")
                    st.write(f"URL: {link}")
                    st.write(f"발행일: {pub_date}")

                    extracted_text = extract_text_from_url(link)

                    if extracted_text:
                        summary = summarizer(extracted_text, max_length=300, min_length=100, do_sample=False)
                        summary_text = summary[0]['summary_text']
                        st.write("내용 요약:")
                        st.write(summary_text)

                        keywords = extract_keywords(summary_text, num_keywords=5)
                        st.write("키워드:")
                        st.write(f"{', '.join(keywords)}")
                    else:
                        st.write("기사를 추출할 수 없습니다.")
                    st.write("---")
            else:
                st.write("뉴스를 가져오는데 실패했습니다.")
        except requests.exceptions.RequestException as e:
            st.write(f"API 요청 중 오류 발생: {e}")
            
'''

보완해야 할 부분
-------------

1. 가끔씩 관련없는 용어들이 내용요약을 거쳐 키워드 추출에도 영향을 주는 경우가 있다.

2. 카테고리 관련 뉴스 말고 최근 뉴스로 나온다.

3. JAVA를 깔아야 한다는 단점이 있다.

4. 사용자만 웹 페이지에 들어갈 수 있다. (다른사람 이용 불가)
   
















