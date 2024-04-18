from pydantic import BaseModel, Field

class Document(BaseModel):

    page_content: str
    metadata: dict = Field(default_factory=dict)