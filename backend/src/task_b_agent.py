import os
import json
from groq import Groq

class RecommendationAgent:
    """
    Task B: Recommendation Agent (Native Groq Implementation)
    Delivers personalized recommendations going beyond collaborative filtering to 
    contextual, conversational retrieval.
    """
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")

    def generate_recommendations(self, user_persona: list, candidate_catalog: list, conversation_context: list = None) -> dict:
        """
        Takes user persona and conversational signals as input to rank and recommend items.
        Architected to satisfy cold-start and multi-turn parameters safely.
        """
        if not user_persona:
            history_summary = "Cold-start scenario. No interaction logs exist for this user yet. Prioritize high-quality, popular selections tailored to their immediate context."
        else:
            history_summary = "User interaction logs: " + ", ".join([f"'{item.get('title', 'Unknown')}' ({item.get('score', 3)} Stars)" for item in user_persona])

        turn_history = ""
        if conversation_context:
            turn_history = "\nActive Multi-turn Conversation Threads:\n" + "\n".join([f"- {msg['role']}: {msg['content']}" for msg in conversation_context])

        # Safely extract catalog parameters to defend against float/NaN values
        candidates_str = ""
        for item in candidate_catalog:
            prod_id = item.get('productId', 'N/A')
            title = item.get('title', 'Unknown')
            categories = item.get('categories', 'Unknown')
            
            # Defensive check against missing description fields (NaN floats)
            raw_description = item.get('description', '')
            if not isinstance(raw_description, str):
                raw_description = "No description available."
            
            candidates_str += f"- ID: {prod_id} | Title: {title} | Genre: {categories} | Description: {raw_description[:120]}...\n"

        # Explicitly enforcing the 'reason before recommending' design metric
        system_prompt = f"""You are an intelligent Conversational Recommendation Agent.
Your workflow must rigorously apply Chain-of-Thought (CoT) reasoning before finalizing recommendations.

--- USER PARAMETERS & HISTORICAL CONTEXT ---
{history_summary}
{turn_history}
--------------------------------------------

Your internal agent execution workflow must:
1. Deduce the user's implicit preferences, mood, and contextual intent.
2. Identify cross-domain overlaps or specific content intersections.
3. Methodically screen out mismatched items from the candidate pool.
4. Finalize selection list emphasizing Contextual Relevance."""

        user_prompt = f"""Evaluate these item candidates and recommend the top matches:
{candidates_str}

You MUST return your output strictly as a JSON object matching this structural schema:
{{
    "reasoning": "Detailed, step-by-step analytical reasoning paragraph explaining the match hypothesis BEFORE making decisions",
    "recommendations": [
        {{"productId": "string", "title": "string", "rank": 1}},
        {{"productId": "string", "title": "string", "rank": 2}}
    ]
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)