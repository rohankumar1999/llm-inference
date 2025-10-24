from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import asyncio
import os
from typing import Optional, Dict, List
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Inference API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # React app - configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model configurations with their TGI endpoint URLs
# These should be set via environment variables or config file
MODELS = {
    "llama-3.2-3b-base": {
        "name": "Llama 3.2 3B (Base)",
        "hf_name": "meta-llama/Llama-3.2-3B-Instruct",
        "endpoint": os.getenv("TGI_LLAMA32_BASE_ENDPOINT", "http://localhost:8080"),
    },
    "llama-3.2-3b-sft": {
        "name": "Llama 3.2 3B (SFT Prover)",
        "hf_name": "rkumar1999/Llama3.2-3B-Prover-openr1-distill-SFT",
        "endpoint": os.getenv("TGI_LLAMA32_SFT_ENDPOINT", "http://localhost:8081"),
    },
    "llama-3.2-3b-grpo": {
        "name": "Llama 3.2 3B (GRPO Prover)",
        "hf_name": "rkumar1999/Llama3.2-3B-Prover-openr1-distill-GRPO",
        "endpoint": os.getenv("TGI_LLAMA32_GRPO_ENDPOINT", "http://localhost:8082"),
    },
    "llama-3.2-3b-obt": {
        "name": "Llama 3.2 3B (OBT)",
        "hf_name": "rkumar1999/llama3.2-3b-obt",
        "endpoint": os.getenv("TGI_LLAMA32_OBT_ENDPOINT", "http://localhost:8083"),
    },
}

# Cache for model health status
model_health_cache: Dict[str, bool] = {}


class GenerateRequest(BaseModel):
    model_id: str
    prompt: str
    max_new_tokens: int = Field(default=200, ge=1, le=2048)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    repetition_penalty: float = Field(default=1.0, ge=1.0, le=2.0)


class GenerateResponse(BaseModel):
    generated_text: str
    model_id: str


class ModelInfo(BaseModel):
    id: str
    name: str
    hf_name: str
    endpoint: str
    available: bool


async def check_model_health(model_id: str, endpoint: str) -> bool:
    """Check if a TGI model endpoint is healthy"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{endpoint}/health")
            is_healthy = response.status_code == 200
            model_health_cache[model_id] = is_healthy
            return is_healthy
    except Exception as e:
        logger.warning(f"Health check failed for {model_id}: {str(e)}")
        model_health_cache[model_id] = False
        return False


async def generate_text(
    model_id: str,
    prompt: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    repetition_penalty: float
) -> str:
    """Generate text using a cloud-hosted TGI endpoint"""
    
    if model_id not in MODELS:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    endpoint = MODELS[model_id]["endpoint"]
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # TGI generate endpoint
            response = await client.post(
                f"{endpoint}/generate",
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": max_new_tokens,
                        "temperature": temperature,
                        "top_p": top_p,
                        "repetition_penalty": repetition_penalty,
                        "do_sample": temperature > 0,
                    }
                }
            )
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"TGI error for {model_id}: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"TGI generation error: {error_detail}"
                )
            
            result = response.json()
            generated_text = result.get("generated_text", "")
            
            logger.info(f"Generated {len(generated_text)} chars for {model_id}")
            return generated_text
            
    except httpx.TimeoutException:
        logger.error(f"Timeout generating text for {model_id}")
        raise HTTPException(status_code=504, detail="Generation timeout - model may be overloaded")
    except httpx.ConnectError:
        logger.error(f"Cannot connect to TGI endpoint for {model_id}: {endpoint}")
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to model endpoint. Make sure TGI is running at {endpoint}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating text for {model_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/")
async def root():
    """API root endpoint with basic info"""
    return {
        "message": "LLM Inference API - Cloud GPU Backend",
        "version": "2.0.0",
        "models": list(MODELS.keys()),
        "docs": "/docs"
    }


@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List all available models with their health status"""
    models_info = []
    
    # Check health of all models in parallel
    health_checks = [
        check_model_health(model_id, config["endpoint"])
        for model_id, config in MODELS.items()
    ]
    await asyncio.gather(*health_checks, return_exceptions=True)
    
    for model_id, config in MODELS.items():
        models_info.append(ModelInfo(
            id=model_id,
            name=config["name"],
            hf_name=config["hf_name"],
            endpoint=config["endpoint"],
            available=model_health_cache.get(model_id, False)
        ))
    
    return models_info


@app.get("/models/{model_id}/health")
async def get_model_health(model_id: str):
    """Check health status of a specific model"""
    if model_id not in MODELS:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    endpoint = MODELS[model_id]["endpoint"]
    is_healthy = await check_model_health(model_id, endpoint)
    
    return {
        "model_id": model_id,
        "endpoint": endpoint,
        "healthy": is_healthy,
        "status": "available" if is_healthy else "unavailable"
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate text using the specified model hosted on cloud GPU.
    The TGI instance must already be running at the configured endpoint.
    """
    
    if request.model_id not in MODELS:
        raise HTTPException(
            status_code=404,
            detail=f"Model {request.model_id} not found. Available: {list(MODELS.keys())}"
        )
    
    # Check if model endpoint is healthy
    endpoint = MODELS[request.model_id]["endpoint"]
    is_healthy = await check_model_health(request.model_id, endpoint)
    
    if not is_healthy:
        raise HTTPException(
            status_code=503,
            detail=f"Model {request.model_id} is not available at {endpoint}. "
                   "Make sure the TGI container is running on your GPU instance."
        )
    
    # Generate text
    logger.info(f"Generating text with {request.model_id}: {request.prompt[:50]}...")
    generated_text = await generate_text(
        request.model_id,
        request.prompt,
        request.max_new_tokens,
        request.temperature,
        request.top_p,
        request.repetition_penalty
    )
    
    return GenerateResponse(
        generated_text=generated_text,
        model_id=request.model_id
    )


@app.on_event("startup")
async def startup_event():
    """Check model endpoints on startup"""
    logger.info("Starting LLM Inference API...")
    logger.info(f"Configured models: {list(MODELS.keys())}")
    
    # Check all model endpoints
    for model_id, config in MODELS.items():
        endpoint = config["endpoint"]
        logger.info(f"  {model_id}: {endpoint}")
        is_healthy = await check_model_health(model_id, endpoint)
        status = "✓ Available" if is_healthy else "✗ Unavailable"
        logger.info(f"    {status}")
    
    logger.info("API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down LLM Inference API...")


if __name__ == "__main__":
    import uvicorn
    import os
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

