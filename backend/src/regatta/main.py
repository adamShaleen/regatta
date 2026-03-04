"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from regatta.api.routes.games import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield  # startup code before, shutdown code after


app = FastAPI(title="Regatta", version="0.1.0", lifespan=lifespan)
app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
