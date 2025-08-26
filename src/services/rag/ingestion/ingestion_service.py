import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

import asyncio
from pathlib import Path
from pypdf import PdfReader
from src.config.bootstrap import bootstrap
from src.services.llm.gemini import GeminiLLM
from langchain.text_splitter import  RecursiveCharacterTextSplitter
from src.repository.embedding_repository import EmbeddingRepository
from src.services.preprocessing.text_preprocessing_service import Preprocessing

BASE_DIR = Path(__file__).parent.parent.parent.parent.parent
DOCUMENTS_DIR = BASE_DIR / "public" / "documents"

def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

async def ingest_pdf():    
  llm_wrapper = GeminiLLM()
  preprocessor_wrapper = Preprocessing()
  repository = EmbeddingRepository()

  for filename in os.listdir(DOCUMENTS_DIR):
    if filename.lower().endswith(".pdf"):
      path = os.path.join(DOCUMENTS_DIR, filename)
      buffer = read_pdf(path)
      clean_buffer = " ".join(preprocessor_wrapper.run([buffer]))
      
      splitter = RecursiveCharacterTextSplitter(
        chunk_size=256,
        chunk_overlap=64,
        separators=["\n\n", "\n", " ", ""]
      )
      chunks = splitter.split_text(clean_buffer)      
      for chunk in chunks:
        vector = await llm_wrapper.embed(chunk)
        n_tokens = llm_wrapper.count_tokens(chunk)
        repository.save(filename, chunk, n_tokens, vector.embeddings[0].values)
  
  repository.adjust_ivfflat_index()

if __name__ == "__main__":
    bootstrap()
    asyncio.run(ingest_pdf())
