from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import data, ingest


@asynccontextmanager
async def lifespan(app: FastAPI):
    # If you add a database later, initialize tables or migrations here.
    yield


app = FastAPI(
    title="Fuel Monitor API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
app.include_router(data.router, tags=["Read"])
