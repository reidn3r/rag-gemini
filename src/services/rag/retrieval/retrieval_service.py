from src.repository.embedding_repository import EmbeddingRepository
from src.services.llm.gemini import GeminiLLM

class RetrievalService:
  def __init__(self):
    self.repository = EmbeddingRepository()
    self.llm = GeminiLLM()

  async def run(self, query: str):
    semantic_result = await self.__semantic_search(query)
    lexical_result = self.__lexical_search(query)
    return self.__list2set(lexical_result, semantic_result)

  async def __semantic_search(self, query: str):
    embedding = await self.llm.embed(query)
    return await self.repository.semantic_search(embedding.embeddings[0].values)
    
  def __lexical_search(self, query: str):
    results, tokens = [], query.split(" ")
    for t in tokens:
      results.append(self.repository.lexical_search(t))
    return results
  
  def __list2set(self, lexical_result, semantic_result):
    unique = set()
    for sem in semantic_result:
      unique.add(tuple(sem))  

    for lex_list in lexical_result:
      for lex in lex_list:
        unique.add(tuple(lex))  

    return unique


