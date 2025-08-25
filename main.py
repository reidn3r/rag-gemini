from fastapi import FastAPI
from src.abstraction.models import MessageDTO

app = FastAPI()
@app.get("/ping")
def ping():
    return "pong"

@app.post("/query")
def query(data: MessageDTO):
    return {"data": "wip"}