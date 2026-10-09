from collections import defaultdict, deque
from contextlib import asynccontextmanager
from time import monotonic

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from incidentlens.api.routes import router
from incidentlens.config import ROOT, settings
from incidentlens.pipeline import Pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    p = Pipeline(settings)
    p.load()
    app.state.pipeline = p
    yield
    p.retriever.close()


def create_app() -> FastAPI:
    app = FastAPI(title="IncidentLens", version="0.1.0", lifespan=lifespan)
    windows = defaultdict(deque)

    @app.middleware("http")
    async def boundary(request: Request, call_next):
        if request.method == "POST":
            origin = request.headers.get("origin")
            allowed = {"http://127.0.0.1:8030", "http://localhost:8030"}
            if origin and origin not in allowed:
                return JSONResponse({"detail": "Cross-origin writes are disabled"}, status_code=403)
            try:
                length = int(request.headers.get("content-length", "0"))
            except ValueError:
                return JSONResponse({"detail": "Invalid content length"}, status_code=400)
            if length > 6 * 1024 * 1024:
                return JSONResponse({"detail": "Payload too large"}, status_code=413)
            key = request.client.host if request.client else "local"
            window = windows[key]
            now = monotonic()
            while window and now - window[0] >= 60:
                window.popleft()
            if len(window) >= 20:
                return JSONResponse({"detail": "Limit: 20 writes per minute"}, status_code=429)
            window.append(now)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
        )
        return response

    app.include_router(router)
    app.mount("/static", StaticFiles(directory=ROOT / "incidentlens/static"), name="static")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(ROOT / "incidentlens/static/index.html")

    return app


app = create_app()
