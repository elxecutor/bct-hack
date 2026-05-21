import os
import json
from groq import Groq

class UserSimulationAgent:
    """
    Task A: User Modeling Agent (Native Groq Implementation)
    Builds an agent that understands users deeply enough to simulate reviews,
    capturing tone, rating behaviour, and contextual nuance.
    """
    def __init__(self):
        # Initializing the native Groq SDK client
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")

    def simulate_review(self, user_history: list, item_metadata: dict) -> dict:
        """
        Takes user persona (history) and product details as input.
        Generates simulated star ratings and written reviews for unseen items.
        Optimized for both RMSE accuracy and ROUGE text quality.
        """
        history_str = ""
        if not user_history:
            history_str = "No historical logs available for this persona (Cold-start configuration)."
        else:
            for i, review in enumerate(user_history):
                history_str += (
                    f"\nPast Review {i+1}:\n"
                    f"- Item Title: {review.get('title', 'Unknown')}\n"
                    f"- Score Given: {review.get('score', 3.0)}/5\n"
                    f"- Headline: {review.get('summary', '')}\n"
                    f"- Content: {review.get('text', '')}\n"
                )

        system_prompt = f"""You are an elite behavioral user-modeling agent tasked with replicating a consumer's exact evaluation profile. Your target is maximizing both Text Quality (ROUGE similarity alignment) and Rating Accuracy (minimizing RMSE) against actual ground truth.

--- START USER HISTORICAL PERSONA ---
{history_str}
--- END USER HISTORICAL PERSONA ---

CRITICAL STEP-BY-STEP EXECUTION PIPELINE:

1. SCORE CALIBRATION (Defeating Positivity Bias): Compare the target item's genres, actors, and descriptions against items the user gave low ratings (1-2 stars) or high ratings (4-5 stars) in their history. If the target item contains thematic elements or genres the user historically disliked, execute a strong negative score deduction. Do not default to a safe average score.

2. TEXT STRUCTURAL ALIGNMENT: Match the typical length, sentence structure, and vocabulary size found in the historical reviews. Preserve lexical patterns and phrasing style to ensure high overlap with ground-truth text samples.

3. CULTURAL CONTEXTUALIZATION: Replicate the consumer's natural profile. Integrate cultural perspective organically if the persona context supports it, but ensure your primary vocabulary anchors map closely to the lexical baseline of the historical reviews to ensure high ROUGE overlap."""

        user_prompt = f"""Simulate this specific user's reaction to the following unseen item metadata:
- Product Title: {item_metadata.get('title', 'Unknown')}
- Categories/Genres: {item_metadata.get('categories', 'Unknown')}
- Product Description: {item_metadata.get('description', 'No description available')}
- Directors: {item_metadata.get('directors', 'N/A')}
- Actors/Cast: {item_metadata.get('actors', 'N/A')}

You MUST output your response strictly as a single JSON object. Do not include markdown formatting or extra text outside the JSON block.
Match this exact schema:
{{
    "score": (a float representing rating accuracy between 1.0 and 5.0, reflecting exact calculated preference based on contrast analysis),
    "summary": "A short headline mirroring the user's historical summary length and style",
    "text": "The full simulated review text tracking historical structural fidelity, vocabulary choice, and emotional scale"
}}"""

        # Using Groq's native JSON mode structure with improved model
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)