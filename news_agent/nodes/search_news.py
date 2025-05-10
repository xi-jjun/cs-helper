import os
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
from datetime import datetime
from schema import Article

load_dotenv()

class NewsSearcher:
    def __init__(self, tavily_api_key="", openai_api_key="", model=""):
        self.tavily_api_key = tavily_api_key
        self.openai_api_key = openai_api_key
        self.client = TavilyClient(api_key=self.tavily_api_key)

        prompt_template = """
        당신은 뉴스 검색 결과를 분석하는 전문가입니다.

        아래는 뉴스 검색 API로부터 받은 답변입니다:
        "{answer}"

        뉴스 API의 답변에서 정보를 찾을 수 없다는 얘기가 나오면 "NO"를 출력하고,
        그 외에는 YES라고 대답해주세요.
        """
        self.prompt = PromptTemplate.from_template(prompt_template)
        self.llm = ChatOpenAI(api_key=openai_api_key, model=model, temperature=0)
        self.chain = self.prompt | self.llm

    def _is_valid_answer(self, answer: str) -> bool:
        result = self.chain.invoke({"answer": answer})
        print("미추겠네")
        print(result)
        return result.content.strip() == "YES"

    def get_news_results(self, question: str) -> List[Article]:
        response = self.client.search(
            query=question,
            search_depth="advanced",
            include_answer="basic",
            exclude_domains=["youtube"],
        )

        answer = response.get("answer", "")
        print("외않돼1")
        print(answer)
        if not self._is_valid_answer(answer):
            return []

        results = []
        for result in response.get("results", []):
            published_date_str = result.get("published_date")
            published_at = None
            if published_date_str:
                try:
                    published_at = datetime.strptime(published_date_str, '%a, %d %b %Y %H:%M:%S GMT')
                except ValueError as e:
                    print(str(e))

            results.append(Article(
                title=result.get("title"),
                url=result.get("url"),
                published_at=published_at
            ))
        print("정신나가ㅏㅏㅏㅏㅏ")
        print(results)
        return results


if __name__ == "__main__":
    # news = get_search_news_results("한덕수 국무총리에 대한 뉴스 주라")
    load_dotenv()
    searcher = NewsSearcher(os.getenv("TAVILY_API_KEY"), os.getenv("OPENAI_API_KEY"), os.getenv("OPEN_AI_MODEL"))
    news = searcher.get_news_results("1490년 세종대왕 맥북 던짐 사태 알려주라")
    # news = searcher.get_news_results("한덕수 국무총리에 대한 뉴스 주라")
    print(news)