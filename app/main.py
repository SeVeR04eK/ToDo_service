from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.api import api_router
from app.core.cleanup import clean_tokens_task

@asynccontextmanager
async def lifespan(_app: FastAPI):

    task = asyncio.create_task(clean_tokens_task())

    yield

    task.cancel()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)