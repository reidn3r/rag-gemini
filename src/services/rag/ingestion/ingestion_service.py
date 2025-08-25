import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

import asyncio
from typing import List
from pathlib import Path
from pypdf import PdfReader
from src.config.bootstrap import bootstrap
from src.services.llm.gemini import GeminiLLM
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
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
    texts: List[str] = []
    if filename.lower().endswith(".pdf"):
        path = os.path.join(DOCUMENTS_DIR, filename)
        buffer = read_pdf(path)
        
        clean_buffer = " ".join(preprocessor_wrapper.run([buffer]))
        texts.append(clean_buffer)
    
    splitter = CharacterTextSplitter(chunk_size=64, chunk_overlap=12)
    docs: List[Document] = []
    
    for text in texts:
      chunks = splitter.split_text(text)
      for c in chunks:
        docs.append(Document(page_content=c))

    for doc in docs:
      vector = await llm_wrapper.embed(doc.page_content)
      n_tokens = llm_wrapper.count_tokens(doc.page_content)
      await repository.save(filename, doc.page_content, n_tokens, vector.embeddings[0].values)

if __name__ == "__main__":
    bootstrap()
    asyncio.run(ingest_pdf())
