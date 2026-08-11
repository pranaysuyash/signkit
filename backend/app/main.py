
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.routers import auth, extraction, workspace
from backend.app.database import Base, engine
from backend.app.paths import LOG_DIR, UPLOADS_DIR
import os
import logging
import sys
import time

# Create the database tables
Base.metadata.create_all(bind=engine)

# Set up logging with local timezone timestamps to a user-writable location

class LocalTimeFormatter(logging.Formatter):
    """Formatter that renders asctime in the user's local timezone."""

    converter = time.localtime


os.makedirs(str(LOG_DIR), exist_ok=True)
LOG_PATH = os.path.join(str(LOG_DIR), "app.log")

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

_formatter = LocalTimeFormatter(LOG_FORMAT, DATE_FORMAT)

_stream_handler = logging.StreamHandler(sys.stdout)
_stream_handler.setFormatter(_formatter)

handlers = [_stream_handler]
try:
    _file_handler = logging.FileHandler(LOG_PATH)
    _file_handler.setFormatter(_formatter)
    handlers.append(_file_handler)
except Exception:
    # If file logging fails, continue with stream-only logging
    pass

logging.basicConfig(
    level=logging.DEBUG,
    handlers=handlers,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SignKit Backend",
    description="API for user authentication and signature extraction from images.",
    version="1.0.0"
)

# Ensure uploads directory exists in a user-writable location
os.makedirs(str(UPLOADS_DIR), exist_ok=True)
logger.info(f"Uploads directory configured at: {UPLOADS_DIR}")

# Mount static files (for serving uploaded images and signatures)
try:
    app.mount("/uploads/images", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
    logger.info("Successfully mounted uploads directory")
except Exception as e:
    logger.error(f"Failed to mount uploads directory: {str(e)}")
    raise

# Configure CORS with all necessary origins
origins = [
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://127.0.0.1:8001",  # Updated to match consistent port
    "http://localhost:8001",  # Updated to match consistent port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    # Report reachability, not the absolute filesystem path — the path adds
    # no diagnostic value here (it's a fixed, config-derived location the
    # operator already knows) and needlessly discloses server-side
    # directory structure in an otherwise-public health check.
    return {
        "status": "healthy",
        "uploads_dir_exists": os.path.exists(str(UPLOADS_DIR)),
    }

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(extraction.router, prefix="/extraction", tags=["Extraction"])
app.include_router(workspace.router, prefix="/workspace", tags=["Workspace"])

# Browser-native product surface. It shares the protected /workspace API but is
# deliberately separate from the historical landing-site assets.
WORKSPACE_WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "web", "cloud_workspace")
if os.path.isdir(WORKSPACE_WEB_DIR):
    app.mount(
        "/workspace-app",
        StaticFiles(directory=WORKSPACE_WEB_DIR, html=True),
        name="workspace-app",
    )
    logger.info("Successfully mounted browser workspace assets")
else:
    logger.warning("Browser workspace assets unavailable: %s", WORKSPACE_WEB_DIR)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the SignKit API"}
