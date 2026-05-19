import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# --- BULLETPROOF HACKATHON IMPORT FALLBACK ---
# This ensures imports work locally with Uvicorn and containerized with Docker
try:
    from src.data_loader import MovieDataLoader
    from src.task_a_agent import UserSimulationAgent
    from src.task_b_agent import RecommendationAgent
except ModuleNotFoundError:
    from data_loader import MovieDataLoader
    from task_a_agent import UserSimulationAgent
    from task_b_agent import RecommendationAgent
# ---------------------------------------------

# Load your .env configurations
load_dotenv()

app = FastAPI(
    title="DSN X BCT LLM Agent Challenge Application",
    description="Containerized API service serving Task A and Task B."
)

# 2. Resolve data pathway safely
DATA_PATH = os.getenv("DATA_PATH", "data/movies_sample.csv")
if not os.path.exists(DATA_PATH):
    raise RuntimeError(f"Data file not found at {DATA_PATH}. Check your .env configuration.")

# 3. Initialize your modular business logic engines
data_loader = MovieDataLoader(DATA_PATH)
task_a_agent = UserSimulationAgent()
task_b_agent = RecommendationAgent()


# --- REQUEST & RESPONSE SCHEMAS ---
class SimulationRequest(BaseModel):
    userId: str
    productId: str

class ConversationTurn(BaseModel):
    role: str
    content: str

class RecommendationRequest(BaseModel):
    userId: str
    conversationHistory: Optional[List[ConversationTurn]] = None


@app.get("/", tags=["Root"])
def read_root():
    """
    A helpful landing route to prevent 404 errors on the base path.
    """
    return {
        "status": "online",
        "competition": "DSN X BCT LLM Agent Challenge 3.0",
        "documentation": "Navigate to /docs to test the interactive API endpoints."
    }

@app.post("/simulate", tags=["Task A: User Modeling"])
def run_simulation(payload: SimulationRequest):
    """
    Task A: Takes user persona (history) and product details as input, 
    and generates simulated reviews and ratings as output.
    """
    history = data_loader.get_user_history(payload.userId)
    metadata = data_loader.get_movie_metadata(payload.productId)
    
    if not metadata:
        raise HTTPException(
            status_code=404, 
            detail=f"Product metadata for ID {payload.productId} not found."
        )
        
    try:
        simulated_output = task_a_agent.simulate_review(history, metadata)
        return simulated_output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend", tags=["Task B: Recommendation"])
def run_recommendation(payload: RecommendationRequest):
    """
    Task B: Takes user persona as input and produces personalized recommendations 
    as output, executing an internal workflow that reasons before recommending.
    """
    # Fetch chronological interaction profile to build the context
    history = data_loader.get_user_history(payload.userId)
    
    # Process conversation blocks if they exist to handle multi-turn constraints
    chat_context = []
    if payload.conversationHistory:
        chat_context = [turn.dict() for turn in payload.conversationHistory]

    # Build a short free-text query from recent user history to retrieve candidates
    if history:
        query_terms = [h.get('title', '') for h in history if h.get('title')]
        query = ' '.join(query_terms) if query_terms else 'popular movies'
    else:
        query = 'popular movies'

    # Use the lightweight semantic search we added to the data loader
    candidate_pool = data_loader.semantic_search(query=query, k=20)
    
    try:
        recommendation_output = task_b_agent.generate_recommendations(
            user_persona=history, 
            candidate_catalog=candidate_pool, 
            conversation_context=chat_context
        )
        return recommendation_output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))