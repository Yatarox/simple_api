from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.database import Base, engine
import src.models
from src.routes import (
    auth,
    users,
    groups,
    events,
    threads,
    photos,
    polls,
    tickets,
    shopping,
    carpooling,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="My Social Networks API",
    description="Refonte API Facebook — Événements, Groupes, Sondages, Billetterie…",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(PermissionError)
async def permission_error_handler(request: Request, exc: PermissionError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(events.router)
app.include_router(threads.router)
app.include_router(photos.router)
app.include_router(polls.router)
app.include_router(tickets.router)
app.include_router(shopping.router)
app.include_router(carpooling.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "version": "2.0.0"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}