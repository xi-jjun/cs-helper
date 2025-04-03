# https://python.langchain.com/v0.1/docs/modules/model_io/output_parsers/quick_start/

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from pydantic.v1 import BaseModel, Field, validator
from langchain.output_parsers import PydanticOutputParser

load_dotenv() # load .env file

API_KEY = os.environ['OPEN_AI_API_KEY']
CHAT_GPT_MODEL = os.environ['OPEN_AI_MODEL']

class CsResponse(BaseModel):
    question_type: str = Field(description="문의 성격을 분류해주세요.")
    emotion: str = Field(description="고객에게 공감하며 위로를 전달하는 말")
    answer: str = Field(description="고객의 문의에 대한 실질적인 답변")

    @classmethod
    def model_json_schema(cls):
        return cls.schema()

parser = PydanticOutputParser(pydantic_object=CsResponse)

prompt = PromptTemplate(
    template="""
    너는 NBT라는 애드 테크 기업의 CS 총괄 관리자야. 고객의 문의를 문의 성격에 따라서 분류해주고 적절한 답변을 해줘야 해.
    답변은 무조건 한국말로 해줘.
    문의 성격은 총 3가지로 나뉘어.
    1. 리워드 지급 이슈
    2. 동일 유저에 대한 중복 문의 (user_id 가 동일하고, 문의 내용이 비슷한 요구사항일 경우)
    3. 그 외 문의

    너는 1, 2 유형에 대해서 해결책을 제시해줘야 해.
    3번 유형에 대해서는 분류 후 CX팀에게 전달해줘야 해.

    <유저 문의 내용>
    유저 ID : {user_id}
    유저 문의 내용 : {user_question}

    <답변 내용>
    {format_instructions}
    """,
    input_variables=["user_id", "user_question"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

llm = ChatOpenAI(model=CHAT_GPT_MODEL, openai_api_key=API_KEY)

chain = prompt | llm
output = chain.invoke({"user_id": "1234", "user_question": "안녕하세요. 캐시슬라이드 설치했는데 리워드가 지급되지 않았어요. 확인해주세요."})
result = parser.invoke(output)
print("파싱된 결과:")
print(f"문의 유형: {result.question_type}")
print(f"공감 메시지: {result.emotion}")
print(f"답변 내용: {result.answer}\n")

output2 = chain.invoke({"user_id": "1234", "user_question": "캐시슬라이드 설치했는데 리워드 안줬어요. 주세요."})
result2 = parser.invoke(output2)
print("파싱된 결과:")
print(f"문의 유형: {result2.question_type}")
print(f"공감 메시지: {result2.emotion}")
print(f"답변 내용: {result2.answer}\n")

output3 = chain.invoke({"user_id": "TEN3TK$", "user_question": "캐시슬라이드 매체에 광고를 진행하고 싶어요. 어떻게 해야 할까요?"})
result3 = parser.invoke(output3)
print("파싱된 결과:")
print(f"문의 유형: {result3.question_type}")
print(f"공감 메시지: {result3.emotion}")
print(f"답변 내용: {result3.answer}\n")

output4 = chain.invoke({"user_id": "agNT$K", "user_question": "오퍼월 광고에 참여했는데 리워드 지급을 못받았어요."})
result4 = parser.invoke(output4)
print("파싱된 결과:")
print(f"문의 유형: {result4.question_type}")
print(f"공감 메시지: {result4.emotion}")
print(f"답변 내용: {result4.answer}\n")

output5 = chain.invoke({"user_id": "i4tarRKT", "user_question": "무신사 광고 참여. 리워드 지급 바람"})
result5 = parser.invoke(output5)
print("파싱된 결과:")
print(f"문의 유형: {result5.question_type}")
print(f"공감 메시지: {result5.emotion}")
print(f"답변 내용: {result5.answer}\n")

# GPT-3.5 모델 사용
# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 안녕하세요. 캐시슬라이드를 이용해주셔서 감사합니다. 리워드 지급이 지연된 점 대단히 죄송합니다. 유저 ID 1234님의 리워드 이슈를 신속하게 확인하여 조치하겠습니다. 잠시만 기다려주세요.
# 답변 내용: CX팀에 해당 유저 ID 및 리워드 지급 이슈를 전달했습니다. 조속한 처리를 위해 최선을 다하겠습니다.

# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 캐시슬라이드 설치해주셔서 감사합니다. 리워드가 정상적으로 지급되지 않아 죄송합니다. 유저 ID 1234님의 리워드를 확인하고 즉시 지급해드리도록 하겠습니다.
# 답변 내용: 유저 ID 1234님의 리워드 지급 이슈에 대해 신속한 조치를 취하겠습니다. 감사합니다.

# 파싱된 결과:
# 문의 유형: 3
# 공감 메시지: 고객님, 광고를 진행하고 싶으시다니 정말 멋진 아이디어네요. 해당 문의는 CX팀에 전달하도록 하겠습니다. 빠른 답변을 도와드리도록 노력하겠습니다.
# 답변 내용: 고객님, 캐시슬라이드 매체에 광고를 진행하고 싶으신다고요? 해당 신청을 위해서는 NBT의 광고 담당자와 상의가 필요합니다. 광고를 원하시는 내용과 목적을 자세히 알려주시면 보다 빠른 도움을 드릴 수 있습니다.

# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 안타깝게도 리워드 지급에 문제가 있었군요. 빠른 시일 내에 조치를 취하도록 하겠습니다.
# 답변 내용: 유저 ID가 agNT$K인 고객님, 오퍼월 광고에 대한 리워드 지급 이슈에 대해 해결책을 찾기 위해 노력하겠습니다. 조속히 상황을 확인하여 문제를 해결해드리겠습니다.

# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 안타깝게도 현재 무신사 광고 참여에 대한 리워드 지급이 지연되고 있습니다. 빠른 시일 내에 조치를 취해드리도록 하겠습니다.
# 답변 내용: 유저 ID i4tarRKT님의 리워드 지급 이슈에 대한 해결책을 찾아보고 빠른 시일 내에 처리해드리도록 하겠습니다.


# ----

# GPT-4o mini 모델 사용
# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 리워드 지급에 대한 불편을 드려서 죄송합니다.
# 답변 내용: 안녕하세요, 고객님. 리워드 지급 문제가 발생하여 매우 유감입니다. 해당 문제를 확인 후 조속히 해결하도록 하겠습니다. 잠시만 기다려 주시면 감사하겠습니다.

# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 안타까운 마음입니다. 리워드를 받지 못하셨다니 유감입니다.
# 답변 내용: 리워드 지급이 지연된 점 사과드립니다. 유저 ID 1234에 대해 확인한 결과, 리워드 지급 프로세스에서 문제가 발생한 것으로 보입니다. 즉시 해당 사항을 처리하여 리워드를 지급하도록 하겠습니다. 잠시만 기다려 주시면 감사하겠습니다.

# 파싱된 결과:
# 문의 유형: 그 외 문의
# 공감 메시지: 안녕하세요! 고객님, 광고 진행에 관심 가져주셔서 감사합니다.
# 답변 내용: 캐시슬라이드 매체에 광고를 진행하기 위해서는 우리 고객 지원팀에 문의하시면 됩니다. 그들은 필요하신 정보를 제공하고 절차를 안내해드릴 것입니다. 연락 주시면 최선을 다해 도와드리겠습니다.

# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 불편을 드려 정말 죄송합니다. 저희 서비스 이용에 불편함이 없도록 최선을 다하겠습니다.
# 답변 내용: 오퍼월 광고 참여에 따른 리워드 지급을 확인해보겠습니다. 확인 후 지급이 지연된 이유를 안내해드리겠습니다. 잠시만 기다려주시기 바랍니다.

# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 리워드 지급이 지연되어 불편을 끼쳐드려 정말 죄송합니다.
# 답변 내용: 무신사 광고 참여에 대한 리워드는 확인 후 지급하도록 하겠습니다. 지급이 완료되면 별도로 안내드리겠습니다. 추가 문의사항이 있으시면 언제든지 말씀해 주세요.

# ---

# GPT-4o 모델 사용
# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 안녕하세요. 불편을 드려 죄송합니다.
# 답변 내용: 캐시슬라이드 설치 후 리워드가 지급되지 않아 불편을 겪으신 점 이해합니다. 우선 앱 설치 과정에서 정상적으로 설치가 완료되었는지 확인 부탁드리며, 설치 후 첫 실행이 정상적으로 이루어졌는지도 체크해주세요. 만약 모든 과정이 정상적이었음에도 문제가 지속된다면, 고객님의 계정 정보를 첨부해주시면 추가적인 확인을 도와드리겠습니다. 감사합니다.

# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 불편을 드려서 죄송합니다.
# 답변 내용: 캐시슬라이드 설치 이후 리워드가 지급되지 않은 경우, 먼저 앱이 최신 버전인지 확인해 주시고, 재시도 후에도 리워드가 지급되지 않는다면 고객님의 계정 정보를 포함하여 고객센터에 다시 문의해 주시기 바랍니다. 저희가 신속히 확인 후 처리해 드리겠습니다.

# 파싱된 결과:
# 문의 유형: 그 외 문의
# 공감 메시지: 캐시슬라이드 광고에 관심을 가져주셔서 감사합니다!
# 답변 내용: 캐시슬라이드 매체에 광고를 진행하고 싶으신 경우, 당사 광고 담당자에게 연락하시거나 공식 웹사이트의 광고 문의 섹션을 통해 신청해주시면 자세한 안내를 받으실 수 있습니다. 추가 문의사항이 있으시면 언제든지 알려주세요.

# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 걱정 많으셨겠어요. 리워드를 받지 못하셨다니 죄송합니다.
# 답변 내용: 해당 오퍼월 광고에 참여하신 기록을 확인 후 리워드 지급 내역을 검토하겠습니다. 정상적으로 참여하신 경우, 리워드가 지급되도록 빠르게 처리해드리겠습니다. 불편을 드려 죄송합니다.

# 파싱된 결과:
# 문의 유형: 리워드 지급 이슈
# 공감 메시지: 고객님, 불편을 드려 죄송합니다. 고객님의 요청을 신속하게 처리하도록 하겠습니다.
# 답변 내용: 현재 무신사 광고 참여에 대한 리워드 지급이 지연되고 있는 것으로 보입니다. 관련 부서에서 확인 후 지급 처리 예정이니, 조금만 더 기다려 주시기 바랍니다. 불편을 끼쳐드려 다시 한번 죄송합니다.