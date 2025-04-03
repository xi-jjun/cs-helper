# 유투브 강의 : https://www.youtube.com/watch?v=VwHXDARgsdE

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv() # load .env file

API_KEY = os.environ['OPEN_AI_API_KEY']
CHAT_GPT_MODEL = os.environ['OPEN_AI_MODEL']

llm = ChatOpenAI(model=CHAT_GPT_MODEL, openai_api_key=API_KEY)

print(llm.invoke("캐시슬라이드 설치했는데 리워드가 지급되지 않았어요. 확인해주세요."))

