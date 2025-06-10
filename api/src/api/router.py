from enum import Enum
from fastapi import FastAPI
from fastapi.routing import APIRouter
from dataclasses import dataclass
from typing import Dict, List
from .v1 import router as customer_router

@dataclass
class RouterConfig:
    router: APIRouter
    prefix: str
    tags: List[str | Enum]

ROUTER_CONFIGS: Dict[str, RouterConfig] = {
    "customers": RouterConfig(
        router=customer_router,
        prefix="/api/v1/customers",
        tags=["customers"]
    )
}

def configure_routes(app: FastAPI) -> FastAPI:
    for domain_name, config in ROUTER_CONFIGS.items():
        print(f"Configuring router for '{domain_name}' with prefix '{config.prefix}' and tags '{config.tags}'")
        app.include_router(config.router, prefix=config.prefix, tags=config.tags)

    return app