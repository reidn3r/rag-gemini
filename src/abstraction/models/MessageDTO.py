from pydantic import BaseModel, Field

class MessageDTO(BaseModel):
  message: str = Field(..., min_length=1, description="Mensagem do usuário")