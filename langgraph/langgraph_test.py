# 공부 자료 : https://wikidocs.net/261587
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

# .env 파일에서 환경 변수 로드
load_dotenv()

# GPT-4o-mini 설정
gpt4o_mini = ChatOpenAI(
    model_name="gpt-4o-mini",  # GPT-4o-mini에 해당하는 모델명
    temperature=0.7,
    max_tokens=150,
)

# GPT-4o 설정
gpt4o = ChatOpenAI(
    model_name="gpt-4o",  # GPT-4o에 해당하는 모델명
    temperature=0.7,
    max_tokens=300,
)

from langchain.schema import HumanMessage

# GPT-4o-mini 사용
response_mini = gpt4o_mini.invoke([HumanMessage(content="Hello, how are you?")])
print(response_mini.content)

# GPT-4o 사용
response_full = gpt4o.invoke([HumanMessage(content="Explain the concept of machine learning.")])
print(response_full.content)

## Q1) Hello, how are you?
# Hello! I'm just a program, so I don't have feelings, but I'm here and ready to help you. How can I assist you today?

## Q2) Explain the concept of machine learning.
# Machine learning is a subset of artificial intelligence (AI) that focuses on the development of algorithms and statistical models that enable computers to perform tasks without explicit instructions. Instead of being programmed with specific rules to follow, machine learning systems are designed to learn from and make predictions or decisions based on data.
#
# Here are some key aspects of machine learning:
# 1. **Data-Driven**: Machine learning models are trained on large datasets. The quality and quantity of the data significantly influence the model's performance. The data can be structured (like databases) or unstructured (like text, images).
# 2. **Learning Process**: The core idea is to allow machines to learn patterns and make decisions from data. This involves creating a model that can find insights and make predictions or decisions based on new data.
# 3. **Types of Learning**:
#    - **Supervised Learning**: The model is trained on a labeled dataset, which means that the input data is paired with the correct output. The goal is for the model to learn the mapping from inputs to outputs so it can predict the output for new, unseen inputs.
#    - **Unsupervised Learning**: The model is given data without explicit instructions on what to do with it. It tries to learn the underlying structure of the data, such as grouping similar items together (clustering) or reducing the dimensionality of the data.
#    - **Semi-supervised Learning**: This is a middle ground between supervised and unsupervised learning. It uses
