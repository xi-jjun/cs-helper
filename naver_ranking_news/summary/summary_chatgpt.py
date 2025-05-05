import os
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 1. API 키 로드
load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
OPEN_AI_MODEL = os.getenv("OPEN_AI_MODEL")

# 2. 기사 URL 설정
news_url = "https://n.news.naver.com/article/011/0004481676?ntype=RANKING"

# 3. 기사 내용 불러오기
loader = WebBaseLoader(news_url)
docs = loader.load()

# 4. 텍스트 분할 (너무 길 경우 대비)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
splitted_docs = text_splitter.split_documents(docs)

# 5. 문서 내용 합치기 (1개의 스트링으로)
article_text = "\n\n".join([doc.page_content for doc in splitted_docs])

# 6. 프롬프트 작성
prompt = PromptTemplate.from_template(
    """
너는 뉴스 요약 전문가야. 아래는 네이버 뉴스 기사야. 
이 기사를 **객관적이고 간결한 다섯 문장**으로 요약해 줘.

조건:
- 핵심 사실, 원인, 배경, 결과 위주로 요약할 것
- 없는 내용은 말하지 말 것
- 결과는 마크다운 리스트 문법으로 출력할 것

[기사 원문]
{article}
"""
)

# 7. LLM 생성
llm = ChatOpenAI(model_name=OPEN_AI_MODEL, api_key=OPEN_AI_API_KEY, temperature=0)

# 8. 체인 구성
chain = (
    {"article": lambda _: article_text}
    | prompt
    | llm
    | StrOutputParser()
)

# 9. 실행
response = chain.invoke({})
print(response)
