# bct-hack — DSN x BCT LLM Agent Challenge 3.0

## Overview
This repository contains Team **elxpektra**'s submission for the DSN x BCT LLM Agent Challenge. We have built a production-ready, full-stack LLM-agent system designed to model dynamic user behavior and deliver context-aware recommendations.

The system addresses the two core challenge tasks:
- **Task A (User Modeling):** An agent that simulates a user's review and star rating for an unseen item, preserving their historical tone, rating behavior, and cultural nuances.
- **Task B (Recommendation):** A conversational recommendation agent that uses Chain-of-Thought (CoT) reasoning to rank and recommend items tailored to the user's implicit preferences.

## Architecture & Modular Design
To ensure code reproducibility and scalability, the repository is cleanly separated into two environments:
* `backend/`: A FastAPI application that serves the core Agentic logic. Powered by Groq (Llama-3.1-8b-instant) for high-speed, structured JSON generation. 
* `frontend/`: A React/Vite application utilizing Tailwind and Radix UI components to provide a visual, interactive interface for the judges to explore the personas and recommendations.

### Agentic Workflow Logic
* **Task A Agent (`backend/src/task_a_agent.py`):** Uses contrastive prompt injection. It compares the target item's metadata against the user's historical likes and dislikes to prevent positivity bias. It forces the LLM to output strict JSON matching the structural habits (vocabulary size, sentiment) of the user's past reviews.
* **Task B Agent (`backend/src/task_b_agent.py`):** Implements a "Reason Before Recommending" workflow. A semantic retrieval layer (TF-IDF) first narrows the catalog pool. The LLM then generates a CoT `reasoning` paragraph deducing the user's implicit needs before emitting the final `recommendations` array.

## Quick Start (Reproducibility)

### Prerequisites
* Docker and Docker Compose
* A [Groq API Key](https://console.groq.com/)

### 1. Environment Setup
Clone the repository and set up your environment variables:
```bash
git clone [https://github.com/elxecutor/bct-hack.git](https://github.com/elxecutor/bct-hack.git)
cd bct-hack
cp .env.example .env

```

Open the `.env` file and insert your `GROQ_API_KEY`.

### 2. Run via Docker (Recommended)

We have containerized the entire stack for seamless evaluation.

```bash
docker-compose up --build

```

* The **Frontend UI** will be available at: `http://localhost:3000`
* The **Backend API** will be available at: `http://localhost:8000`
* The **Interactive API Docs** will be available at: `http://localhost:8000/docs`

### 3. Run Locally (Without Docker)

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

```

**Frontend:**

```bash
cd frontend
npm install
npm run dev

```

## API Endpoints

The system exposes two primary endpoints for automated evaluation.

### Task A: `/simulate`

Simulates a review and rating for an unseen item.

```bash
curl -X POST http://localhost:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{"userId":"A1Q6QSDVNK3L7M","productId":"B002OHDRF2"}'

```

### Task B: `/recommend`

Generates ranked recommendations based on user history.

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"userId":"A20KRG6P6HCSB1"}'

```