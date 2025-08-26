from services.llm.gemini import GeminiLLM
from services.rag.retrieval.retrieval_service import RetrievalService

class QueryService:
  def __init__(self):
    self.retrieval_service = RetrievalService()
    self.llm = GeminiLLM()

  async def run(self, query: str):
    search = await self.retrieval_service.run(query)
    reranking = await self.llm.rerank(query, search)
    return reranking
    