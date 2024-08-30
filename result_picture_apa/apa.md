News_Summarizer
-------------

이 프로젝트는 뉴스 기사를 검색하고, 해당 기사의 내용을 요약한 뒤, 주요 키워드를 추출하는 웹 애플리케이션입니다. 사용자는 선택한 카테고리에서 최신 뉴스를 검색하고, 요약된 내용과 주요 키워드를 확인할 수 있습니다. 이 애플리케이션은 Python을 기반으로 Streamlit을 사용하여 개발되었습니다.

필수 패키지 설치
-------------

필요한 Python 패키지를 설치합니다. 
'''
pip install streamlit
pip install requests
pip install beautifulsoup4
pip install transformers
pip install konlpy
pip install scikit-learn
'''

Streamlit 앱 실행
-------------

'''
streamlit run apa.py
'''

파일 설명
-------------

apa.py 파일은 뉴스 기사를 검색하고, 해당 기사의 내용을 요약한 후 주요 키워드를 추출하는 Streamlit 웹 애플리케이션입니다. 
#필요한 라이브러리 임포트

