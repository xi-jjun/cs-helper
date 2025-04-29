from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

class PDFQASystem:
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
        self.embeddings = OllamaEmbeddings(model=model_name)
        self.llm = Ollama(model=model_name)
        self.vector_store = None
        
    def load_pdf(self, pdf_path: str):
        """PDF 파일을 로드하고 청크로 분할"""
        # PDF 로드
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        
        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_documents(documents)
        
        # FAISS Vectorstore 생성
        self.vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )
        
        print(f"PDF 로드 완료: {len(chunks)}개의 청크로 분할됨")
        
        # FAISS 인덱스 저장 (선택사항)
        # self.vector_store.save_local("faiss_index")
        
    def load_vectorstore(self, index_path: str = "faiss_index"):
        """저장된 FAISS 인덱스 로드 (선택사항)"""
        if os.path.exists(index_path):
            self.vector_store = FAISS.load_local(
                index_path,
                self.embeddings
            )
            print("기존 FAISS 인덱스를 로드했습니다.")
        
    def setup_qa_chain(self):
        """QA 체인 설정"""
        prompt_template = """
        You are a assistant at the Daejeon Tourism Organization that provides information about company regulations.
        Your role is to find and answer the user’s questions based on the context.

        If you cannot find the answer in the documents, you must clearly respond that you do not know.

        All responses must be in Korean.

        You must answer the question based on the context.
        Do not answer not related to given context.
        Do your best to answer the question.

        #Context: 
        {context}

        #Question:
        {question}

        #Answer:
        """

        prompt = PromptTemplate.from_template(prompt_template)
        chain = (
            {"context": self.vector_store.as_retriever(), "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain
        
    def answer_question(self, question: str):
        """질문에 답변"""
        if not self.vector_store:
            return "PDF를 먼저 로드해주세요."
            
        qa_chain = self.setup_qa_chain()
        response = qa_chain.invoke(question)
        
        print("\n=== 질문 ===")
        print(question)
        print("\n=== 답변 ===")
        print(response)

def main():
    # QA 시스템 초기화
    qa_system = PDFQASystem(model_name="dolphin-llama3:8b")  # 또는 다른 Ollama 모델 사용 가능
    
    # PDF 로드
    pdf_path = "../pdf/daejeon.pdf"  # PDF 파일 경로를 지정해주세요
    qa_system.load_pdf(pdf_path)
    
    # 대화형 질문-답변 루프
    print("\nPDF 문서에 대해 질문해주세요. (종료하려면 'quit' 입력)")
    while True:
        question = input("\n질문: ")
        if question.lower() == 'quit':
            break
            
        qa_system.answer_question(question)

if __name__ == "__main__":
    main()
