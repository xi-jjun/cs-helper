import os
from typing import List

from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from tavily import TavilyClient
from datetime import datetime
from schema import Article

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

prompt_template = """
당신은 뉴스 검색 결과를 분석하는 전문가입니다.

다음은 사용자가 입력한 뉴스 검색 질문입니다:
"{question}"

그리고 이것은 위 질문에 대해 뉴스 검색 API로부터 받은 답변입니다:
"{answer}"

이 답변이 유의미한 뉴스 정보(기사, 출처 등)를 제공한다고 판단되면 "YES"만 출력하고,
유의미한 정보가 없거나 관련성이 낮다면 "NO"만 출력하세요.
"""

prompt = PromptTemplate.from_template(prompt_template)

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0
)

chain = prompt | llm

def get_search_news_results(question: str, api_key=TAVILY_API_KEY) -> List[Article]:
    client = TavilyClient(api_key=api_key)
    response = client.search(
        query=question,
        search_depth="advanced",
        include_answer="basic",
        topic="news",
        exclude_domains=["youtube"]
    )

    answer = response.get("answer", "")
    result = chain.invoke({"question": question, "answer": answer})

    is_valid = result.content

    results = []
    if is_valid == "NO":
        return results

    for result in response.get("results"):
        published_at = datetime.strptime(result.get("published_date"), '%a, %d %b %Y %H:%M:%S GMT') if result.get("published_date") else None
        results.append(Article(title=result.get("title"), url=result.get("url"), published_at=published_at))
    return results

if __name__ == "__main__":
    # news = get_search_news_results("한덕수 국무총리에 대한 뉴스 주라")
    news = get_search_news_results("1490년 세종대왕 맥북 던짐 사태 알려주라")
    print(news)

