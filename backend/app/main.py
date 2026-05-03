from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from .models import database, db_models
from .api import auth, endpoints
from .services import model_service

# Create database tables
db_models.Base.metadata.create_all(bind=database.engine)

from sqlalchemy import text
# Auto-migration hotfix for adding 'name' column
try:
    with database.engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR DEFAULT 'User';"))
except Exception as e:
    pass # Column likely already exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models at startup
    model_service.load_models()
    yield
    # Clean up on shutdown if necessary
    pass

app = FastAPI(title="Fruit Analysis API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, configure to restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Timeout Middleware
REQUEST_TIMEOUT = 30.0 # 30 seconds max per request

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        # Wrap the route execution in asyncio.wait_for
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT)
    except asyncio.TimeoutError:
        logging.error(f"Request timeout on {request.url.path}")
        return JSONResponse(
            status_code=504,
            content={"detail": "Request Timeout. The server took too long to process the image."}
        )

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(endpoints.router, prefix="/api", tags=["api"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Fruit Analysis API"}
