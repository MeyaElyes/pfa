from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=True)

from backend.database.database import engine
from backend.routes import data, ingest
try:
    from backend.routes import prophet_routes
    _HAS_PROPHET = True
except Exception:
    prophet_routes = None
    _HAS_PROPHET = False
from backend.database import models
from backend.database.seed import seed_stations
from backend.agent.watcher import start_watcher


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_stations()
    start_watcher()
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
models.Base.metadata.create_all(bind=engine)
app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
app.include_router(data.router, tags=["Read"])
if _HAS_PROPHET and prophet_routes is not None:
    app.include_router(prophet_routes.router)
