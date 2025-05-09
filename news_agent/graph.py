import os

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from typing import Literal, Optional

from nodes.news_summary import NewsSummarizer, NewsArticle
from nodes.input import get_user_input_from_cli
from nodes.search_news import get_search_news_results
from schema import NewsAgentState

VALID_ARTICLE_COUNT = 3  # 3건 이상일 경우에만 응답해야 하는 요구사항 존재


# Node 정의
def get_user_input(state: NewsAgentState):
    """
    유저의 입력을 받는 노드
    :param state:
    :return:
    """
    user_input = get_user_input_from_cli()
    return {"input": user_input}


def search_news_articles(state: NewsAgentState):
    """
    뉴스 기사 정보를 가져오는 노드.
    가져오는 정보 : Article 클래스 참고
    :param state:
    :return:
    """
    print("search_news_articles")
    articles = get_search_news_results(state.get("input"))
    return {"articles": articles}


def check_article_exist(state: NewsAgentState) -> Literal["not_existed", "existed"]:
    """
    conditional edge function
    가져온 뉴스 기사가 1건 이상 존재하는지 확인.
    1건 미만일 경우, 다시 검색필요.
    :param state:
    :return: 1개라도 존재할 경우 existed, 없을 경우 not_existed 반환
    """
    if len(state["articles"]) >= VALID_ARTICLE_COUNT:
        return "existed"
    else:
        return "not_existed"


def remove_duplicated_articles(state: NewsAgentState):
    """
    중복된 뉴스 기사 제거
    :param state:
    :return:
    """
    print("remove_duplicated_articles")
    return {"articles": state["articles"]}


def summary_news_articles(state: NewsAgentState):
    """
    뉴스 기사 내용을 확인하여 3줄 요약, 최대 10개 (PoC 개념이기에, 무한정 늘어나도록 놔둘 이유가 없음)
    :param state:
    :return:
    """
    print("summary_news_articles")
    load_dotenv()
    summarizer = NewsSummarizer(api_key=os.environ['OPENAI_API_KEY'])

    results = []
    for article in state["articles"]:
        news_url = article.get('url')
        news_article = summarizer.extract_news_content(news_url)
        summarized_content: Optional[NewsArticle] = summarizer.summarize_article(news_article)
        results.append({
            "title": article.get('title'),
            "url": news_url,
            "summarized_content": summarized_content
        })

    return {"output": results}


graph = StateGraph(state_schema=NewsAgentState)
# Node 정의
graph.add_node("UserInput", get_user_input)
graph.add_node("SearchNews", search_news_articles)
graph.add_node("RemoveDuplicatedNews", remove_duplicated_articles)
graph.add_node("SummaryNews", summary_news_articles)

# graph edge 정의
graph.add_edge(START, "UserInput")
graph.add_edge("UserInput", "SearchNews")
graph.add_conditional_edges(
    "SearchNews",
    check_article_exist,
    {
        "existed": "RemoveDuplicatedNews",
        "not_existed": "UserInput"
    }
)
graph.add_edge("RemoveDuplicatedNews", "SummaryNews")
graph.add_edge("SummaryNews", END)

# compile
news_agent = graph.compile()

# 실행
# TODO : 테스트 용도로 일단 선언. 향후 streamlit 등으로 서비스 제공 시 수정 필요
if __name__ == '__main__':
    initial_state = {
        "input": "",
        "articles": [],
        "output": ""
    }
    result = news_agent.invoke(initial_state)
    print(result)
