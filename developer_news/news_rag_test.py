# 뉴스 1개 가져와서 RAG 로 상호작용 할 수 있는 chatbot 만들기

import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import os
from dotenv import load_dotenv

# API 키 정보 로드
load_dotenv()

# MODEL_NAME="gemma3:4b"
VECTOR_DB_NAME = "faiss_index"

news_url = 'https://blog.pragmaticengineer.com/software-architecture-is-overrated/'

# WebBaseLoader : https://python.langchain.com/docs/integrations/document_loaders/web_base/
loader = WebBaseLoader(news_url)
docs = loader.load()

# 2. document text split
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
splitted_docs = text_splitter.split_documents(docs)

# 3. embedding
embeddings = OllamaEmbeddings(model="dolphin-llama3:8b")

# 4. create DB (vector store)
# 사용법 : https://wikidocs.net/234014
vectorstore = FAISS.load_local(
    folder_path="./db",
    index_name=VECTOR_DB_NAME,
    embeddings=embeddings,
    allow_dangerous_deserialization=True,
)

if not vectorstore:
    vectorstore = FAISS.from_documents(
        documents=splitted_docs,
        embedding=embeddings,
    )
    vectorstore.save_local(folder_path="./db", index_name=VECTOR_DB_NAME)

# 5: 검색기(Retriever) 생성
# 문서에 포함되어 있는 정보를 검색하고 생성합니다.
retriever = vectorstore.as_retriever()

# 단계 6: 프롬프트 생성(Create Prompt)
# 프롬프트를 생성합니다.
prompt = PromptTemplate.from_template(
    """You must act as an assistant who understands the latest development trends and technologies.
You will receive written content and answer user questions about it in detail.
All responses must be provided in Korean only.

#Context: 
{context}

#Question:
{question}

#Answer:"""
)

# 단계 7: 언어모델(LLM) 생성
# 모델(LLM) 을 생성합니다.
llm = ChatOpenAI(model_name=os.environ['OPENAI_MODEL'], temperature=0)

# 단계 8: 체인(Chain) 생성
chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)

question = "2년차 개발자인 나에게 좋은 시니어 개발자가 될 수 있도록 가장 도움이 되는 내용을 요약해서 나에게 알려줘"
response = chain.invoke(question)
print(response)

# 결과
## Model : GPT-3.5-turbo-0125
# Q1) 이 글을 5줄로 요약해줘
# A1) 소프트웨어 아키텍처가 과대평가되고 명확하고 간단한 디자인이 과소평가된다. 새로운 프로젝트를 시작할 때, 가능한 간단한 디자인을 고려하고 복잡성을 피하는 것이 중요하다. 소프트웨어 아키텍처의 최선의 실천 방법과 기업 아키텍처 패턴은 유용하지만, 시작부터 간단하게 유지하는 것이 좋다. 이 글은 러시아어로 Habr에서, 중국어로 InfoQ China에서 번역본을 확인할 수 있다.
# Q2) 시스템을 설계하는 것의 목적을 이 글에서는 뭐라고 해?
# A2) 시스템을 설계하는 목적은 "가장 간단한 가능한 디자인을 어떻게 만들 수 있을지, 누구에게나 이해하기 쉬운 방식으로" 생각하는 것이라고 이 글에서 언급하고 있습니다. 소프트웨어 아키텍처의 최선의 실천 방법, 기업 아키텍처 패턴 및 시스템을 설명하는 형식화된 방법은 알아두면 유용한 도구이며 언젠가 유용할 수 있습니다. 그러나 시스템을 설계할 때는 가능한 간단하게 시작하고 최대한 간단하게 유지하는 것이 중요하다고 강조하고 있습니다.
# Q3) 2년차 개발자인 나에게 좋은 시니어 개발자가 될 수 있도록 가장 도움이 되는 내용을 요약해서 나에게 알려줘
# A3)
# 2년차 개발자가 좋은 시니어 개발자가 되기 위해 도움이 될 내용은 다음과 같습니다:
# 1. 새로운 프로젝트를 시작할 때, 가능한 간단한 디자인을 고려하고 복잡성을 피하는 것이 중요합니다.
# 2. 소프트웨어 아키텍처의 최신 동향과 기술을 이해하고, 간단하고 명확한 디자인을 중시하는 것이 중요합니다.
# 3. 성장을 위해 경험 많은 개발자들과의 네트워킹을 유지하고, 성장을 위한 조언을 받는 것이 도움이 됩니다.
# 4. 기술 뉴스레터나 기술 관련 자료를 꾸준히 읽고 최신 동향을 파악하는 것이 중요합니다.
# 5. 책이나 온라인 자료를 통해 지식을 쌓고, 새로운 기술에 대한 이해를 높이는 것이 시니어 개발자로 성장하는 데 도움이 됩니다.
