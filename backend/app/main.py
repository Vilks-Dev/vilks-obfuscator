import uuid
import logging
from fastapi import FastAPI, UploadFile, File, Form, Request, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import io

from backend.app.config import settings
from backend.app.logging_config import setup_logging, correlation_id_ctx
from backend.app.utils import validate_filename, validate_python_code
from backend.app.sandbox import run_in_sandbox

setup_logging()
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Python Obfuscator API", docs_url="/docs" if settings.APP_ENV == "development" else None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    corr_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
    token = correlation_id_ctx.set(corr_id)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-Id"] = corr_id
        return response
    finally:
        correlation_id_ctx.reset(token)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    corr_id = correlation_id_ctx.get()
    logger.error(f"Unhandled exception occurred: {str(exc)}", exc_info=True)
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "correlation_id": corr_id
        }
    )
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8080"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@app.get("/health")
@limiter.limit(settings.RATE_LIMIT_REQUESTS)
async def health(request: Request):
    import docker
    docker_ok = False
    try:
        client = docker.from_env()
        client.ping()
        docker_ok = True
    except Exception:
        pass
    
    return {
        "status": "healthy",
        "sandbox_ready": docker_ok,
        "environment": settings.APP_ENV
    }

@app.post("/obfuscate")
@limiter.limit(settings.RATE_LIMIT_UPLOADS)
async def obfuscate_file(
    request: Request,
    file: UploadFile = File(...),
    level: str = Form("standard")
):
    if level not in ["basic", "standard", "hardcore"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid obfuscation level. Choose basic, standard, or hardcore."}
        )

    clean_name = validate_filename(file.filename)
    
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "File size exceeds 10 MB limit."}
        )

    if clean_name.endswith(".py"):
        try:
            validate_python_code(content.decode("utf-8"))
        except UnicodeDecodeError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Python file must be UTF-8 encoded text."}
            )

    result_bytes = run_in_sandbox(content, clean_name, level)
    
    return StreamingResponse(
        io.BytesIO(result_bytes),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="obfuscated_{clean_name}"'}
    )

@app.post("/obfuscate-text")
@limiter.limit(settings.RATE_LIMIT_REQUESTS)
async def obfuscate_text(
    request: Request,
    payload: dict
):
    code = payload.get("code", "")
    level = payload.get("level", "standard")

    if not code:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Code parameter is missing"}
        )

    if level not in ["basic", "standard", "hardcore"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid obfuscation level. Choose basic, standard, or hardcore."}
        )

    validate_python_code(code)
    
    code_bytes = code.encode("utf-8")
    result_bytes = run_in_sandbox(code_bytes, "script.py", level)
    
    return {
        "obfuscated_code": result_bytes.decode("utf-8")
    }


