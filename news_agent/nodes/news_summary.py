import os
from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from newspaper import Article


@dataclass
class NewsArticle:
    """뉴스 기사 데이터 클래스"""
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    published_date: Optional[str] = None


class NewsContentExtractor(ABC):
    """뉴스 기사 본문 추출을 위한 추상 클래스"""

    @abstractmethod
    def extract(self, url: str) -> Optional[NewsArticle]:
        """
        뉴스 기사 본문을 추출합니다.
        
        Args:
            url (str): 뉴스 기사 URL
            
        Returns:
            Optional[NewsArticle]: 추출된 기사 정보. 실패 시 None 반환
        """
        pass


class Newspaper3kExtractor(NewsContentExtractor):
    """newspaper3k를 사용한 뉴스 기사 본문 추출기"""

    def extract(self, url: str) -> Optional[NewsArticle]:
        try:
            article = Article(url)
            article.download()
            article.parse()

            if not article.text:
                print(f"기사 본문이 비어있습니다: {url}")
                return None

            return NewsArticle(
                url=url,
                title=article.title,
                content=article.text,
                published_date=article.publish_date.isoformat() if article.publish_date else None,
            )

        except Exception as e:
            print(f"기사 본문 추출 중 오류 발생: {url}, 에러: {str(e)}")
            return None


class NewsSummarizer:
    """뉴스 기사 요약 클래스"""

    def __init__(
            self,
            api_key: str,
            model_name: str = "gpt-3.5-turbo-0125",
            content_extractor: Optional[NewsContentExtractor] = None
    ):
        """
        Args:
            api_key (str): OpenAI API 키
            model_name (str): 사용할 OpenAI 모델 이름
            content_extractor (Optional[NewsContentExtractor]): 뉴스 본문 추출기
        """
        self.model_name = model_name
        self.embeddings = OpenAIEmbeddings(model=model_name, openai_api_key=api_key)
        self.llm = ChatOpenAI(model_name=model_name, temperature=0.5)
        self.vector_store = None
        self.content_extractor = content_extractor or Newspaper3kExtractor()

    def extract_news_content(self, news_url: str) -> Optional[NewsArticle]:
        """
        뉴스 기사 본문을 추출합니다.
        
        Args:
            news_url (str): 뉴스 기사 URL
            
        Returns:
            Optional[NewsArticle]: 추출된 기사 정보
        """
        return self.content_extractor.extract(news_url)

    def summarize_article(self, article: NewsArticle) -> Optional[str]:
        """
        뉴스 기사를 요약합니다.
        
        Args:
            article (NewsArticle): 요약할 뉴스 기사
            
        Returns:
            Optional[str]: 요약된 기사 내용
        """
        if not article.content:
            return None

        # TODO: 실제 요약 로직 구현
        return f"요약: {article.title}"


if __name__ == "__main__":
    load_dotenv()
    # 테스트 코드
    test_url = "https://www.hankyung.com/article/202505089530i"

    summarizer = NewsSummarizer(api_key=os.environ['OPENAI_API_KEY'])
    article = summarizer.extract_news_content(test_url)

    if article:
        print(f"제목: {article.title}")
        print(f"본문: {article.content}")
        print(f"작성일: {article.published_date}")

        summary = summarizer.summarize_article(article)
        if summary:
            print(f"요약: {summary}")
