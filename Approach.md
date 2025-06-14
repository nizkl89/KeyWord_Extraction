# Approach to Building the Keyword Extraction System

This document explains the approach taken to design and implement a keyword extraction system as part of the AI-powered text analysis project. The system extracts the most important keywords or phrases from input text or `.txt` files via a web interface, using a React front-end and Flask backend, deployed with Docker. Below, I outline the problem breakdown, choice of algorithms and models, text preprocessing techniques (inspired by [Aysel Aydin's article](https://ayselaydin.medium.com/1-text-preprocessing-techniques-for-nlp-37544483c007)), implementation details, potential improvements, and evaluation strategies.

## Problem Breakdown
The task was to build a simple AI-powered text analysis system, selecting one of three options: keyword extraction, text summarization, or topic classification. I chose **keyword extraction** because:
- I think it is a useful content analysis tool for search engine which I am interested in.
- It leverages modern transformer-based models like BERT, which excel at capturing contextual semantics, and I had hands-on experience in using BERT related models in my Machine learning course porject.
- It aligns with the requirement for a simple yet impactful system that can be extended with a front-end interface.

I first break it down into sub-problems:
1. **Core Functionality**: Develop an AI model to extract keywords/phrases from text.
2. **Text Preprocessing**: Clean and prepare raw text for analysis, following best practices in NLP.
3. **Interface**: Provide a user-friendly API and front-end for interaction.
4. **Deployment**: Ensure easy setup and scalability using containerization.

## Choice of Algorithms and Models

After doing some research on models and text preprocessing,
### KeyBERT
I selected **KeyBERT**, a lightweight, pre-trained keyword extraction framework built on BERT embeddings, for the following reasons:
- **BERT Embeddings**: KeyBERT uses BERT-based models (e.g., `all-MiniLM-L6-v2`) to generate contextual embeddings for words and phrases. Unlike traditional methods like TF-IDF, BERT captures semantic relationships, making it ideal for identifying contextually relevant keywords.
- **Ease of Use**: KeyBERT combines BERT with cosine similarity and Maximal Marginal Relevance (MMR) for diversity, reducing implementation complexity while maintaining effectiveness.
- **Performance**: The `all-MiniLM-L6-v2` model (22M parameters, 384-dimensional embeddings) is optimized for speed, suitable for a simple system and being lightweight.
- **Preprocessing Integration**: KeyBERT supports custom candidate phrases (e.g., noun phrases), enabling seamless integration with spaCy for enhanced preprocessing.

### spaCy
I used **spaCy** with the `en_core_web_md` model for text preprocessing:
- **Noun Phrase Extraction**: spaCy identifies noun phrases (e.g., “artificial intelligence”) as candidate keywords, improving input quality for KeyBERT.
- **Efficiency**: The medium-sized model (31 MB, 300-dimensional vectors) balances accuracy and speed.
- **Preprocessing Support**: spaCy’s pipeline handles tokenization and syntactic analysis, critical for cleaning text.

### NLTK
I employed **NLTK** for stopword removal:
- **Simplicity**: NLTK’s stopword list is lightweight and effective for filtering common words (e.g., “the”, “is”).
- **Customization**: I extended the stopword list with domain-specific terms (e.g., “via”, “skip”) to improve keyword relevance.

### Why Not Other Models?
- **TF-IDF**: Lacks contextual understanding, producing less relevant keywords.
- **TextRank**: Graph-based, less effective for short texts and lacks BERT’s semantic depth.
- **LDA**: Suited for topic modeling, not precise keyword extraction.
- **Larger BERT Models**: Models like `bert-base-uncased` (110M parameters) are computationally expensive for a simple system.
- **T5/BART**: Better for summarization or generation, not keyword extraction.

KeyBERT, spaCy, and NLTK provided a balance of accuracy, simplicity, and deployability.

## Text Preprocessing Techniques
Inspired by Aysel Aydin’s article on [text preprocessing for NLP](https://ayselaydin.medium.com/1-text-preprocessing-techniques-for-nlp-37544483c007), I implemented the following techniques to clean and prepare text for keyword extraction. These steps ensure the text is structured and noise-free, enhancing KeyBERT’s performance.

### 1. Lowercasing
- **Purpose**: Converts all text to lowercase to ensure case-insensitive processing (e.g., “AI” and “ai” are treated as the same).
- **Implementation**: In `backend/app.py`, the `TextPreprocessor.clean_text` method uses Python’s `text.lower()`:
  ```python
  text = text.lower()
  ```
- **Why**: Prevents KeyBERT from treating identical words with different cases as distinct, improving consistency.

### 2. Removing Punctuation & Special Characters
- **Purpose**: Removes punctuation (e.g., commas, exclamation marks) and special characters to focus on meaningful words.
- **Implementation**: Uses a regular expression in `clean_text`:
  ```python
  text = re.sub(r'[^\w\s-]', '', text)
  ```
- **Why**: Reduces noise, ensuring KeyBERT processes only alphanumeric content and hyphens (for compound terms like “machine-learning”).

### 3. Stop-Words Removal
- **Purpose**: Eliminates common words (e.g., “the”, “is”) that don’t contribute to meaning.
- **Implementation**: Uses NLTK’s stopword list in `TextPreprocessor`:
  ```python
  stop_words = set(stopwords.words('english'))
  stop_words.update(['via', 'using', 'eg', 'ie', 'skip'])
  word_tokens = text.split()
  text = ' '.join([word for word in word_tokens if len(word) >= 1])
  ```
- **Why**: Focuses KeyBERT on content words, with custom stopwords (e.g., “skip”) to filter irrelevant terms in snippets like “Skip to content”.

### 4. Removal of URLs
- **Purpose**: Removes URLs (e.g., `https://example.com`) that are irrelevant to keyword extraction.
- **Implementation**: Uses a regex in `clean_text`:
  ```python
  text = re.sub(r'https?://\S+|www\.\S+', '', text)
  ```
- **Why**: Eliminates web-specific noise, common in user inputs like social media snippets.

### 5. Removal of HTML Tags
- **Purpose**: Strips HTML tags (e.g., `<p>`) from web-scraped or formatted text.
- **Implementation**: Uses a regex in `clean_text`:
  ```python
  text = re.sub(r'<.*?>', '', text)
  ```
- **Why**: Ensures clean text for KeyBERT, especially for inputs copied from web pages.

### 6. Additional Preprocessing
- **Whitespace Normalization**: Collapses multiple spaces into a single space:
  ```python
  text = re.sub(r'\s+', ' ', text.strip())
  ```
- **Noun Phrase Extraction**: Uses spaCy’s dependency parser in `extract_noun_phrases` to identify multi-word phrases (e.g., “machine learning”):
  ```python
  doc = self.nlp(text)
  phrases = [chunk.text for chunk in doc.noun_chunks if len(chunk.text) >= 1]
  ```
- **Why**: Noun phrases are more meaningful candidates for KeyBERT than single words, improving keyword quality.

### Preprocessing Order
The preprocessing steps are applied in the following order:
1. Lowercasing
2. URL removal
3. HTML tag removal
4. Punctuation removal
5. Whitespace normalization
6. Stopword removal (implicitly via spaCy and NLTK)
7. Noun phrase extraction

This order ensures case-insensitive processing before removing noise, as recommended by Aydin’s article (e.g., lowercasing before stopword removal to catch “This” and “this”).

## Implementation Details
### Backend (`backend/app.py`)
- **Framework**: Flask, chosen for its lightweight RESTful API capabilities.
- **Preprocessing**:
  - `TextPreprocessor` class implements the above techniques, with caching (`lru_cache`) for noun phrase extraction.
  - Combines spaCy for syntactic analysis and NLTK for stopwords.
- **Keyword Extraction**:
  - `KeywordExtractor` wraps KeyBERT, using MMR (diversity=0.3) and a score threshold (>0.05).
  - Fallbacks: Uses top-2 keywords or re-runs KeyBERT without candidates if no high-scoring keywords.
- **API**: `/extract_keywords` accepts JSON (`{"text": "..."}`) or `.txt` files, returning keywords and scores.
- **CORS**: Allows requests from `http://frontend:8080` (Docker) and `http://localhost:8080` (local).
- **Deployment**: Gunicorn with 2 workers and 120-second timeout in Docker.

### Frontend (`frontend/src/App.jsx`)
- **Framework**: React for component-based UI.
- **Styling**: Tailwind CSS for responsive design.
- **Build**: Babel compiles JSX to static JavaScript, served by Nginx.
- **Features**: Text/file input, keyword display with toggleable scores, error handling, and loading states.
- **API Calls**: Fetches `/extract_keywords` from `http://backend:5001`.

### Deployment (`docker-compose.yml`)
- **Docker**: Containerizes frontend (Node.js + Nginx) and backend (Python + Gunicorn).
- **Docker Compose**: Defines services with a shared `keyword-network` for communication.
- **Ports**: Frontend at `8080`, backend at `5001`.

### Software Engineering Practices
- **Modularity**: Separated preprocessing and extraction into classes.
- **Error Handling**: API returns 400/500 status codes; frontend displays user-friendly errors.
- **Logging**: Backend logs requests and errors.

## Potential Improvements
1. **Preprocessing**:
   - Add **stemming/lemmatization** (e.g., spaCy’s lemmatizer) to normalize words (e.g., “running” → “run”).
   - Use dependency parsing for more precise multi-word phrases.
2. **Model**:
   - Fine-tune `all-MiniLM-L6-v2` on domain-specific data (e.g., news) for better relevance.
   - Experiment with larger models (e.g., `all-distilroberta-v1`) if resources allow.
3. **Deployment**:
   - Deploy to AWS ECS or Kubernetes for production.
   - Add CI/CD with GitHub Actions.
4. **Multilingual Support**:
   - Use `paraphrase-multilingual-MiniLM-L12-v2` and spaCy’s multilingual models.

## Evaluation Strategy
1. **Manual Evaluation**:
   - Curate texts (e.g., news, Wikipedia) with human-annotated keywords.
   - Compute precision, recall, and F1-score against ground truth.
2. **Automated Metrics**:
   - Use ROUGE to compare keywords to reference summaries.
   - Measure cosine similarity between keyword and document embeddings.

## Conclusion
The system combines KeyBERT’s semantic power, spaCy/NLTK preprocessing, and a modular Flask/React architecture. Docker ensures portability. Future enhancements could boost accuracy, scalability, and user experience.
