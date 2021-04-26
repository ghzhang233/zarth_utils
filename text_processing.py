import re
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer


def process_sentence(s, lower=True, remove_number=True, remove_punctuation=True, tokenize=False, remove_stop=False,
                     stem=False, lemmatize=False):
    s = s.strip()
    if lower:
        s = s.lower()
    if remove_number:
        s = re.sub(r"\d +", "", s)
    if remove_punctuation:
        s = "".join(c for c in s if c not in string.punctuation)
    if tokenize:
        s = word_tokenize(s)
        if remove_stop:
            s = [w for w in s if w not in stopwords]
        if stem:
            stemmer = PorterStemmer()
            s = [stemmer.stem(w) for w in s]
        if lemmatize:
            lemmatizer = WordNetLemmatizer()
            s = [lemmatizer.lemmatize(w) for w in s]
    return s


def process_text(text, **kwargs):
    return [process_sentence(s, **kwargs) for s in text]
