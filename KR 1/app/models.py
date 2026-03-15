from pydantic import BaseModel, Field, field_validator
import re

class Author(BaseModel):
    name: str
    id: int
    age: int

class BlogPost(BaseModel):
    author_name: str = Field(..., min_length=2, max_length=50)
    content: str = Field(..., min_length=10, max_length=500)

    @field_validator('content')
    @classmethod
    def check_forbidden_words(cls, v: str) -> str:
        forbidden_words = ['кринг', 'рофл', 'вайб']
        v_lower = v.lower()
        for word in forbidden_words:
            if re.search(rf'\b{word}\b', v_lower):
                raise ValueError('Пост содержит недопустимые слова (кринг, рофл, вайб)')
        return v