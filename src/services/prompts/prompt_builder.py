def final_prompt(query: str, reranked_documents: list, reranking_scores: list = None):
    context = "\n\n".join([
        f"[Documento {i+1} - Relevância: {reranking_scores[i]['score'] if reranking_scores else 'Alta'}]\n{doc}"
        for i, doc in enumerate(reranked_documents)
    ])
    
    relevance_analysis = ""
    if reranking_scores:
        relevance_analysis = f"""
        Análise de Relevância dos Documentos:
        {chr(10).join([f'- Documento {i+1}: Score {score['score']}/10 - {score['reason']}' 
                      for i, score in enumerate(reranking_scores)])}
        """
    
    prompt = f"""
    # CONTEXTO PARA RESPOSTA
    Baseie-se EXCLUSIVAMENTE nas informações fornecidas nos documentos abaixo para responder à pergunta.
    
    ## DOCUMENTOS RELEVANTES (ordenados por relevância)
    {context}
    
    {relevance_analysis}
    
    ## PERGUNTA DO USUÁRIO
    {query}
    
    ## INSTRUÇÕES PARA RESPOSTA
    1. Use APENAS informações dos documentos fornecidos
    2. Seja preciso e completo na resposta
    3. Cite as fontes quando possível (ex: "conforme Documento 1")
    4. Se não houver informação suficiente, diga claramente
    5. Mantenha a resposta focada na pergunta
    6. Use linguagem natural e clara
    
    ## FORMATO DA RESPOSTA
    - Forneça uma resposta direta e bem estruturada
    - Inclua detalhes relevantes dos documentos
    - Evite informações não presentes no contexto
    
    RESPOSTA:
    """
    
    return prompt.strip()

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
