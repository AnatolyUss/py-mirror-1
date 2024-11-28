from fastapi import FastAPI

from py_mirror.app.api.api_endpoints import api_router
from py_mirror.app.api.healthcheck_endpoints import healthcheck_router


def get_api() -> FastAPI:
    api = FastAPI(title="Mirror API", version="0.1.0", docs_url="/docs")
    api.include_router(api_router)
    api.include_router(healthcheck_router)
    return api
