import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import analytics, audit, auth, documents, gis, records, reports
from app.config import settings
from app.database.session import Base, engine
from app import models  # noqa: F401 -- import registers all models on Base.metadata

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("bhumi_praman")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Bhumi Praman API starting up. DB: %s", settings.DATABASE_URL)
    yield


app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="Intelligent Land Record Digitization &amp; Validation System — SIH 2026, PS 26018 (prototype).",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Centralized error handling (spec section 32): the client never sees a
# raw Python exception or stack trace. Real errors are logged server-side. ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Something went wrong while processing this request. Please try again."},
    )


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok", "app": settings.APP_NAME}


app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(records.router)
app.include_router(analytics.router)
app.include_router(gis.router)
app.include_router(reports.router)
app.include_router(audit.router)
