# 공부 자료 : https://wikidocs.net/261590
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 그래프의 상태를 정의하는 클래스
class MyState(TypedDict):
    counter: int

# StateGraph 인스턴스 생성
graph = StateGraph(MyState) # MyState : 그래프가 다루는 데이터 구조를 정의

# 카운터를 증가시키는 노드 함수 정의
# state : type=dict
def increment(state):
    return {"counter": state["counter"] + 1}

# 'increment' 노드 추가
graph.add_node("increment", increment)

# START에서 'increment' 노드로 엣지 추가
# 공부 자료 : https://wikidocs.net/262302
# edge 는 node 간의 연결을 정의
# - 실행 순서 정의: 엣지는 노드들이 어떤 순서로 실행될지 결정합니다.
# - 흐름 제어: 조건부 엣지를 사용하면 특정 조건에 따라 다른 노드로 이동할 수 있습니다.
# - 상태 전달: 한 노드에서 다음 노드로 상태를 전달하는 통로 역할을 합니다.
graph.add_edge(START, "increment")

# 'increment' 노드에서 END로 엣지 추가
graph.add_edge("increment", END)

# 그래프 컴파일
# 공부 자료 : https://wikidocs.net/262304
# 1. compile() 메서드는 정의된 그래프를 실행 가능한 형태로 변환합니다.
# 2. 이 과정에서 그래프의 구조가 검증되고, 최적화됩니다.
# 3. 컴파일된 그래프는 app 변수에 저장되며, 이제 실행할 준비가 된 상태입니다.
app = graph.compile()

# 그래프 실행
result = app.invoke({"counter": 0}) # 초기 상태를 같이 전달
print(result) # {'counter': 1}

