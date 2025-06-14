import argparse
import logging
import re
from functools import lru_cache
from typing import List, Tuple

import nltk
import spacy
from flask import Flask, jsonify, request
from flask_cors import CORS
from keybert import KeyBERT
from nltk.corpus import stopwords

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Download NLTK stopwords
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    logger.info("Downloading NLTK stopwords")
    nltk.download('stopwords')

# Initialize singletons
class TextPreprocessor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                logger.info("Loading spaCy model en_core_web_md")
                cls._instance.nlp = spacy.load("en_core_web_md", disable=["ner", "lemmatizer", "attribute_ruler"])
            except OSError as e:
                logger.error(f"Failed to load en_core_web_md: {e}")
                raise RuntimeError("SpaCy model 'en_core_web_md' not found. Run `python -m spacy download en_core_web_md`.")
            cls._instance.stop_words = set(stopwords.words('english'))
            cls._instance.stop_words.update(['via', 'using', 'eg', 'ie', 'skip'])
        return cls._instance

    def clean_text(self, text: str) -> str:
        if not text or not isinstance(text, str):
            logger.warning("Invalid or empty text input for cleaning")
            return text or ""
        text = text.lower()
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'\s+', ' ', text.strip())
        word_tokens = text.split()
        text = ' '.join([word for word in word_tokens if len(word) >= 1])
        logger.debug(f"Cleaned text: {text[:100]}...")
        return text

    @lru_cache(maxsize=1000)
    def extract_noun_phrases(self, text: str) -> tuple:
        if not text:
            logger.debug("Empty text for noun phrase extraction")
            return tuple()
        doc = self.nlp(text)
        phrases = [chunk.text for chunk in doc.noun_chunks if len(chunk.text) >= 1]
        if not phrases:
            phrases = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) >= 2]
        logger.debug(f"Extracted {len(phrases)} noun phrases: {phrases[:5]}")
        return tuple(phrases)

class KeywordExtractor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.preprocessor = TextPreprocessor()
            try:
                logger.info("Initializing KeyBERT with all-MiniLM-L6-v2")
                cls._instance.kw_model = KeyBERT(model='all-MiniLM-L6-v2')
            except Exception as e:
                logger.error(f"Failed to initialize KeyBERT: {e}")
                raise RuntimeError(f"KeyBERT initialization failed: {e}")
        return cls._instance

    def extract_keywords(self, text: str) -> List[Tuple[str, float]]:
        if not text:
            logger.warning("Empty text input for keyword extraction")
            return []
        
        try:
            logger.debug(f"Processing text: {text[:100]}...")
            cleaned_text = self.preprocessor.clean_text(text)
            candidates = list(self.preprocessor.extract_noun_phrases(text))
            
            if not candidates:
                candidates = cleaned_text.split() if cleaned_text else [word for word in text.lower().split() if len(word) >= 2]
                logger.debug(f"No noun phrases found, using candidates: {candidates[:5]}")
            
            if not candidates:
                logger.warning("No valid candidates for keyword extraction")
                return []
            
            keywords = self.kw_model.extract_keywords(
                text,
                candidates=candidates,
                top_n=10,
                use_mmr=True,
                diversity=0.3,
                min_df=1
            )
            
            keyword_scores = [(kw, score) for kw, score in keywords if score > 0.05][:5]
            
            if not keyword_scores and keywords:
                keyword_scores = keywords[:2]
                logger.debug("Using fallback keywords due to low scores")
            
            if not keyword_scores:
                keywords = self.kw_model.extract_keywords(
                    text,
                    top_n=5,
                    use_mmr=False
                )
                keyword_scores = [(kw, score) for kw, score in keywords if score > 0.05][:5]
                logger.debug("Using KeyBERT without candidates as final fallback")
            
            logger.info(f"Extracted {len(keyword_scores)} keywords: {keyword_scores}")
            return keyword_scores
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            raise

def read_file(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        raise

app = Flask(__name__)
CORS(app, resources={r"/extract_keywords": {"origins": ["http://localhost:8080", "http://frontend:8080"]}})

@app.route('/extract_keywords', methods=['POST'])
def extract_keywords_api():
    logger.info("Received request to /extract_keywords")
    try:
        extractor = KeywordExtractor()
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.txt'):
                text = file.read().decode('utf-8')
                logger.debug(f"Processing file: {file.filename}")
            else:
                logger.warning("Invalid file format")
                return jsonify({'error': 'Only .txt files are supported'}), 400
        else:
            data = request.get_json()
            if not data or 'text' not in data:
                logger.warning("No text provided in request")
                return jsonify({'error': 'No text provided'}), 400
            text = data['text']
            if not text.strip():
                logger.warning("Empty text in request")
                return jsonify({'error': 'Empty text provided'}), 400
        
        keywords = extractor.extract_keywords(text)
        response = {
            'keywords': [{'keyword': kw, 'score': float(score)} for kw, score in keywords]
        }
        logger.info(f"Returning {len(keywords)} keywords")
        return jsonify(response)
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

def main():
    parser = argparse.ArgumentParser(description="AI-powered keyword extraction system.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', type=str, help="Input text for keyword extraction.")
    group.add_argument('--file', type=str, help="Path to text file for keyword extraction.")
    group.add_argument('--api', action='store_true', help="Run Flask API server.")
    args = parser.parse_args()

    if args.api:
        logger.info("Starting Flask API server")
        app.run(debug=False, host='0.0.0.0', port=5001)
    else:
        extractor = KeywordExtractor()
        try:
            text = args.text if args.text else read_file(args.file)
            keywords = extractor.extract_keywords(text)
            print("\nExtracted Keywords:")
            for keyword, score in keywords:
                print(f"{keyword}: {score:.4f}")
        except Exception as e:
            logger.error(f"CLI error: {e}")
            print(f"Error: {e}")

if __name__ == "__main__":
    main()