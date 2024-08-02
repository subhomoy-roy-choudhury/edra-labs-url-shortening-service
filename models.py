from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
from utils import random_alias_string
from collections import deque

class ShortenedURL(BaseModel):
    alias: str
    long_url: str
    ttl_seconds: int
    access_count: int = Field(default=0)
    access_times: List[datetime] = Field(default=deque(maxlen=10))
    created_at: datetime

class CreateShortenURLRequest(BaseModel):
    long_url: str
    custom_alias: str =  Field(default=random_alias_string(5))
    ttl_seconds: int = Field(default=120)

class CreateShortenURLResponse(BaseModel):
    short_url: str

class URLAnalyticsResponse(BaseModel):
    alias: str
    long_url: str
    access_count: int
    access_times: List[datetime]

class UpdateShortenURLRequest(BaseModel):
    custom_alias: str
    ttl_seconds: int