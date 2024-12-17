import re
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

class TextPreprocessor:
    def __init__(self):
        self.ps = PorterStemmer()
        self.wnl = WordNetLemmatizer()
        self.stop_words = stopwords.words('english')
        self.stopwords_dict = Counter(self.stop_words)

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'\[.*?\]','',text)
        text = re.sub("\\W"," ",text)
        text = re.sub(r'https?://\S+|www\.\S+','',text)
        text = re.sub('<.*?>+','',text)
        text = re.sub(r'\w*\d\w*','',text)
        return text

    def preprocess_text(self, text):
        text = self.clean_text(text)
        wordlist = text.split()
        text = ' '.join([self.wnl.lemmatize(word) for word in wordlist 
                        if word not in self.stopwords_dict])
        return text
