bct-hack — Groq test pipeline

Setup

1) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

2) Install dependencies
pip install -r requirements.txt

3) Configure environment variables
Create a `.env` file in the project root (or update existing) with:
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=mixtral-8x7b-32768
DATA_PATH=data/movies_sample.csv

4) Run the pipeline
python test_pipeline.py

Notes
- Ensure `data/movies_sample.csv` exists (sample provided in `data/`).
- If you need a different Groq model, update `GROQ_MODEL_NAME` in `.env`.

Docker

Build and run with Docker:

```bash
docker build -t bct-hack:latest .
docker run -p 8000:8000 --env-file .env bct-hack:latest
```

Or with docker-compose:

```bash
docker-compose up --build
```

Development: reuse your host `.venv` to avoid reinstalling

If you already have a working `.venv` in the project root and want the container
to reuse it (fast, low-resource dev flow), build the dev image which copies
the `.venv` into the image at build time and runs from it:

```bash
# Ensure `.venv` exists in the project root and was created on the same OS/arch
docker build -t bct-hack:dev -f Dockerfile.dev .
docker run --rm -p 8000:8000 --env-file .env bct-hack:dev
```

Notes and caveats:
- This approach assumes the host `.venv` is compatible with the base image (same CPU architecture and Linux libc). If you run Docker on the same Linux host, this usually works.
- If you see import errors for compiled extensions (e.g., `scikit-learn`, `numpy`), use the wheelhouse approach instead (generate wheels locally and copy them into the image).
