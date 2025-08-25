import re
import string
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from typing import Literal, List

class Preprocessing:
  def __init__(self):
    self.stopwords = set(stopwords.words('english'))
    self.punctuation = set(string.punctuation)
    
  def run(self, text: List[str], approach: Literal['stem', 'lemma'] = 'stem'):
    tokens = self.__clean__(text)

    if approach == 'stem':
      tokens =  self.__stemming__(tokens)
    
    elif approach == 'lemma':
      tokens = self.__lemmatization__(tokens);

    tokens = self.__remove_stopwords__(tokens)

    return tokens

  def __clean__(self, text):
    latex_pattern = re.compile(r'\\[a-z]+|[\x00-\x1f\x7f]')

    tokens = []
    for token in text:
      if token in self.punctuation:
        continue
      
      # Remove TODOS os parênteses e seu conteúdo (em qualquer posição)
      token = re.sub(r'\([^)]*\)', ' ', token).lower()
        
      # Remove pontuação residual (como o "." em "(j)).")
      # token = re.sub(r'[^\w\s-]', ' ', token)
    
      # Remove padrão latex do texto
      token = latex_pattern.sub(' ', token)
      
      # Remove -\n do texto, comum em quebras de linha dos docs.
      token = token.replace('-\n', "")

      # Remove \n do texto, comum em quebras de linha dos docs.
        # Trata separação de palavras com hífen nao capturadas em -\n
      subtokens = [t for t in token.replace('\n', " ").split(" ") if t]
      if(len(subtokens) == 2 and subtokens[0].endswith('-')):
        tokens.append(subtokens[0][:-1] + subtokens[1])
      else:
        tokens.extend(subtokens)

    return tokens

  def __remove_stopwords__(self, tokens):
    return [token for token in tokens if token.lower() not in self.stopwords]

  def __stemming__(self, tokens):
    stemmer = SnowballStemmer('english')
    return [stemmer.stem(token) for token in tokens]

  def __lemmatization__(self, tokens):
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]
