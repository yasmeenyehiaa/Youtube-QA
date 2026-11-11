# YouTube QA

A FastAPI-based RAG application for answering questions about YouTube videos using transcript retrieval, vector search, and an LLM-powered chat workflow built with LangChain, OpenAI models, and a vector database (Pinecone). The project ingests a video, extracts/transcribes content, chunks it into searchable segments, embeds those segments in Pinecone, and answers questions with source citations.

## What it does

- Ingests YouTube video URLs and loads transcript data
- Splits transcripts into searchable chunks
- Embeds chunks with OpenAI and stores them in Pinecone
- Retrieves the most relevant transcript segments for a user question
- Generates grounded answers with citation timestamps
- Produces video overviews from transcript content
- Supports a Vue-based frontend for browsing videos and chatting
- Includes evaluation scripts for LangSmith-based quality checks

## Repository layout

- `app/` — FastAPI backend and application logic
- `frontend/` — Vue frontend
- `data/` — local data and generated artifacts
- `scripts/` — dataset and utility scripts
- `evaluate_langsmith.py` — LangSmith evaluation entry point

## Prerequisites

- Python 3.12
- Node.js 18+ for the frontend
- Access to the following services:
  - OpenAI API key
  - Pinecone API key and an index
  - Optional: LangSmith API key for evaluation runs

Create a `.env` file in the project root with values like:

```bash
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=youtube-qa
CORS_ORIGINS=http://localhost:5173

# Optional for experiment tracking
LANGSMITH_API_KEY=your_langsmith_key
```

## Getting started

### 1) Set up the Python environment

```bash
source .venv312/bin/activate
python -m pip install -r requirements.txt
```

If you do not already have the virtual environment, create it with:

```bash
python3.12 -m venv .venv312
source .venv312/bin/activate
python -m pip install -r requirements.txt
```

### 2) Run the backend

```bash
source .venv312/bin/activate
uvicorn app.main:app --reload --port 8000
```

The API is available at:

- Health check: `http://127.0.0.1:8000/api/health`
- Swagger docs: `http://127.0.0.1:8000/docs`

### 3) Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Then open the local Vite URL shown in the terminal.

## Example usage

### Ingest a video

```bash
curl -X POST http://127.0.0.1:8000/api/videos \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=SLHCfIUTYZI"}'
```

### Ask a question about an ingested video

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id":"demo-session",
    "video_id":"SLHCfIUTYZI",
    "message":"What is data streaming?"
  }'
```

### Search indexed videos

```bash
curl -X POST http://127.0.0.1:8000/api/videos/search \
  -H "Content-Type: application/json" \
  -d '{"query":"data streaming"}'
```

## Evaluation

Run the LangSmith evaluation script:

```bash
source .venv312/bin/activate
python evaluate_langsmith.py
```

`evaluate_langsmith.py` runs a dataset-backed evaluation using LangSmith to compare generated answers against expected evidence and scoring criteria.

## Notes

- This project is designed for local or trusted deployment scenarios. Review the security and operational guidance before exposing it publicly.
- The backend stores registry data and vector metadata locally in the project, while searchable transcript content is kept in Pinecone.
