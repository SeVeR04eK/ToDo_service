from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings
from app.presentation.api.middleware.security_header import SecurityHeadersMiddleware
from app.presentation.api.middleware.logging import RequestLoggingMiddleware
from app.presentation.api.middleware.correlation import CorrelationIdMiddleware


def setup_middlewares(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    app.add_middleware(
        SecurityHeadersMiddleware,
        settings=settings,
    )

    app.add_middleware(RequestLoggingMiddleware)

    app.add_middleware(CorrelationIdMiddleware)
