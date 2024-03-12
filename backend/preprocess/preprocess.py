import os
import json
import string
import re
from nltk.corpus import stopwords
from collections import Counter
from nltk.stem.snowball import SnowballStemmer

# Download necessary NLTK datasets
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')


def preprocess_text(text, language='english'):

    # Find the start of the Project Gutenberg eBook content
    start_pattern = re.compile(r"\*\*\* START OF THIS PROJECT GUTENBERG EBOOK .+ \*\*\*")
    start_match = start_pattern.search(text)
    
    # If the start line is found, trim the text to start from there
    if start_match:
        start_pos = start_match.end()
        text = text[start_pos:]
    else:
        # If start line is not found, assume entire text needs processing
        pass
    
    # Define stemmer based on language
    stemmer = SnowballStemmer(language)
    
    # Define stopwords based on language
    stop_words = set(stopwords.words(language))
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    
    # Convert to lowercase
    text = text.lower()
    
    # Tokenize
    tokens = text.split()
    
    # Remove stopwords and stem
    tokens = [stemmer.stem(word) for word in tokens if word not in stop_words]
    
    # Calculate frequency
    frequency = Counter(tokens)
    
    # Calculate positions
    positions = {}
    for index, token in enumerate(tokens):
        if token not in positions:
            positions[token] = []
        positions[token].append(index)
    
    return tokens, frequency, positions


class Preprocess:
        
    def preprocess(self, text):
        tokens = preprocess_text(text)
        return tokens