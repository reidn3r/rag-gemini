from langchain.prompts import ChatPromptTemplate

reranking_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """
    Avalie a relevância dos seguintes documentos para a query: "{query}".
    
    Classifique cada documento de 0 (não relevante) a 10 (muito relevante).
    Considere:
    - Precisão da informação
    - Completude da resposta
    - Contextualização
    - Especificidade
    
    DOCUMENTOS:
    {documents}
    
    Retorne APENAS uma lista JSON com scores:
    [{{"document_index": 1, "score": 8, "reason": "explica conceito X"}}, ...]
    """)
])

final_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """
    # CONTEXTO PARA RESPOSTA
    Baseie-se EXCLUSIVAMENTE nas informações fornecidas nos documentos abaixo para responder à pergunta.

    ## DOCUMENTOS RELEVANTES (ordenados por relevância)
    {context}

    {relevance_analysis}

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
    """),
    ("user", "{query}")
])