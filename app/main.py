from fastapi import FastAPI

from app.routes.ask import router as ask_router
from app.routes.upload import router as upload_router


app = FastAPI(
    title="Document Q&A Agent",
    description="Agentic document Q&A system using RAG, tools, Chroma and Groq.",
    version="1.0.0",
)


app.include_router(upload_router)
app.include_router(ask_router)


@app.get("/")
def root():
    return {
        "name": "Document Q&A Agent",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }