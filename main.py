from fastapi import FastAPI
from src.controllers.health_controller import health_router
from src.controllers.query_controller import query_router

app = FastAPI()
app.include_router(health_router)
app.include_router(query_router)