import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from services.query.query_service import QueryService
from src.abstraction.models.MessageDTO import MessageDTO
from src.config.get_service import get_query_service

query_router = APIRouter()

@query_router.post("/query")
async def query(
  data: MessageDTO,
  queryService: QueryService = Depends(get_query_service)
  ):
  response = await queryService.generate_response(data.message)
  return JSONResponse({"response": response}, 200)

@query_router.post("/query/stream")
async def stream(
  data: MessageDTO,
  queryService: QueryService = Depends(get_query_service)
  ):
  async def stream_response():
    async for token in queryService.stream_response(data.message):
      yield f"data: {json.dumps({'token': token, 'type': 'token'})}\n\n"
    yield f"data: {json.dumps({'end': True})}\n\n"

  return StreamingResponse(
    stream_response(), 
    200,
    media_type="text/event-stream",
  )