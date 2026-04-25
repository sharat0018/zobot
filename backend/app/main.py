from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.database import init_db
import os

app = FastAPI(
    title="Zobot API",
    description="AI-Powered Wealth Operating System for Indian Retail Banking",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Initialize database
@app.on_event("startup")
def startup_event():
    init_db()

# Include routes
app.include_router(router, prefix="/api/v1", tags=["Zobot"])

@app.get("/")
def root():
    return {
        "message": "Zobot API - AI Wealth Operating System",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
