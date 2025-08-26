from pydantic import BaseModel, Field
from pydantic.tools import parse_obj_as
import json
from typing import List

class RerankingDTO(BaseModel):
    document_index: int = Field(..., ge=1)  
    score: float = Field(..., ge=0, le=10)  
    reason: str

def map_to_reranking_list(json_string: str) -> List[RerankingDTO]:
    clean_json = json_string.strip().replace('```json', '').replace('```', '').strip()
    data = json.loads(clean_json)
    return parse_obj_as(List[RerankingDTO], data)  
