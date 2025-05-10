import streamlit as st

from agent import NewsAgent

ROLE_ASSISTANT = "assistant"
ROLE_USER = "user"

# 사이드바 메뉴
with st.sidebar:
    llm_model = st.text_input("LLM Model", key="llm_model")
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    tavily_api_key = st.text_input("Tavily API Key", key="news_article_fetching_api_key", type="password")
    "[OpenAI API Key 발급하러 가기](https://platform.openai.com/account/api-keys)"
    "[Tavily API Key 발급하러 가기](https://app.tavily.com/home)"

st.title("💬 News Summary Agent")
st.caption("🚀 원하는 키워드를 작성하여 해당 기사에 대해 요약된 내용을 확인하세요!")

# session_state의 messages 데이터 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": ROLE_ASSISTANT, "content": "원하시는 뉴스 키워드를 입력해주세요"}]

# 채팅창의 모든 메세지
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if user_input_query := st.chat_input():
    if not openai_api_key:
        st.info("OpenAI Key를 세팅해주세요!")
        st.stop()
    if not tavily_api_key:
        st.info("Tavily API Key를 세팅해주세요!")
        st.stop()

    client = NewsAgent(tavily_api_key=tavily_api_key, openai_api_key=openai_api_key, llm_model=llm_model)

    # 유저 채팅
    st.session_state.messages.append({"role": ROLE_USER, "content": user_input_query})
    st.chat_message(ROLE_USER).write(user_input_query)

    # AI 채팅
    response = client.execute(user_input_query)

    msg_list = []
    if len(response.get('output')) == 1:
        msg = response.get('output')[0]
    else:
        for summarized_article in response.get('output'):
            msg_list.append(
                f"\n\n제목: {summarized_article.get('title')}\n\nurl: {summarized_article.get('url')}\n\nsummary)\n{summarized_article.get('summarized_content')}\n\n")
        msg = "\n=================================================\n".join(msg_list)
    st.session_state.messages.append({"role": ROLE_ASSISTANT, "content": msg})
    st.chat_message(ROLE_ASSISTANT).write(msg)
