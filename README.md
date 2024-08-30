# 📰News_Summarizer


 :one:Project Introduction 
-------------


뉴스 기사 내용 요약 및 핵심 키워드 자동 생성 모델 제작, Streamlit 기반 UI 구현


🌏Development Environment
-------------


✔뉴스 모델 제작

-Jupyter Notebook

-Colab

-Python

✔UI 구현

-Streamlit

-Java

-Ollama


🗝Key features
-------------


-뉴스 카테고리 선택: 경제, IT, 과학, 사회, 문화, 스포츠, 건강

-선택된 카테고리의 인기 뉴스 기사 5개 수집

-각 기사의 요약 생성

-각 기사의 핵심 키워드 추출

-결과 시각화(출력)


👾Model Realization
-------------


-사용자가 카테고리를 선택하고 결과를 확인할 수 있는 웹 또는 모바일 인터페이스를 설계

-apa: 뉴스 기사 요약 및 핵심 키워드 추출

-apf: Ollama를 이용하여 뉴스 요점 정리


Architecture
============


# News Crawler

• Source

- 네이버 뉴스 API (free for 25k requests)

# News Analyzer

• html.paser: 구문 분석

# News Summarizer

• 한국어 Tokenizer: 텍스트 -> 문장 분리

• Huggingface 뉴스 요약 모델 사용

-t5-base 모델을 로드하여 한국어 텍스트 요약

# Keyword Extractor

• Okt(Open Korean Text) & TfidfVectorizer: 텍스트에서 핵심 키워드 추출

# UI Implementation

• konlpy를 사용하여 streamlit으로 웹페이지 구현

• ollama로 새로 작성한 코드로 streamlit으로 웹페이지 구현 -> 성능 향상


🧗‍♀️Future Work
-------------


-apa 코드 사용시 중간에 종종 발생하는 요약 오류 해결하기

-Ollama를 이용하여 뉴스의 핵심 키워드까지 추출하기
