# 참고 강의 : https://github.com/teddylee777/langchain-kr/blob/main/12-RAG/00-RAG-Basic-PDF.ipynb

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import os
from dotenv import load_dotenv

# API 키 정보 로드
load_dotenv()

# PDF_FILE_PATH = "pdf/adison_introduce.pdf"
PDF_FILE_PATH = "../pdf/daejeon.pdf"

# 1. document load
loader = PyMuPDFLoader(PDF_FILE_PATH)
docs = loader.load()

# 2. document text split
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
splitted_docs = text_splitter.split_documents(docs)

# 3. embedding
embeddings = OpenAIEmbeddings()

# 4. create DB (vector store)
vectorstore = FAISS.from_documents(
    documents=splitted_docs,
    embedding=embeddings,
)

# "전화"와 유사한 내용을 vector store에서 검색
# for doc in vectorstore.similarity_search("전화"):
#     print(doc.page_content)

# 5: 검색기(Retriever) 생성
# 문서에 포함되어 있는 정보를 검색하고 생성합니다.
retriever = vectorstore.as_retriever()

# 검색기에 의해 질문에 대한 답변의 근거를 잘 찾는지 확인
# --> 전화는 3번(10초) 내에 받아야 한다는 내용을 찾아내는 것까지 확인함
# result = retriever.invoke("전화는 몇 초 내로 받아야 해?")
# print(result)

# 단계 6: 프롬프트 생성(Create Prompt)
# 프롬프트를 생성합니다.
prompt = PromptTemplate.from_template(
    """You are a assistant at the Daejeon Tourism Organization that provides information about company regulations.
Your role is to find and answer the user’s questions based on the context.

If you cannot find the answer in the documents, you must clearly respond that you do not know.

All responses must be in Korean.

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


#### 가상의 사용자가 질문 ####
# 체인 실행(Run Chain)
# 문서에 대한 질의를 입력하고, 답변을 출력합니다.
question = "공익 신고를 하기 위한 전화번호가 뭐야"
response = chain.invoke(question)
print(response)
# Model : gpt-3.5-turbo-0125
# Q1) 전화는 몇 초 내로 받아야 해?
# A1) 전화를 받을 때는 벨이 울리면 3번(10초) 이내에 받아야 합니다.

# Q2) 전화를 응대하는 방법에 대해서 순서대로 설명해줘
# A2) 전화를 받을 때, 벨이 울리면 3번(10초) 이내 전화를 받는다. 4회 / 10초 이상이면 양해 인사를 한다. "늦게 받아서 죄송합니다." 등 소속과 이름이 정확히 들리도록 인사한다. 필요에 따라 5W 1H에 의해 메모하면서 용건을 듣는다. 중요한 내용은 복창(인명, 지명, 연락처 등)하고 고객에게 재확인한다. 필요시 상대방의 인적사항을 정중히 확인한다. 상대가 먼저 끊는 것을 확인하고, 수화기를 내려 놓는다. 상대방 입장 (TPO : Time, Place, Occasion)을 고려해 전화를 걸어도 될지 생각한다. 필요한 자료와 서류를 준비해두고 메모용지와 필기구는 옆에 둔다. 상대의 수신을 확인 후, 인사말과 함께 자신의 소속과 이름을 밝힌다. 통화 중 전화가 끊기면 곧 다시 걸어 상대방이 기다리지 않게 한다. 용건이 복잡할 때는 요점을 재확인한다. 전화를 끊을 때 반드시 마무리 인사를 하고 조용히 수화기를 내려둔다.

# Q3) 대전의 유명한 관광지에 대해서 알려줘
# A3) 죄송합니다. 제가 알고 있는 정보에는 대전의 유명한 관광지에 대한 내용이 포함되어 있지 않습니다. 해당 정보를 찾아드릴 수 없습니다. 추가적인 도움이 필요하시면 다른 질문이나 문의사항이 있으시면 알려주세요. 감사합니다.

# Model : gpt-4o
# Q1) 전화는 몇 초 내로 받아야 해?
# A1) 전화는 벨이 울리면 3번(10초) 이내에 받아야 합니다.

# Q2) 전화를 응대하는 방법에 대해서 순서대로 설명해줘
# A2)
# 전화를 응대하는 방법은 다음과 같습니다:
# 1. 벨이 울리면 3번(10초) 이내에 전화를 받습니다. 만약 4회 이상 벨이 울렸다면, "늦게 받아서 죄송합니다." 등의 양해 인사를 합니다.
# 2. 소속과 이름이 정확히 들리도록 인사합니다. 예를 들어, "감사합니다, 대전관광공사 OOO팀 OOO입니다."
# 3. 필요에 따라 5W 1H에 의해 메모하면서 용건을 듣습니다. (Who, When, Where, What, Why, How)
# 4. 중요한 내용은 복창하고 고객에게 재확인합니다.
# 5. 필요시 상대방의 인적사항을 정중히 확인합니다.
# 6. 상대가 먼저 전화를 끊는 것을 확인하고, 수화기를 내려놓습니다.

# Q3) 대전의 유명한 관광지에 대해서 알려줘
# A3) 죄송하지만, 대전의 유명한 관광지에 대한 정보는 제공된 문서에 포함되어 있지 않습니다.
