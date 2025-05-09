from openai import OpenAI
import streamlit as st

ROLE_ASSISTANT = "assistant"
ROLE_USER = "user"

# 사이드바 메뉴
with st.sidebar:
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

    client = OpenAI(api_key=openai_api_key)

    # 유저 채팅
    st.session_state.messages.append({"role": ROLE_USER, "content": user_input_query})
    st.chat_message(ROLE_USER).write(user_input_query)

    # AI 채팅
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": ROLE_ASSISTANT, "content": msg})
    st.chat_message(ROLE_ASSISTANT).write(msg)
