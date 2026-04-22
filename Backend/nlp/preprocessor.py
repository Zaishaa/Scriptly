import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)


class TextPreprocessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        # Keep these emotional words even if they're stopwords
        self.emotional_words = {
            'not', 'no', 'never', 'very', 'really', 'so',
            'too', 'most', 'more', 'but', 'however'
        }
        self.stop_words -= self.emotional_words

    def clean_text(self, text):
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\!\?]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def preprocess(self, text):
        # Step 1: Lowercase
        text = text.lower()

        # Step 2: Clean text
        text = self.clean_text(text)

        # Step 3: Tokenize
        tokens = word_tokenize(text)

        # Step 4: Remove stopwords
        tokens = [t for t in tokens if t not in self.stop_words]

        # Step 5: Lemmatize
        tokens = [self.lemmatizer.lemmatize(t) for t in tokens]

        # Step 6: Rejoin
        processed = ' '.join(tokens)

        return processed

    def preprocess_for_model(self, text):
        # For the transformer model, we use cleaned but NOT
        # stopword-removed text — transformers work better with
        # full sentences
        text = text.lower()
        text = self.clean_text(text)
        # Truncate to 512 tokens max (BERT limit)
        words = text.split()
        if len(words) > 400:
            text = ' '.join(words[:400])
        return text
    
    def clean_text(self, text):
        text = re.sub(r'http\S+|www\S+', '', text)
        # FIX: Keep apostrophes so "don't", "I'm", "I've" survive intact
        text = re.sub(r"[^\w\s\.\!\?\']", '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text