"""FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(title="Regatta", version="0.1.0")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
