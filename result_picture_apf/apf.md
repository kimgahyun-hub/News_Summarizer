News_Summarize Use Ollama
=============

Streamlit이라는 파이썬 웹 애플리케이션 프레임워크를 사용하여 뉴스 기사를 검색하고, 해당 기사 내용을 요약하고 번역하는 애플리케이션을 만드는 코드

Useage
-------------
먼저 Ollama가 사용하는 pc에 설치 되어 있어야함

여기서 Ollama 설치
        Ollama : <https://ollama.com/>

이 사이트 참고하여 llama3.1을 실행한다
        Ollama github : <https://github.com/ollama/ollama>

pc상에서 ollama 시작(여기서 llama3.1:8b 버전 사용):
  
    ollama run llama3.1:3b


http://localhost:11434 주소에서 실행 중인지 확인

    Ollama is running

이 문자가 나오면 실행 중 

자바 또한 설치되어 있어야 한다

Oracle Java : <https://www.oracle.com/kr/java/technologies/downloads/>

최신 버전의 맞는 os용 Installer를 설치하여 Java 설치

필요한 라이브러리
-------------

Streamlit (st): 사용자 인터페이스를 만드는 데 사용되는 라이브러리.

Requests (requests): HTTP 요청을 보내기 위한 라이브러리로, 네이버 API와 Ollama API에 요청을 보내기 위해 사용.

BeautifulSoup (bs4): HTML을 파싱하고 웹 페이지에서 텍스트를 추출하는 데 사용.

BeautifulSoup (bs4): HTML과 XML 파일을 파싱하기 위해 사용되는 라이브러리입니다. 뉴스 기사 웹 페이지에서 텍스트를 추출할 때 사용.
```
import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
```

API 키 설정
-------------

client_id 및 client_secret: 네이버 API에 접근하기 위해 필요한 인증 정보입니다. 실제 사용 시, 이 값들은 보안상 비공개로 유지해야 하며 환경 변수나 별도의 설정 파일로 관리하는 것이 좋다

ollama_base_url: Ollama API 서버의 기본 URL입니다. 로컬 호스트에서 실행 중인 서버로 연결되어 있습니다.

```
client_id = 'client_id'
client_secret = 'client_secret' // your_Api use
url = 'https://openapi.naver.com/v1/search/news.json' //API request url
ollama_base_url = 'http://localhost:11434'
```

뉴스기사 텍스트 추출
-------------

extract_text_from_url(url): 이 함수는 주어진 URL에서 텍스트를 추출하는 역할을 합니다.

response = requests.get(url): URL에 GET 요청을 보내어 웹 페이지의 내용을 가져옵니다.

status_code 확인: 만약 응답 코드가 200(성공)이 아니면 에러 메시지를 출력하고 빈 문자열을 반환합니다.

BeautifulSoup을 사용한 파싱: HTML 내용을 파싱하여 script와 style 태그를 제거한 뒤, 텍스트만 추출합니다.

텍스트 정리: 여러 공백을 하나로 줄이고, 정리된 텍스트를 반환합니다.

```
def extract_text_from_url(url):
    try:
        response = requests.get(url)
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
```

Streamlit UI 구성
-------------

st.title("뉴스 요약 및 분석"): 애플리케이션의 제목을 설정합니다.

categories: 사용자가 선택할 수 있는 뉴스 카테고리 목록을 딕셔너리 형태로 정의합니다. 이 목록에서 사용자는 특정 카테고리를 선택할 수 있습니다.

st.selectbox: 드롭다운 메뉴를 제공하여 사용자가 원하는 뉴스 카테고리를 선택할 수 있게 합니다.

```
st.title("뉴스 요약 및 분석") 

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

```

네이버 API 요청 및 결과 처리
-------------

url: 네이버 뉴스 검색 API의 엔드포인트 URL입니다.

params: API 요청 시 사용되는 파라미터입니다.

query: 선택된 카테고리를 기준으로 검색합니다.

display: 최대 5개의 기사를 반환하도록 설정합니다.

sort: 최신 뉴스부터 정렬합니다.

headers: 요청에 필요한 인증 정보를 담고 있는 헤더입니다.

st.button: 버튼을 클릭하면 뉴스 검색이 시작됩니다.

st.spinner: 뉴스 검색이 진행되는 동안 로딩 스피너를 표시합니다.

response: 네이버 API에 요청을 보내고, JSON 형식의 응답을 받습니다

```
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
    'X-Naver-Client-Id': client_id,  #고유 id사용
    'X-Naver-Client-Secret': client_secret
}

if st.button('뉴스 클릭'): #Streamlit
    with st.spinner('뉴스를 검색하고 있습니다. 잠시만 기다려 주세요...'):
        # API 요청
        response = requests.get(url, params=params, headers=headers)
        data = response.json()

```

뉴스 기사 정보 출력 및 요약/번역 처리
-------------

items: JSON 응답에서 뉴스 기사를 포함하는 항목을 가져옵니다.

enumerate: 각 기사를 순차적으로 처리합니다.

article: 뉴스 기사의 제목, 설명, 링크, 발행일을 추출합니다.

extracted_text: 이전에 정의한 extract_text_from_url 함수를 사용해 뉴스 기사에서 텍스트를 추출합니다.

article_text: Ollama API가 처리할 수 있도록 텍스트를 3000자 내로 잘라냅니다.

summary_response: Ollama API에 요약 요청을 보냅니다. 여기서는 스트리밍 모드를 사용해 응답을 조금씩 받아옵니다.

```
# 뉴스 정보 출력
if 'items' in data:
    articles = data['items']
    for i, article in enumerate(articles, 1): //extract new information
        title = article['title']
        description = article['description']
        link = article['link']
        pub_date = article['pubDate']

        # 기사 내용 추출 및 요약
        extracted_text = extract_text_from_url(link) #text extract to translate 
        if extracted_text:
            article_text = extracted_text[:3000]

            # 요약 요청
            try:
                summary_response = requests.post( #request Ollama API 
                    f"{ollama_base_url}/api/chat",
                    json={
                        "model": "llama3.1:8b",
                        "messages": [
                            {
                                "role": "user",
                                "content": f"Please analyze the text and summarize it around the important part : {article_text}",
                            },
                        ],
                    },
                    stream=True  # Enables streaming mode
                )

```

JSON 응답 처리 및 번역 요청
-------------
response_text: 응답을 스트리밍 방식으로 읽어와서 response_text에 저장합니다.

JSON 객체 분리: 응답 데이터를 하나의 문자열로 받고, 이를 여러 개의 JSON 객체로 분리하여 처리합니다.

summary_message: 분리된 JSON 객체들에서 요약된 내용을 추출하여 하나의 메시지로 결합합니다.

```
# Initialize an empty string to collect response data
response_text = ''

# Read the response in chunks and concatenate
for chunk in summary_response.iter_lines():
    if chunk:
        response_text += chunk.decode('utf-8')

# Split the concatenated response into individual JSON objects
json_objects = []
current_json = ''
inside_braces = 0

for char in response_text:
    if char == '{':
        inside_braces += 1
    elif char == '}':
        inside_braces -= 1
    current_json += char

    # Assuming that each JSON object ends with '}'
    if inside_braces == 0 and current_json.strip():
        try:
            json_objects.append(json.loads(current_json))
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON: {current_json}")
        current_json = ''

# Combine message contents from the JSON objects
summary_message = ''
for obj in json_objects:
    if 'message' in obj and 'content' in obj['message']:
        summary_message += obj['message']['content']

```

번역 요청
-------------

위의 요약 요청을 하는 코드 중에 API 요청을 하는 부분과 거의 같다

```
# 번역 요청
translate_response = requests.post(
    f"{ollama_base_url}/api/chat",
    json={
        "model": "llama3.1:8b",
        "messages": [
            {
                "role": "user",
                "content": f"and Please translate this into Korean: {summary_message}",
            },
        ],
    },
    stream=True  # Enables streaming mode
)

```

번역된 결과 출력
-------------

#### JSON 응답 처리 및 번역 요청 
과 동일한 코드 사용

### 추가된 코드

마지막 최종 결과 출력을 위한 코드 구현

```
# 결과 출력
st.subheader(f"뉴스 {i}:")
st.write(f"제목: {title}")
st.write(f"내용: {message}")
st.write(f"URL: {link}")
st.write(f"발행일: {pub_date}")
st.write("---")
```

오류 처리 및 예외 처리
-------------

오류가 발생했을시 오류 확인을 위한 코드 구현

### 예시

```
if inside_braces == 0 and current_json.strip():
        try:
            json_objects.append(json.loads(current_json)) #변역된 결과 출력 부분
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON: {current_json}")
        current_json = ''

try: #뉴스 기사에서 텍스트 추출 부분
        response = requests.get(url)
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
```

보완해야 할 부분
-------------

1. 실행 후 뉴스를 찾고 요약 및 번역하는 시간이 오래 걸림

2. 요약 및 해석한 결과 값이 이상하게 나올 때가 있음 -> content 부분에서 요청하는 부분을 더 세밀하게 하면 오류를 줄일 수 있을거 같다

3. 사용하는 pc에 Ollama 및 llama3.1이 설치 되어있어야한다 -> 무료라는 이점으로 사용하기는 하나 chatGPT라는 유료 사용처도 존재한다

   
















