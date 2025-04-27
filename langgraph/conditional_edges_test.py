# 공부 자료 : https://wikidocs.net/261598
from langgraph.graph import StateGraph, START, END
from typing import Literal, Optional, TypedDict

# query: 사용자의 원래 질문
# location: 추출된 위치 정보
# forecast: 가져온 날씨 예보 정보
class WeatherState(TypedDict):
    query: Optional[str]
    location: Optional[str]
    forecast: Optional[str]

# 데이터 처리 함수 (모의 데이터)
def extract_location(query: str) -> Optional[str]:
    # 쿼리에서 "in" 다음에 오는 단어를 위치로 간주
    words = query.split()
    if "in" in words:
        index = words.index("in")
        if index + 1 < len(words):
            return words[index + 1]
    return None

def is_ambiguous(location: str) -> bool:
    # 위치가 3글자 미만이면 애매한 것으로 간주
    return len(location) < 3

def fetch_weather_data(location: str) -> str:
    # 간단한 모의 날씨 데이터
    weather_data = {
        "New York": "Sunny, 25°C",
        "London": "Rainy, 15°C",
        "Tokyo": "Cloudy, 20°C",
        "Paris": "Partly cloudy, 22°C"
    }
    return weather_data.get(location, "Weather data not available")

def generate_location_clarification(location: str) -> str:
    print(f"Could you please provide more details about the location '{location}'?")
    return location

def format_weather_response(location: str, forecast: str) -> str:
    return f"The weather in {location} is: {forecast}"

# 2. 노드 정의
def get_user_input_query(state: WeatherState):
    user_input = input("your query:")
    return {"query": user_input}

def parse_query(state: WeatherState):
    location = extract_location(state["query"])
    return {"location": location}

def get_forecast(state: WeatherState):
    forecast = fetch_weather_data(state["location"])
    return {"forecast": forecast}

def clarify_location(state: WeatherState):
    generate_location_clarification(state["location"])
    return state

def generate_response(state: WeatherState):
    response = format_weather_response(state["location"], state["forecast"])
    return {"response": response}

# conditional edges function
def check_location(state: WeatherState) -> Literal["valid", "invalid", "ambiguous"]:
    if not state["location"]:
        return "invalid"
    elif is_ambiguous(state["location"]):
        return "ambiguous"
    else:
        return "valid"

# 그래프 구성
graph = StateGraph(WeatherState)
# 그래프를 구성할 node 정의
graph.add_node("get_user_input_query", get_user_input_query)
graph.add_node("parse_query", parse_query)
graph.add_node("get_forecast", get_forecast)
graph.add_node("clarify_location", clarify_location)
graph.add_node("generate_response", generate_response)

# 구성된 node 들의 관계를 정의
graph.add_edge(START, "get_user_input_query")
graph.add_edge("get_user_input_query", "parse_query")
graph.add_conditional_edges(
    "parse_query", # parse_query node 에서
    check_location, # 해당 로직을 실행시켜서
    # 나온 결과가 key 들과 같을 때, value 의 로직을 실행한다.
    {
        "ambiguous": "clarify_location",
        "valid": "get_forecast",
        "invalid": END
    }
)
graph.add_edge("clarify_location", "get_user_input_query")
graph.add_edge("get_forecast", "generate_response")
graph.add_edge("generate_response", END)

app = graph.compile()

# result = app.invoke({'query': 'where is in To'})
result = app.invoke({}) # langgraph 실행
# your query:in tj
# Could you please provide more details about the location 'tj'?
# your query:it is in Tokyo
# {'query': 'it is in Tokyo', 'location': 'Tokyo', 'forecast': 'Cloudy, 20°C'}
print(result)
