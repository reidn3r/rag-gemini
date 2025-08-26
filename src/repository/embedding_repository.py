import psycopg2
import os

class EmbeddingRepository:
  def __init__(self):
    self.cursor = psycopg2.connect(
      host="localhost",
      port=os.getenv("POSTGRES_PORT"),
      dbname=os.getenv("POSTGRES_DB"),
      user=os.getenv("POSTGRES_USER"),
      password=os.getenv("POSTGRES_PASSWORD")
    ).cursor()


  async def save(self, filename, content, n_tokens, embedding):
    sql = '''INSERT INTO  tb_documents (file_name, content, tokens, embedding) VALUES (%s, %s, %s, %s)'''
    self.cursor.execute(sql, (filename, content, n_tokens, embedding))
    self.cursor.connection.commit()

  async def adjust_ivfflat_index(self):    
    self.cursor.execute("SELECT COUNT(*) FROM tb_documents;")
    n = self.cursor.fetchone()[0]
    lists = max(1, int(n / 1000))

    self.cursor.execute("DROP INDEX IF EXISTS idx_tb_documents_embedding_ivfflat;")
    self.cursor.execute(f"""
        CREATE INDEX idx_tb_documents_embedding_ivfflat
        ON tb_documents
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = {lists});
    """)
    self.cursor.connection.commit()
    print(f"Recriado índice IVFFLAT com lists={lists}")
