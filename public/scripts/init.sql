CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS btree_gin;

CREATE TABLE IF NOT EXISTS tb_documents (
  id SERIAL PRIMARY KEY,
  file_name TEXT,
  content TEXT,
  tokens INT, 
  embedding VECTOR(32),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tb_documents_embedding_ivfflat
ON tb_documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 64);

CREATE INDEX IF NOT EXISTS idx_tb_documents_gin_content
ON tb_documents
USING gin(to_tsvector('portuguese', content));