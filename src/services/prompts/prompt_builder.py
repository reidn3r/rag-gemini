def final_prompt():
  pass

def reranking_prompt(query: str, found_documents: set):
  prompt=f"""
    Avalie a relevância dos segu documentos para a query: "{query}"
    
    Classifique cada documento de 0 (não relevante) a 10 (muito relevante).
    Considere:
    - Precisão da informação
    - Completude da resposta
    - Contextualização
    - Especificidade
    
    DOCUMENTOS:
    {chr(10).join([f'[Documento {i+1}] {doc[:500]}...' for i, doc in enumerate(found_documents)])}
    
    Retorne APENAS uma lista JSON com scores:
    [{{"document_index": 1, "score": 8, "reason": "explica conceito X"}}, ...]
  """
  return prompt.strip()
