from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import os

from app.database import init_db
from app.seed_data import seed_initial_data
from app.routes import router

app = FastAPI(
    title="Enterprise Shopping API",
    description="Core order processing and checkout system.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.on_event("startup")
def startup():
    init_db()
    seed_initial_data()

@app.get("/")
def root():
    return {"message": "Enterprise Shopping API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router)