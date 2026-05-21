import os
import json
import time
from collections import OrderedDict

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
DATA_PATH = os.getenv("DATA_PATH", "../data/movies_sample.csv")
SAMPLE_SIZE = int(os.getenv("TASK_B_SAMPLE_SIZE", "10"))
TIMEOUT_SECONDS = int(os.getenv("TASK_B_REQUEST_TIMEOUT", "120"))


def calculate_ndcg_at_k(predicted_ids, relevant_ids, k=10):
    """Compute binary-relevance NDCG@k.

    This is a standard NDCG implementation: each relevant item contributes 1,
    irrelevant items contribute 0, and the score is normalized by the ideal DCG.
    The result is bounded in [0, 1].
    """
    if not predicted_ids or not relevant_ids:
        return 0.0

    ranked = list(OrderedDict.fromkeys(predicted_ids))[:k]

    def dcg(items):
        score = 0.0
        for rank, item_id in enumerate(items):
            rel = 1.0 if item_id in relevant_ids else 0.0
            if rel > 0:
                score += rel / np.log2(rank + 2)
        return score

    actual_dcg = dcg(ranked)
    ideal_hits = min(len(relevant_ids), k)
    ideal_ranking = list(relevant_ids)[:ideal_hits]
    ideal_dcg = dcg(ideal_ranking)

    if ideal_dcg == 0:
        return 0.0
    return float(actual_dcg / ideal_dcg)


def calculate_hit_rate(predicted_ids, relevant_ids, k=10):
    ranked = list(OrderedDict.fromkeys(predicted_ids))[:k]
    return 1 if any(item_id in relevant_ids for item_id in ranked) else 0


def call_recommend_api(user_id, conversation_history=None):
    payload = {
        "userId": user_id,
        "conversationHistory": conversation_history or []
    }
    response = requests.post(
        f"{API_URL.rstrip('/')}/recommend",
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def run_task_b_endpoint_evaluation():
    print("📋 Loading dataset and preparing Task B endpoint evaluation...")
    df = pd.read_csv(DATA_PATH)

    user_items = df.groupby("userId")["productId"].apply(set).to_dict()
    valid_users = [user_id for user_id, items in user_items.items() if len(items) >= 1]

    if not valid_users:
        print("No users with interaction history were found.")
        return

    sample_count = min(SAMPLE_SIZE, len(valid_users))
    sampled_users = np.random.choice(valid_users, size=sample_count, replace=False)

    ndcg_scores = []
    hit_rates = []
    processed_users = []

    # Open raw outputs file to capture full model responses per user
    raw_output_path = "task_b_raw_outputs.jsonl"
    raw_f = open(raw_output_path, "w", encoding="utf-8")

    print(f"🤖 Evaluating Task B endpoint on {len(sampled_users)} users against {API_URL}...\n")

    for user_id in sampled_users:
        relevant_products = user_items.get(user_id, set())
        if not relevant_products:
            print(f"⏭️  Skipping user {user_id}: no interaction history")
            continue

        try:
            started_at = time.time()
            output = call_recommend_api(user_id)
            # Save the raw model response with the input case
            record = {
                "input_case": {"userId": user_id, "relevant_products": list(relevant_products)},
                "model_response": output,
                "meta": {"latency_seconds": time.time() - started_at},
            }
            raw_f.write(json.dumps(record, ensure_ascii=False) + "\n")

            elapsed = time.time() - started_at

            recommendations = output.get("recommendations", [])
            predicted_ids = [rec.get("productId") for rec in recommendations if rec.get("productId")]

            ndcg_at_10 = calculate_ndcg_at_k(predicted_ids, relevant_products, k=10)
            hit_at_10 = calculate_hit_rate(predicted_ids, relevant_products, k=10)

            ndcg_scores.append(ndcg_at_10)
            hit_rates.append(hit_at_10)
            processed_users.append(user_id)

            print(f"✅ User: {user_id}")
            print(f"   - API latency: {elapsed:.2f}s")
            print(f"   - Ground truth items: {len(relevant_products)}")
            print(f"   - Recommendations returned: {len(predicted_ids)}")
            print(f"   - NDCG@10: {ndcg_at_10:.4f}")
            print(f"   - Hit Rate@10: {hit_at_10}")
            print()

        except Exception as exc:
            print(f"❌ Error processing user {user_id}: {exc}\n")
            continue

    # close raw outputs file
    raw_f.close()

    if ndcg_scores:
        final_ndcg = float(np.mean(ndcg_scores))
        final_hit_rate = float(np.mean(hit_rates))

        print("\n📊 --- FINAL TASK B ENDPOINT EVALUATION METRICS ---")
        print(f"NDCG@10 (Ranking Quality): {final_ndcg:.4f} (bounded 0-1)")
        print(f"Hit Rate@10: {final_hit_rate * 100:.2f}%")

        results_df = pd.DataFrame({
            "user_id": processed_users,
            "ndcg_at_10": ndcg_scores,
            "hit_rate_at_10": hit_rates,
        })
        results_df.to_csv("task_b_endpoint_evaluation_metrics.csv", index=False)
        print("💾 Saved evaluation data to 'task_b_endpoint_evaluation_metrics.csv'")
    else:
        print("No users were successfully processed for endpoint evaluation.")


if __name__ == "__main__":
    run_task_b_endpoint_evaluation()
