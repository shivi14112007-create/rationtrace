from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.data.seed import seed_database
from backend.app.api.auth import router as auth_router
from backend.app.api.beneficiaries import router as beneficiaries_router
from backend.app.api.dealer import router as dealer_router
from backend.app.api.complaints import router as complaints_router
from backend.app.api.audits import router as audits_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.tinyfish import router as tinyfish_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is created and seeded
    Base.metadata.create_all(bind=engine)
    try:
        seed_database()
    except Exception as e:
        print(f"Startup seed notice: {e}")
    yield

app = FastAPI(
    title="RationTrace Public Distribution Intelligence API",
    description="Backend API powering PDS transparency, audit reconciliation, and grievance workflows.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
origins = settings.cors_origins_list
if "*" in origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(beneficiaries_router, prefix="/api")
app.include_router(dealer_router, prefix="/api")
app.include_router(complaints_router, prefix="/api")
app.include_router(audits_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(tinyfish_router, prefix="/api")

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": "RationTrace",
        "environment": settings.APP_ENV,
        "demo_mode": settings.DEMO_MODE
    }
