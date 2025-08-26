from fastapi import FastAPI
from services.query.query_service import QueryService
from src.abstraction.models.MessageDTO import MessageDTO

app = FastAPI()
@app.get("/ping")
def ping():
    return "pong"

@app.post("/query")
async def query(data: MessageDTO):
    q = QueryService()
    rs = await q.run(data.message)
    return {"result": rs}