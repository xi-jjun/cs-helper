# 공부 자료 : https://wikidocs.net/261598
from langgraph.graph import StateGraph, START, END
from typing import Literal, Optional, TypedDict

# query: 사용자의 원래 질문
# location: 추출된 위치 정보
# forecast: 가져온 날씨 예보 정보
class WeatherState(TypedDict):
    query: str
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
    return f"Could you please provide more details about the location '{location}'?"

def format_weather_response(location: str, forecast: str) -> str:
    return f"The weather in {location} is: {forecast}"

# 2. 노드 정의
def parse_query(state: WeatherState):
    location = extract_location(state["query"])
    return {"location": location}

def get_forecast(state: WeatherState):
    forecast = fetch_weather_data(state["location"])
    return {"forecast": forecast}

def clarify_location(state: WeatherState):
    clarification = generate_location_clarification(state["location"])
    return {"query": clarification}

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

graph = StateGraph(WeatherState)
graph.add_node("parse_query", parse_query)
graph.add_node("get_forecast", get_forecast)
graph.add_node("clarify_location", clarify_location)
graph.add_node("generate_response", generate_response)

graph.add_edge(START, "parse_query")
graph.add_conditional_edges(
    "parse_query",
    check_location,
    {
        "ambiguous": "clarify_location",
        "valid": "get_forecast",
        "invalid": END
    }
)
graph.add_edge("clarify_location", "parse_query")
graph.add_edge("get_forecast", "generate_response")
graph.add_edge("generate_response", END)

app = graph.compile()

result = app.invoke({'query': 'where is in To'})
print(result)
