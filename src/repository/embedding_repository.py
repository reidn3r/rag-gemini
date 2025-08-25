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
