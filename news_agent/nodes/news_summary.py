import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
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
            llm_model: str = "gpt-3.5-turbo-0125",
            content_extractor: Optional[NewsContentExtractor] = None
    ):
        """
        Args:
            api_key (str): OpenAI API 키
            llm_model (str): 사용할 OpenAI 모델 이름
            content_extractor (Optional[NewsContentExtractor]): 뉴스 본문 추출기
        """
        self.llm_model = llm_model
        self.llm = ChatOpenAI(model_name=llm_model, temperature=0.5, openai_api_key=api_key)
        self.content_extractor = content_extractor or Newspaper3kExtractor()

        # 요약을 위한 프롬프트 템플릿
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 뉴스 기사를 요약하는 전문가입니다.
            주어진 뉴스 기사를 다음 형식으로 요약해주세요:
            
            핵심 내용이 잘 드러나도록 3줄 이내로 요약해 주세요.  
            중요한 사실, 원인, 결과가 포함되도록 간결하게 정리해 주세요.  
            불필요한 수식어나 광고 문구는 생략해 주세요.
            결과는 markdown list format으로 작성해주세요.
            
            또한 뉴스 기사 내용 외의 것은 참고하지 마세요.

            3줄에는 아래 내용이 있어야 합니다.
            1. 핵심 내용
            2. 주요 포인트
            3. 결론 또는 시사점

            요약은 원문의 맥락을 유지하면서 객관적이고 명확하게 작성해주세요."""),
            ("human", "다음 뉴스 기사를 요약해주세요:\n\n제목: {title}\n\n내용:\n{content}")
        ])

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
            print("기사 본문이 비어있어 요약할 수 없습니다.")
            return None

        try:
            prompt = self.summary_prompt.format_messages(
                title=article.title or "제목 없음",
                content=article.content
            )

            # GPT를 사용하여 요약 생성
            response = self.llm.invoke(prompt)
            return response.content

        except Exception as e:
            print(f"기사 요약 중 오류 발생: {str(e)}")
            return None


if __name__ == "__main__":
    load_dotenv()
    # 테스트 코드
    test_url = "https://www.hankyung.com/article/202505089530i"

    summarizer = NewsSummarizer(api_key=os.environ['OPENAI_API_KEY'])
    article = summarizer.extract_news_content(test_url)

    if article:
        print(f"제목: {article.title}")
        print(f"작성일: {article.published_date}")
        print("\n=== 원문 ===")
        print(article.content)

        print("\n=== 요약 ===")
        summary = summarizer.summarize_article(article)
        if summary:
            print(summary)
