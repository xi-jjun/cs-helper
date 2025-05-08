from typing import TypedDict
from datetime import datetime


class Article(TypedDict):
    title: str
    url: str
    published_at: datetime


class NewsAgentState(TypedDict):
    input: str
    articles: list[Article]
    output: str
