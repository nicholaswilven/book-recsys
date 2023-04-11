from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel

class Books(BaseModel):
    isbn : str
    title : str
    author : str
    year : int
    pub : str
    img_url : str

class Reviews(BaseModel):
    user_id: UUID
    isbn : str
    rating : int

class User(BaseModel):
    user_id: UUID 
    age: Optional[int]
    location: str
    

