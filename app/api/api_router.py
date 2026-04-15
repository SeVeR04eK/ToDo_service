from fastapi import APIRouter

from app.api.routers import *

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(tasks_router)
