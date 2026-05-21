# bct-hack — Groq test pipeline

## Overview

`bct-hack` is a small FastAPI + LLM pipeline that demonstrates two tasks used in the hackathon brief:

- Task A — User Modeling: simulates a user review and rating for a target item using historical reviews.
- Task B — Recommendation: generates contextual, chain-of-thought recommendations given a user profile and a candidate pool.

## Code pointers

- API entrypoint: [backend/src/main.py](backend/src/main.py)
- Data handling: [backend/src/data_loader.py](backend/src/data_loader.py)
- Task A agent (user simulation): [backend/src/task_a_agent.py](backend/src/task_a_agent.py)
- Task B agent (recommendation): [backend/src/task_b_agent.py](backend/src/task_b_agent.py)
- Example env template: [.env.example](.env.example)
- Docker: [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml)
- Backend documentation: [backend/README.md](backend/README.md)

## API

Two main endpoints are exposed by the FastAPI app in `backend/src/main.py`:

- POST `/simulate` — Task A: payload `{"userId": "<id>", "productId": "<id>"}`. Returns a simulated review and numeric rating based on the user's history.
- POST `/recommend` — Task B: payload `{"userId": "<id>", "conversationHistory": [{"role":"user","content":"..."}] }`. Returns an object with `reasoning` (chain-of-thought) and `recommendations` array.

### Example curl (simulate):

```bash
curl -sS -X POST http://127.0.0.1:8000/simulate \
	-H "Content-Type: application/json" \
	-d '{"userId":"AWPODHOB4GFWL","productId":"B004BH1TN0"}'
```

### Example curl (recommend):

```bash
curl -sS -X POST http://127.0.0.1:8000/recommend \
	-H "Content-Type: application/json" \
	-d '{"userId":"AWPODHOB4GFWL"}'
```

## Data

The pipeline expects a CSV dataset at `backend/data/movies_sample.csv` with columns used in `backend/src/data_loader.py` (e.g. `userId`, `productId`, `title`, `description`, `score`, `time`, `categories`). `MovieDataLoader` provides `get_user_history()` and `get_movie_metadata()` and includes a lightweight TF-IDF semantic search helper `semantic_search()`.

## Environment variables

Copy `.env.example` to `.env` and fill the values:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=llama-3.1-8b-instant
DATA_PATH=backend/data/movies_sample.csv
```

## Local dev (no Docker)

1. Create and activate a venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies and run:

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.src.main:app --host 0.0.0.0 --port 8000
```

## Docker

Standard build & run (preferred for distribution):

```bash
docker build -t bct_agent_api .
docker run -p 8000:8000 --env-file .env -v ./backend/data:/app/data bct_agent_api
```

## Testing & verification

- Health check: `curl http://127.0.0.1:8000/` should return a status JSON.
- OpenAPI docs: `http://127.0.0.1:8000/docs` for interactive testing.

## 📊 Automated Live Endpoint Evaluation

To verify the system performance metrics directly across the active FastAPI HTTP endpoints, execute from the `backend/evaluations` directory:

```bash
cd backend/evaluations

# Benchmark Task A (RMSE and Token Overlap)
python run_task_a_evaluation_api.py

# Benchmark Task B (NDCG@10 and Hit Rate@10)
python run_task_b_evaluation_api.py
```

Or run all evaluations at once using the helper script:

```bash
bash backend/evaluations/run_evaluations.sh
```

Evaluation metrics will be written out cleanly to `task_a_endpoint_evaluation_metrics.csv` and `task_b_endpoint_evaluation_metrics.csv` respectively.