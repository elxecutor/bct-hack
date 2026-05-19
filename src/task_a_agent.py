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

        # Prompt modified to explicitly request Nigerian nuances to secure bonus marks
        system_prompt = f"""You are a specialized behavioral user-modeling agent. Your objective is to achieve high behavioral fidelity.
Analyze the historical profile provided below to extract rating patterns, critical lens, text length, and vocabulary quirks.

--- START USER HISTORICAL PERSONA ---
{history_str}
--- END USER HISTORICAL PERSONA ---

CRITICAL HACKATHON DIRECTIVE: You will receive additional marks if your simulation is contextualized to behave and sound like Nigerians.
Infuse natural Nigerian English structures, phrasing, expressions (such as 'abeg', 'so far so good', 'pure vibes', 'no caps'), and local contextual priorities if the history or product allows."""

        user_prompt = f"""Simulate this specific user's reaction to the following unseen item metadata:
- Product Title: {item_metadata.get('title', 'Unknown')}
- Categories/Genres: {item_metadata.get('categories', 'Unknown')}
- Product Description: {item_metadata.get('description', 'No description available')}
- Directors: {item_metadata.get('directors', 'N/A')}
- Actors/Cast: {item_metadata.get('actors', 'N/A')}

You MUST output your response strictly as a single JSON object. Do not include markdown formatting or extra text outside the JSON block.
Match this exact schema:
{{
    "score": (a float representing rating accuracy between 1.0 and 5.0),
    "summary": "A short headline capturing the core sentiment",
    "text": "The full simulated review text capturing the persona's tone, nuance, and structural behavior"
}}"""

        # Using Groq's native JSON mode structure
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