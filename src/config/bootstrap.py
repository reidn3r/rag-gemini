import nltk

def __check_stopwords_dependency():
  try:
    nltk.data.find('corpora/stopwords.zip')
  except LookupError:
    nltk.download('stopwords')

def __check_wordnet_dependency():
  try:
    nltk.data.find('corpora/wordnet.zip')
  except LookupError:
    nltk.download('wordnet')

def __check_punkt_tab_dependency():
  try:
    nltk.data.find('tokenizers/punkt_tab.zip')
  except LookupError:
    nltk.download('punkt_tab')

def __check_punkt_dependency():
  try:
    nltk.data.find('tokenizers/punkt.zip')
  except LookupError:
    nltk.download('punkt')

def bootstrap():
  __check_stopwords_dependency()
  __check_wordnet_dependency()
  __check_punkt_tab_dependency()
  __check_punkt_dependency
