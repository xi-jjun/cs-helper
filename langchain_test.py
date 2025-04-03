# 유투브 강의 : https://www.youtube.com/watch?v=VwHXDARgsdE

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

load_dotenv() # load .env file

API_KEY = os.environ['OPEN_AI_API_KEY']
CHAT_GPT_MODEL = os.environ['OPEN_AI_MODEL']

template = """
너는 NBT라는 애드 테크 기업의 CS 총괄 관리자야. 고객의 문의를 문의 성격에 따라서 분류해주고 적절한 답변을 해줘야 해.

<유저 문의 내용>
{user_question}
"""

prompt_template = PromptTemplate.from_template(template)
prompt_template.format(user_question="안녕하세요. 캐시슬라이드 설치했는데 리워드가 지급되지 않았어요. 확인해주세요.")

llm = ChatOpenAI(model=CHAT_GPT_MODEL, openai_api_key=API_KEY)

chain = prompt_template | llm

print(chain.invoke({"user_question": "안녕하세요. 캐시슬라이드 설치했는데 리워드가 지급되지 않았어요. 확인해주세요."}))
