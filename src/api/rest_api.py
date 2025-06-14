"""
REST API for the Ansible TinyLlama 3 integration.
"""
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from src.llm_engine.model_loader import load_model
from src.utils.logger import setup_logger

# Initialize logger
logger = setup_logger(name="rest_api")

# Read configuration
API_VERSION = "1.0.0"
PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"

# Initialize FastAPI app
app = FastAPI(
    title="Ansible TinyLlama Integration API",
    description="API for integrating TinyLlama 3 with Ansible automation",
    version=API_VERSION,
    docs_url="/docs" if not PRODUCTION else None,
    redoc_url="/redoc" if not PRODUCTION else None,
)

# Define CORS origins for production
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

# Add production origins if specified
cors_origins = os.getenv("CORS_ORIGINS")
if cors_origins:
    origins.extend(cors_origins.split(","))

# Add CORS middleware with proper security
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-API-Version"],
)

# Model and tokenizer instances
model = None
tokenizer = None

# Request/response models
class PlaybookRequest(BaseModel):
    """Request model for playbook generation."""
    description: str
    target_os: Optional[str] = "Linux"
    additional_context: Optional[str] = None

class PlaybookResponse(BaseModel):
    """Response model for playbook generation."""
    playbook: str
    analysis: Optional[str] = None
    
class AnalysisRequest(BaseModel):
    """Request model for playbook analysis."""
    playbook: str

class AnalysisResponse(BaseModel):
    """Response model for playbook analysis."""
    analysis: str
    suggestions: List[str]
    security_issues: List[str]

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    model_loaded: bool
    timestamp: str

# Application startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the model during startup."""
    global model, tokenizer
    
    try:
        model_name = os.getenv("MODEL_NAME", "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T")
        quantization = os.getenv("QUANTIZATION", "4bit")
        if quantization.lower() == "none":
            quantization = None
        
        logger.info(f"Loading model {model_name} with quantization {quantization}")
        model, tokenizer = load_model(model_name=model_name, quantization=quantization)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        # Don't raise an exception here, let the health endpoint report the issue

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global model, tokenizer
    
    logger.info("Shutting down API")
    # Clean up model resources
    model = None
    tokenizer = None

# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok" if model is not None else "error",
        "version": API_VERSION,
        "model_loaded": model is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/generate_playbook", response_model=PlaybookResponse)
async def generate_playbook(request: PlaybookRequest):
    """Generate an Ansible playbook from a natural language description."""
    if not model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded, check server health"
        )
    
    logger.info(f"Generating playbook for: {request.description[:50]}...")
    
    try:
        # Here you would implement the actual playbook generation using the model
        # For now we'll return a placeholder
        playbook = f"""---
# Ansible playbook generated for: {request.description}
# Target OS: {request.target_os}
# Generated at: {datetime.utcnow().isoformat()}

- name: Sample generated playbook
  hosts: all
  become: true
  tasks:
    - name: Echo a message
      debug:
        msg: "This is a placeholder for actual LLM-generated content"
"""
        
        return {
            "playbook": playbook,
            "analysis": "This is a placeholder for LLM-generated analysis of the playbook."
        }
    except Exception as e:
        logger.error(f"Error generating playbook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating playbook: {str(e)}"
        )

@app.post("/analyze_playbook", response_model=AnalysisResponse)
async def analyze_playbook(request: AnalysisRequest):
    """Analyze an existing Ansible playbook."""
    if not model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded, check server health"
        )
    
    logger.info("Analyzing playbook")
    
    try:
        # Here you would implement the actual playbook analysis using the model
        # For now we'll return a placeholder
        return {
            "analysis": "This is a placeholder for LLM analysis of the playbook.",
            "suggestions": [
                "Consider using handlers for service restarts",
                "Add tags to tasks for better organization"
            ],
            "security_issues": [
                "No significant security issues detected in this playbook"
            ]
        }
    except Exception as e:
        logger.error(f"Error analyzing playbook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing playbook: {str(e)}"
        )

@app.middleware("http")
async def add_api_version_header(request: Request, call_next):
    """Add API version header to all responses."""
    response = await call_next(request)
    response.headers["X-API-Version"] = API_VERSION
    return response

# Main entry point for direct execution
def main(host="127.0.0.1", port=8000, debug=False):
    """Start the API server."""
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run("src.api.rest_api:app", host=host, port=port, reload=debug)

if __name__ == "__main__":
    main()
