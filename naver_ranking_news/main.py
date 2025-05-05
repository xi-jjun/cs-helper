import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

VECTOR_DB_NAME = "faiss_index"
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
OPEN_AI_MODEL = os.getenv("OPEN_AI_MODEL")


def get_naver_new_ranking():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    news_url = "https://news.naver.com/main/ranking/popularDay.naver?mid=etc&sid1=111"
    # 요청
    response = requests.get(news_url, headers=headers)
    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')
    # .list_content 클래스 요소 모두 찾기
    content_list = soup.select('.list_content')
    # 결과 출력 (예: 텍스트만)
    # 뉴스 제목과 링크 추출
    news_data = []
    for content in content_list:
        a_tag = content.find('a')
        if a_tag:
            title = a_tag.get_text(strip=True)
            url = a_tag['href']
            full_text = f"제목: {title} URL: {url}"
            news_data.append({
                'title': title,
                'url': url,
                'combined_text': full_text
            })
    return news_data


# 1. 네이버 랭킹 뉴스를 제목 및 링크를 추출해서 리스트로 반환함
news_data = get_naver_new_ranking()

# 2. 임베딩 요청
docs = [Document(page_content=item['combined_text'], metadata={"title": item['title'], "url": item['url']}) for item in
        news_data]

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.load_local(
    folder_path="./db",
    index_name=VECTOR_DB_NAME,
    embeddings=embeddings,
    allow_dangerous_deserialization=True,
)

if not vectorstore:
    vectorstore = FAISS.from_documents(
        documents=docs,
        embedding=embeddings,
    )
    vectorstore.save_local(folder_path="./db", index_name=VECTOR_DB_NAME)

retriever = vectorstore.as_retriever()

prompt = PromptTemplate.from_template(
    """너는 최신 인기 뉴스를 알려주는 뉴스 요약 챗봇이야.

사용자가 입력한 질문과 관련된 뉴스를 벡터 임베딩을 통해 찾아서 가장 관련도 높은 뉴스 제목과 링크를 제공해줘.

가능하면 사용자에게 친절하게 설명하고, 클릭할 수 있는 링크도 알려줘.

뉴스 제목만 요약하면 충분하다고 판단되면 제목만 출력해도 좋아.

뉴스의 전문은 너도 모르니, 링크만 안내하고 사실인 것처럼 단정적으로 말하지 마.

#Context: 
{context}

#Question:
{question}

#Answer:"""
)

# 단계 7: 언어모델(LLM) 생성
# 모델(LLM) 을 생성합니다.
llm = ChatOpenAI(model=OPEN_AI_MODEL, api_key=OPEN_AI_API_KEY)

# 단계 8: 체인(Chain) 생성
chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)

question = "김재준 들어간 뉴스 찾아줘"
response = chain.invoke(question)
print(response)
