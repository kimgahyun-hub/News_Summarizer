import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
import re


model_name = "lcw99/t5-base-korean-text-summary"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# 요약 파이프라인 설정
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# 네이버 API 키 설정
client_id = 'xIpH54vcwURuvzz8t0vl'
client_secret = 'dfHi2SP3CQ'

# API 요청 URL
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

# 사용자로부터 카테고리 선택 받기
print("카테고리를 선택하세요: 경제, IT, 과학, 사회, 문화, 스포츠, 건강")
user_choice = input("선택한 카테고리: ")

# 유효한 카테고리인지 확인
if user_choice in categories:
    selected_category = categories[user_choice]
else:
    print("유효하지 않은 카테고리입니다. 기본적으로 '경제' 카테고리를 선택합니다.")
    selected_category = '경제'

# 파라미터 설정
params = {
    'query': selected_category,  # 검색어
    'display': 5,            # 5개의 뉴스 가져오기
    'sort': 'date'           # 날짜 기준 정렬
}

# 헤더 설정
headers = {
    'X-Naver-Client-Id': client_id,
    'X-Naver-Client-Secret': client_secret
}

# 기사 내용 추출 함수
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve the web page. Status code: {response.status_code}")
            return ""

        soup = BeautifulSoup(response.content, 'html.parser')
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        text = soup.get_text(separator=' ')
        text = ' '.join(text.split())

        return text

    except requests.exceptions.RequestException as e:
        print(f"Error during requests to {url}: {str(e)}")
        return ""

# API 요청
response = requests.get(url, params=params, headers=headers)

# 응답을 JSON 형태로 파싱
data = response.json()

# 뉴스 정보 출력 및 기사 내용 추출
if 'items' in data:
    articles = data['items']
    for i, article in enumerate(articles, 1):
        title = article['title']
        description = article['description']
        link = article['link']
        pub_date = article['pubDate']

        print(f"뉴스 {i}:")
        print(f"제목: {title}")
        print(f"URL: {link}")
        print(f"발행일: {pub_date}")

        # URL에서 기사 텍스트 추출
        extracted_text = extract_text_from_url(link)

        if extracted_text:
            # KoBART 요약 기능
            summary = summarizer(extracted_text, max_length=300, min_length=100, do_sample=False)
            summary_text = summary[0]['summary_text']

            # 요약된 텍스트가 3000자를 넘지 않도록 자르기
            if len(summary_text) > 3000:
                summary_text = summary_text[:3000] + '...'

            print("내용 요약:")
            print(summary_text)

            # 키워드 추출 기능
            okt = Okt()

            def extract_keywords(text, num_keywords=5):
                text = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣\s]', '', text)
                nouns = okt.nouns(text)
                if not nouns:
                    return []
                vectorizer = TfidfVectorizer(max_features=num_keywords)
                tfidf_matrix = vectorizer.fit_transform([' '.join(nouns)])
                feature_names = vectorizer.get_feature_names_out()
                sorted_items = sorted(zip(vectorizer.idf_, feature_names))
                keywords = [item[1] for item in sorted_items[:num_keywords]]
                return keywords

            keywords = extract_keywords(summary_text, num_keywords=5)

            print(f"키워드: {keywords}")
        else:
            print("기사를 추출할 수 없습니다.")
        print("-" * 80)
else:
    print("뉴스를 가져오는데 실패했습니다.")