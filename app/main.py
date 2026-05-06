from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import logging
import sys

logging.basicConfig(
    stream=sys.stdout, 
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

from app.limiter.limiter import limiter

from app.media.routes import router as MediaRouter
from app.catalog.routes import router as CatalogRouter
from app.collections.routes import router as CollectionRouter
from app.games.routes import router as GameRouter
from app.discover.routes import router as DiscoverRouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(MediaRouter)
app.include_router(CatalogRouter)
app.include_router(CollectionRouter)
app.include_router(GameRouter)
app.include_router(DiscoverRouter)
