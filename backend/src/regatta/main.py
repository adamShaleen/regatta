"""FastAPI application entry point."""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from regatta.api.auth import router as auth_router
from regatta.api.routes.games import router
from regatta.api.routes.ws import router as ws_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield  # startup code before, shutdown code after


origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(title="Regatta", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(ws_router, prefix="/games")
app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
