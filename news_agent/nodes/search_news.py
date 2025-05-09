import os
from typing import List

from dotenv import load_dotenv
from tavily import TavilyClient
from datetime import datetime
from schema import Article

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def get_search_news_results(question: str) -> List[Article]:
    client = TavilyClient(api_key=TAVILY_API_KEY)
    response = client.search(
        query=question,
        search_depth="advanced",
        include_answer="basic",
        exclude_domains=["youtube"]
    )

    results = []
    for result in response.get("results"):
        published_at = datetime.strptime(result.get("published_date"), '%a, %d %b %Y %H:%M:%S GMT') if result.get("published_date") else None
        results.append(Article(title=result.get("title"), url=result.get("url"), published_at=published_at))
    return results

if __name__ == "__main__":
    news = get_search_news_results("한덕수 국무총리에 대한 뉴스 주라")
    print(news)

