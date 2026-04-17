from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.database import engine, Base
from backend.routes import ingest, data, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created")
    yield
    print("[STOP] Shutting down Fuel Monitor API")

app = FastAPI(
    title="Fuel Monitor API",
    description="Real-time fuel station monitoring system for Tunisia — tracks prices, "
                "stock levels, consumption, and generates anomaly alerts.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(data.router, tags=["Data"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "version": "2.0.0"}
