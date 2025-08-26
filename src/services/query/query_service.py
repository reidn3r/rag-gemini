from typing import List
from abstraction.models import RerankingDTO
from services.llm.gemini import GeminiLLM
from services.rag.retrieval.retrieval_service import RetrievalService

class QueryService:
  def __init__(self):
    self.retrieval_service = RetrievalService()
    self.llm = GeminiLLM()

  async def run(self, query: str):
    search = await self.retrieval_service.run(query)
    reranking = await self.llm.rerank(query, search)
    selected = self.__select_by_reranking_threshold(threshold=6.5, reranking_list=reranking)
    return await self.llm.query(query, selected)
  
  def __select_by_reranking_threshold(self, threshold: float, reranking_list):
    return [r for r in reranking_list if r.score >= threshold]