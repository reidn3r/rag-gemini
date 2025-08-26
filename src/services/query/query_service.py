from services.llm.gemini import GeminiLLM
from services.rag.retrieval.retrieval_service import RetrievalService

class QueryService:
  def __init__(self):
    self.retrieval_service = RetrievalService()
    self.llm = GeminiLLM()

  async def stream_response(self, query: str):
    selected = await self.__search_and_rerank(query)
    async for chunk in self.llm.stream(query, selected):
      yield chunk

  async def generate_response(self, query: str):
    selected = await self.__search_and_rerank(query)
    return await self.llm.query(query, selected)

  async def __search_and_rerank(self, query: str):
    search = await self.retrieval_service.run(query)
    reranking = await self.llm.rerank(query, search)
    selected = self.__select_by_reranking_threshold(threshold=6.5, reranking_list=reranking)    
    return selected
  
  def __select_by_reranking_threshold(self, threshold: float, reranking_list):
    return [r for r in reranking_list if r.score >= threshold]