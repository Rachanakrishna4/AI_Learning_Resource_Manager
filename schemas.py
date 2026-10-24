
from pydantic import BaseModel, Field, HttpUrl
from pydantic import Field


class ResourceCreate(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    topic: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=5, max_length=500)
    url: HttpUrl

class SearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=10)

