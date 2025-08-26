from fastapi import APIRouter

health_router = APIRouter(
  prefix='/health'
)

@health_router.get("/ping")
def check_health():
  return "pong"
