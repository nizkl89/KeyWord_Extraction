# Keyword Extraction System

A web-based application for extracting keywords from text or `.txt` files using a React front-end and Flask backend, powered by KeyBERT and spaCy. Deployable locally using Docker and Docker Compose.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technologies](#technologies)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [License](#license)

## Overview
This project provides a user-friendly interface to extract keywords from input text or uploaded `.txt` files. The front-end, built with React and styled with Tailwind CSS, communicates with a Flask backend that leverages KeyBERT and spaCy for natural language processing. The application is containerized using Docker for easy deployment.

## Features
- Input text directly or upload `.txt` files for keyword extraction.
- Displays extracted keywords with relevance scores, toggleable for visibility.
- Responsive UI with error handling and loading states.
- Backend API with CORS support for secure cross-origin requests.
- Dockerized setup for consistent local deployment.

## Technologies
- **Front-end**:
  - React 18.2.0
  - Tailwind CSS 3.4.1
  - Babel 7.24.7
  - Nginx (serving static files)
- **Backend**:
  - Flask 2.3.3
  - KeyBERT 0.8.5
  - spaCy 3.7.6 (en_core_web_md model)
  - Gunicorn 23.0.0
  - NLTK 3.9.1
- **Deployment**:
  - Docker
  - Docker Compose

## Prerequisites
- Docker and Docker Compose installed.
- Node.js 20.x and npm.
- Python 3.11 (for local backend testing, optional).

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd KeyWordExtraction
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

3. **Verify Directory Structure**:
   Ensure the following structure:
   ```
   KeyWordExtraction/
   ├── backend/
   │   ├── Dockerfile
   │   ├── requirements.txt
   │   ├── app.py
   ├── frontend/
   │   ├── Dockerfile
   │   ├── etc/
   │   │   ├── nginx.conf
   │   ├── package.json
   │   ├── package-lock.json
   │   ├── .babelrc
   │   ├── src/
   │   │   ├── App.jsx
   │   │   ├── index.css
   │   ├── public/
   │   │   ├── index.html
   ├── docker-compose.yml
   ├── README.md
   ├── LICENSE
   ```

4. **Build and Run with Docker Compose**:
   ```bash
   cd /Users/kingsleylam/KinzDev/Python/KeyWordExtraction
   docker-compose build
   docker-compose up -d
   ```

5. **Access the Application**:
   - Open `http://localhost:8080` in your browser.
   - Backend API is available at `http://localhost:5001/extract_keywords`.

6. **Stop Containers**:
   ```bash
   docker-compose down
   ```

### Local Testing
- **Frontend**:
  ```bash
  cd frontend
  npm run build
  npm run start
  ```
- **Backend**:
  ```bash
  cd backend
  pip install -r requirements.txt
  python -m spacy download en_core_web_md
  python app.py --api
  ```

## Usage
1. **Text Input**:
   - Enter text in the textarea.
   - Click “Extract Keywords” to view results.
2. **File Input**:
   - Upload a `.txt` file
   - Click “Extract from File” to view results.
3. **Toggle Scores**:
   - Click “Toggle Scores” to show/hide keyword relevance scores.

## License
This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.
