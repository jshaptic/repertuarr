from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class IntentResponse(BaseModel):
    intent: Literal['ADD_MEDIA', 'RECOMMEND', 'INQUIRY'] = Field(description="The user's intent")
    media_type: Literal['movie', 'series'] = Field(default='movie', description="The type of media (movie or series/show)")
    title: Optional[str] = Field(default=None, description="Title of the media to add (for ADD_MEDIA)")
    query: Optional[str] = Field(default=None, description="Search query or user's question (for RECOMMEND and INQUIRY)")

class RecommendationItem(BaseModel):
    title: str = Field(description="Title of the movie/show")
    year: int = Field(description="Release year")
    overview: str = Field(description="Short overview/synopsis")

class RecommendationResponse(BaseModel):
    items: List[RecommendationItem] = Field(description="List of recommended items")

class InquiryResponse(BaseModel):
    reply_text: str = Field(description="The conversational text reply sent to the user")
    items: List[RecommendationItem] = Field(default_factory=list, description="List of movies or shows mentioned in the reply, if any. Empty if none.")
