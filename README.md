# RAG: Gemini, LangChain e PostgreSQL
Implementação de pipeline de **Recuperação-Aumentada por Geração (RAG)** utilizando a **SDK do Gemini**, LangChain, PostgreSQL para armazenamento de embeddings e documentos, pré-processamento de texto, reranking e **token streaming** para respostas em tempo real.

## Tecnologias utilizadas
- **Python 3.12**  
- **PostgreSQL** - Extensões **pgvector** e **GIN**:  
  - `pgvector` armazena embeddings vetoriais e permite buscas semânticas otimizadas.  
  - `GIN` (Generalized Inverted Index) acelera buscas textuais completas em documentos.  
- **Google Gemini SDK (`google-genai`)**: interface com o LLM Gemini para geração de embeddings, reranking e streaming de tokens.  
- **LangChain**: Gerenciamento de mensagens, Prompt templates, Splitter, etc
- **PyPDF**: Extração de texto de documentos PDF para pré-processamento.  
- **Asyncio**: processamento assíncrono de ingestão, embedding e geração de respostas.  
- **tiktoken**: contagem de tokens em chunks de texto para controle de tamanho de prompt e cálculo de embeddings.

## Fluxo completo do projeto

O pipeline completo do sistema envolve várias etapas, combinando pré-processamento, indexação, busca e reranking, conforme detalhado abaixo:

1. **Extração e pré-processamento de documentos**  
   - PDFs são lidos página por página usando **PyPDF**.  
   - Textos passam por limpeza e normalização com a classe **Preprocessing**, removendo quebras, espaços extras e caracteres irrelevantes.  

2. **Chunking e criação de embeddings**  
   - Textos longos são divididos em **chunks de 256 tokens** com **overlap de 64** usando `RecursiveCharacterTextSplitter`.  
   - Cada chunk gera um **embedding vetorial** via **Gemini LLM**.  

3. **Armazenamento no PostgreSQL e indexação**  
   - Cada chunk é armazenado na tabela `tb_documents` com: nome do arquivo, conteúdo, número de tokens e vetor de embedding (`pgvector`).  
   - **Indexação IVFFLAT**: clusters de vetores agrupam embeddings, acelerando buscas semânticas.  
   - **GIN (Generalized Inverted Index)**: acelera buscas textuais completas (`to_tsvector` + `plainto_tsquery`).  

4. **Busca semântica ou lexical**  
   - **Busca semântica**: vetores de consulta são comparados com embeddings usando distância de cosseno, retornando os chunks mais relevantes.  
   - **Busca lexical**: consultas textuais retornam documentos via GIN rapidamente, com relevância baseada em ocorrência de termos.  

5. **Reranking via Gemini LLM**  
   - Resultados da busca são reranqueados com **prompt templates do LangChain**, considerando:  
     - Similaridade semântica  
     - Contexto da query  
     - Conteúdo do documento  
   - Geração de scores e razões que permitem ordenação mais precisa.  

6. **Retorno da resposta**  
   - A resposta final é enviada ao usuário.  
   - **Token streaming** (via `agenerate_stream`) permite que respostas parciais sejam entregues conforme o modelo gera o texto, reduzindo latência percebida e melhorando a experiência em tempo real.

## Token Streaming
- Permite que o usuário receba **respostas parciais** conforme o modelo vai gerando texto.
- Reduz a **latência percebida**, melhorando a experiência em aplicações interativas.


O streaming de tokens funciona sobre uma **conexão HTTP/1.1** utilizando **TCP** como protocolo de transporte:

- A conexão é **mantida ativa (keep-alive)** durante toda a geração da resposta, evitando o overhead de abrir/fechar múltiplas conexões.
- O fluxo é **unidirecional** do servidor (modelo LLM) para o cliente, enviando chunks de tokens assim que são gerados.
- Cada chunk chega **incrementalmente**, permitindo que o cliente processe ou exiba o conteúdo em tempo real.
- Como HTTP/1.1 mantém a conexão TCP aberta, o servidor pode enviar múltiplos fragmentos sem esperar que o cliente confirme cada um individualmente.
- Esse método reduz a latência percebida e melhora a interatividade.
Busca:


## 1. SDK do Gemini

O projeto utiliza a **SDK oficial do Google Gemini** (`google-genai`) para:

- Geração de respostas com modelos como `gemini-2.5-flash`.
- Criação de embeddings vetoriais para indexação semântica.
- Streaming de tokens em tempo real, permitindo respostas parciais durante a inferência.

A integração é feita via cliente Python assíncrono, garantindo alta performance em chamadas concorrentes.  

## 2. Pré-processamento pré-ingestão

Antes de enviar documentos para indexação, realizamos um pipeline de pré-processamento em três etapas principais:

### 2.1 Extração de texto
- PDFs são processados usando a biblioteca `pypdf.PdfReader`.
- O texto é extraído **página por página**, garantindo que todo o conteúdo seja capturado.

### 2.2 Limpeza textual
- São removidas quebras de linha desnecessárias, espaços extras e caracteres irrelevantes.
- Utilizamos a classe `Preprocessing` para **normalização do texto**, padronizando conteúdo para geração de embeddings e indexação.

### 2.3 Chunking
- Textos longos são divididos em **chunks de 256 tokens** com **overlap de 64 tokens** utilizando o `RecursiveCharacterTextSplitter`.
- Esse processo garante que cada pedaço mantenha contexto suficiente, **melhorando a recuperação semântica** durante buscas.

## 3. Armazenamento de embeddings no PostgreSQL

Os embeddings gerados pelo Gemini são armazenados no **PostgreSQL** na tabela `tb_documents`.  

Cada registro contém os seguintes campos:

- **file_name**: nome do arquivo de origem.
- **content**: conteúdo do chunk de texto.
- **tokens**: número de tokens do chunk.
- **embedding**: vetor de embedding armazenado no tipo `vector`.

### 3.1 Indexação com IVFFLAT

Para acelerar a **busca semântica**, foi utilizado o índice **IVFFLAT**, baseado em **clusterização de vetores**:

- Os vetores são agrupados em **listas (clusters)**.
- Durante a busca, apenas os clusters mais próximos do vetor de consulta são examinados, aumentando significativamente a velocidade.
- O índice é **recriado dinamicamente** após cada ingestão de novos documentos, garantindo eficiência e atualização contínua.

## 4. Armazenamento de documentos textuais e GIN
Além dos embeddings, os conteúdos completos dos documentos podem ser consultados **lexicalmente**.

Para acelerar buscas de texto completo, utilizamos **GIN (Generalized Inverted Index)** em conjunto com `to_tsvector` e `plainto_tsquery`.

### 4.1 Funcionamento do GIN

- O texto é **tokenizado em palavras**.
- Cada palavra é associada aos **documentos onde aparece**.

## 5. Reranking de resultados

Após a busca semântica, os resultados podem ser **reranqueados** utilizando **prompts especializados do LangChain**.

### 5.1 Template de Reranking
O `reranking_prompt_template` aplica análise de relevância considerando:

- **Similaridade semântica** entre a query e o documento.
- **Contexto da query**, incluindo intenção e termos-chave.
- **Conteúdo do documento**, para avaliar quão útil ele é.

### 5.2 Processamento da resposta

- A resposta gerada pelo **Gemini LLM** é mapeada para uma lista de objetos contendo **score** e **razão** para cada documento.
- Essa lista permite ordenar os resultados de forma **mais precisa**, destacando os documentos mais relevantes antes de apresentar ao usuário.
