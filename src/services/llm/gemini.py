from src.services.prompts.prompt_builder import reranking_prompt
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
  
  async def rerank(self, query: str, context: set):
    prompt = reranking_prompt(query, context)

    print(f'PROMPT: ', prompt)
    
    return await self.generate(prompt)
  
  def count_tokens(self, content: str) -> int:
    tokens = self.encoding.encode(content)
    return len(tokens)