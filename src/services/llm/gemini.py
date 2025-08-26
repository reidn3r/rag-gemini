from src.services.prompts.prompt_builder import reranking_prompt_template, final_prompt_template
from src.abstraction.models.RerankingDTO import map_to_reranking_list
from google.genai import types
from dotenv import load_dotenv
from google import genai
import tiktoken
import os

load_dotenv()
class GeminiLLM:
  def __init__(self):
    self.model = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    self.encoding = tiktoken.get_encoding("cl100k_base")

  async def embed(self, text: str):
    return await self.model.aio.models.embed_content(
      model="gemini-embedding-001",
      contents=text,
      config=types.EmbedContentConfig(output_dimensionality=32),
    )

  async def generate(self, prompt:str) -> str:
    response = await self.model.aio.models.generate_content(
      model=os.getenv("GEMINI_MODEL"),
      contents=prompt,
      config=genai.types.GenerateContentConfig(
        temperature=0,
      ),
    )
    return response.text
    

  async def rerank(self, query: str, context: list[str]):
    docs_text = "\n".join([f"[Documento {i+1}] {doc[:500]}..." for i, doc in enumerate(context)])

    prompt = reranking_prompt_template.format_messages(query=query, documents=docs_text)
    prompt = "\n".join([m.content for m in prompt])

    llm_response = await self.generate(prompt)
    return map_to_reranking_list(llm_response)
  
  async def query(self, query: str, reranked_documents: list[str], reranking_scores: list = None):
    context = "\n\n".join([
      f"[Documento {i+1} - Relevância: {reranking_scores[i]['score'] if reranking_scores else 'Alta'}]\n{doc}"
      for i, doc in enumerate(reranked_documents)
    ])

    relevance_analysis = ""
    if reranking_scores:
      relevance_analysis = "\n".join([
        f"- Documento {i+1}: Score {score['score']}/10 - {score['reason']}"
        for i, score in enumerate(reranking_scores)
      ])

    prompt = final_prompt_template.format_messages(
        query=query,
        context=context,
        relevance_analysis=relevance_analysis
    )
    prompt = "\n".join([m.content for m in prompt])
    return await self.generate(prompt)
  
  async def stream(self, query: str, reranked_documents: list[str], reranking_scores: list = None):
    context = "\n\n".join([
      f"[Documento {i+1} - Relevância: {reranking_scores[i]['score'] if reranking_scores else 'Alta'}]\n{doc}"
      for i, doc in enumerate(reranked_documents)
    ])

    relevance_analysis = ""
    if reranking_scores:
      relevance_analysis = "\n".join([
        f"- Documento {i+1}: Score {score['score']}/10 - {score['reason']}"
        for i, score in enumerate(reranking_scores)
      ])

    prompt = final_prompt_template.format_messages(
      query=query,
      context=context,
      relevance_analysis=relevance_analysis
    )
    prompt = "\n".join([m.content for m in prompt])  
    stream_response = await self.model.aio.models.generate_content_stream(
      model=os.getenv("GEMINI_MODEL"),
      contents=prompt,
      config=genai.types.GenerateContentConfig(
        temperature=0,
      ),
    )
    async for chunk in stream_response:
      if chunk.text:
        yield chunk.text


  def count_tokens(self, content: str) -> int:
    tokens = self.encoding.encode(content)
    return len(tokens)