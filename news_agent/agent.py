from langgraph.graph import StateGraph, START, END

from nodes.news_summary import NewsSummarizer
from nodes.search_news import NewsSearcher
from schema import NewsAgentState


class NewsAgent:
    def __init__(self, tavily_api_key="", openai_api_key="", llm_model="gpt-3.5-turbo-0125"):
        self.tavily_api_key = tavily_api_key
        self.openai_api_key = openai_api_key
        self.llm_model = llm_model
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

    # TODO : 사실상 필요없는 노드여서 삭제 필요
    def _get_user_input(self, state: NewsAgentState):
        return {"input": state["input"]}

    def _search_news_articles(self, state: NewsAgentState):
        print('_search_news_articles')
        question = state["input"]
        searcher = NewsSearcher(tavily_api_key=self.tavily_api_key, openai_api_key=self.openai_api_key,
                                model=self.llm_model)
        articles = searcher.get_news_results(question)
        # TODO : 전체 기사가 아닌 특정 몇몇 건에 대해서만 요약하도록 건수 제한 처리 추가 필요
        return {"articles": articles}

    def _remove_duplicated_articles(self, state: NewsAgentState):
        print('_remove_duplicated_articles')
        is_existed = set()
        result = []
        for article in state["articles"]:
            news_url = article["url"]
            if news_url not in is_existed:
                is_existed.add(news_url)
                result.append(article)

        return {"articles": result}

    def _summary_news_articles(self, state: NewsAgentState):
        print('_summary_news_articles')
        summarizer = NewsSummarizer(api_key=self.openai_api_key, llm_model=self.llm_model)
        results = []

        for article in state["articles"]:
            news_url = article.get('url')
            news_article = summarizer.extract_news_content(news_url)
            if news_article is None or news_article == "":
                continue

            summarized_content = summarizer.summarize_article(news_article)
            results.append({
                "title": article.get('title'),
                "url": news_url,
                "summarized_content": summarized_content
            })

        return {"output": results}

    def _check_article_exist(self, state: NewsAgentState):
        """
        conditional edge function
        가져온 뉴스 기사가 3건 이상 존재하는지 확인.
        3건 미만일 경우, 다시 검색필요.
        :param state:
        :return: 1개라도 존재할 경우 existed, 없을 경우 not_existed 반환
        """

        if len(state["articles"]) >= 3:
            return "existed"
        return "not_existed"

    def _setup_nodes(self):
        """노드 설정"""
        self._graph.add_node("UserInput", self._get_user_input)
        self._graph.add_node("SearchNews", self._search_news_articles)
        self._graph.add_node("RemoveDuplicatedNews", self._remove_duplicated_articles)
        self._graph.add_node("SummaryNews", self._summary_news_articles)

    def _setup_edges(self):
        """엣지 설정"""
        self._graph.add_edge(START, "UserInput")
        self._graph.add_edge("UserInput", "SearchNews")
        self._graph.add_conditional_edges(
            "SearchNews",
            self._check_article_exist,
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
