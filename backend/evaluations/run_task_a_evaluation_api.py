import os
import json
from math import sqrt

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
DATA_PATH = os.getenv("DATA_PATH", "../data/movies_sample.csv")
SAMPLE_SIZE = int(os.getenv("TASK_A_SAMPLE_SIZE", "10"))
TIMEOUT_SECONDS = int(os.getenv("TASK_A_REQUEST_TIMEOUT", "120"))


def calculate_rmse(actual, predicted):
    actual = np.array(actual, dtype=float)
    predicted = np.array(predicted, dtype=float)
    return sqrt(np.mean((actual - predicted) ** 2))


def simple_token_overlap(actual_text, predicted_text):
    """A lightweight proxy for ROUGE using normalized word overlap."""
    actual_words = set(str(actual_text).lower().split())
    predicted_words = set(str(predicted_text).lower().split())
    if not actual_words:
        return 0.0
    intersection = actual_words.intersection(predicted_words)
    return len(intersection) / len(actual_words)


def call_simulate_api(user_id, product_id):
    payload = {
        "userId": user_id,
        "productId": product_id,
    }
    response = requests.post(
        f"{API_URL.rstrip('/')}/simulate",
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def run_task_a_endpoint_evaluation():
    print("📋 Loading dataset and preparing Task A endpoint evaluation...")
    df = pd.read_csv(DATA_PATH)

    required_cols = {"userId", "productId", "score", "text"}
    missing = required_cols.difference(df.columns)
    if missing:
        raise RuntimeError(f"Missing required columns in dataset: {sorted(missing)}")

    sample_count = min(SAMPLE_SIZE, len(df))
    eval_sample = df.sample(n=sample_count, random_state=42)

    actual_ratings = []
    predicted_ratings = []
    text_similarities = []
    processed_rows = []

    # Open raw outputs file to capture full model responses per case
    raw_output_path = "task_a_raw_outputs.jsonl"
    raw_f = open(raw_output_path, "w", encoding="utf-8")

    print(f"🤖 Evaluating Task A endpoint on {len(eval_sample)} rows against {API_URL}...\n")

    for _, row in eval_sample.iterrows():
        user_id = row["userId"]
        product_id = row["productId"]
        actual_score = float(row["score"])
        actual_text = row["text"]

        try:
            output = call_simulate_api(user_id, product_id)
            # Persist the raw model output with the input case for reproducibility
            record = {
                "input_case": {
                    "userId": user_id,
                    "productId": product_id,
                    "actual_score": actual_score,
                    "actual_text": actual_text,
                },
                "model_response": output,
            }
            raw_f.write(json.dumps(record, ensure_ascii=False) + "\n")

            pred_score = float(output.get("score", 3.0))
            pred_text = output.get("text", "")

            actual_ratings.append(actual_score)
            predicted_ratings.append(pred_score)
            text_similarities.append(simple_token_overlap(actual_text, pred_text))
            processed_rows.append((user_id, product_id))

            print(f"✅ User: {user_id} | Product: {product_id}")
            print(f"   - Actual score: {actual_score}")
            print(f"   - Predicted score: {pred_score}")
            print(f"   - ROUGE proxy overlap: {text_similarities[-1]:.4f}")
            print()

        except Exception as exc:
            print(f"❌ Error processing row (user={user_id}, product={product_id}): {exc}\n")
            continue

    # close raw outputs file
    raw_f.close()

    if actual_ratings:
        final_rmse = calculate_rmse(actual_ratings, predicted_ratings)
        avg_overlap = float(np.mean(text_similarities))

        print("\n📊 --- FINAL TASK A ENDPOINT EVALUATION METRICS ---")
        print(f"RMSE (Rating Accuracy): {final_rmse:.4f} (lower is better)")
        print(f"Text Quality Proxy (ROUGE-like overlap): {avg_overlap * 100:.2f}% (higher is better)")

        results_df = pd.DataFrame({
            "user_id": [u for u, _ in processed_rows],
            "product_id": [p for _, p in processed_rows],
            "actual_rating": actual_ratings,
            "predicted_rating": predicted_ratings,
            "word_overlap": text_similarities,
        })
        results_df.to_csv("task_a_endpoint_evaluation_metrics.csv", index=False)
        print("💾 Saved evaluation data to 'task_a_endpoint_evaluation_metrics.csv'")
    else:
        print("No rows were successfully processed.")


if __name__ == "__main__":
    run_task_a_endpoint_evaluation()
