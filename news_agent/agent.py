from langgraph.graph import StateGraph, START, END

from graph import search_news_articles, remove_duplicated_articles, summary_news_articles, \
    check_article_exist
from schema import NewsAgentState


class NewsAgent:
    def __init__(self):
        self.agent = None
        self.user_query = None
        self._graph = StateGraph(state_schema=NewsAgentState)
        self._build_agent()

    def execute(self, user_query):
        """
        유저가 던진 질문에 답변을 해주는 News agent
        기본적으로 사용자가 입력한 키워드 기반으로 뉴스들의 내용을 요약하여 정리해준다.
        :param user_query: 사용자 질문
        :return: 요약된 내용
        """
        self.user_query = user_query
        try:
            return self.agent.invoke({
                "input": user_query,
                "articles": [],
                "output": []
            })
        except Exception as e:
            return {
                "input": user_query,
                "articles": [],
                "output": [f"Error is occurred {str(e)}"]
            }

    def _get_user_input(self, state: NewsAgentState):
        return {"input": state["input"]}

    def _setup_nodes(self):
        """노드 설정"""
        self._graph.add_node("UserInput", self._get_user_input)
        self._graph.add_node("SearchNews", search_news_articles)
        self._graph.add_node("RemoveDuplicatedNews", remove_duplicated_articles)
        self._graph.add_node("SummaryNews", summary_news_articles)

    def _setup_edges(self):
        """엣지 설정"""
        self._graph.add_edge(START, "UserInput")
        self._graph.add_edge("UserInput", "SearchNews")
        self._graph.add_conditional_edges(
            "SearchNews",
            check_article_exist,
            {
                "existed": "RemoveDuplicatedNews",
                "not_existed": "UserInput"
            }
        )
        self._graph.add_edge("RemoveDuplicatedNews", "SummaryNews")
        self._graph.add_edge("SummaryNews", END)

    def _build_agent(self):
        self._setup_nodes()
        self._setup_edges()
        self.agent = self._graph.compile()
