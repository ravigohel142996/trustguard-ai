# FastAPI Backend (Coming Soon)
# This will handle the AI model inference and API endpoints

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "TrustGuard AI Backend API - Coming Soon"}

# TODO: Add endpoints for:
# - /analyze - Main analysis endpoint
# - /health - Health check
# - /models - Model information
