# FC26 Career Analyzer

A system that extracts and analyzes EA FC 26 Career Mode save files using AI integration.

## Tech Stack

- **Language**: Python 3.10+
- **API**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: SQLite
- **Vector DB**: ChromaDB
- **LLM**: Google Gemini 3 Pro
- **Embeddings**: sentence-transformers
- **Parser**: Node.js 18+

## Setup

1.  **Clone the repository**
2.  **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Install Node.js dependencies** (in `parser/` directory if applicable, or root if shared):
    ```bash
    npm install
    ```
4.  **Environment Variables**:
    Copy `.env.example` to `.env` and fill in your API keys.
    ```bash
    cp .env.example .env
    ```

## Project Structure

- `src/`: Python source code
    - `core/`: Business logic
    - `database/`: Models and repositories
    - `llm/`: Gemini integration
    - `vector/`: ChromaDB integration
    - `api/`: FastAPI routes
    - `cli/`: CLI interface
    - `utils/`: Utilities
- `parser/`: Node.js save file parser
- `data/`: Local databases (SQLite, ChromaDB)
- `tests/`: Test files
- `docs/`: Documentation

## Usage

(Instructions to run the API and CLI will be added here)
