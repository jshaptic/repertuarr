from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class IntentResponse(BaseModel):
    intent: Literal['ADD_MEDIA', 'RECOMMEND', 'INQUIRY'] = Field(description="The user's intent")
    media_type: Literal['movie', 'series'] = Field(default='movie', description="The type of media (movie or series/show)")
    title: Optional[str] = Field(default=None, description="Title of the media to add (for ADD_MEDIA)")
    query: Optional[str] = Field(default=None, description="Search query or user's question (for RECOMMEND and INQUIRY)")
    image_description: Optional[str] = Field(
        default=None,
        description="Brief description of what is visible in the attached image (poster, scene, actor, etc.)",
    )

class RecommendationFilters(BaseModel):
    media_type: Literal['movie', 'tv'] = Field(default='movie', description="Media type the user constrained the request to; default to movie when unclear")
    genres: List[str] = Field(default_factory=list, description="Genre names picked EXACTLY from the provided genre list; empty if no genre constraint")
    people: List[str] = Field(default_factory=list, description="Full names of actors or directors the user mentioned; empty if none")
    year_from: Optional[int] = Field(default=None, description="Earliest release year, e.g. 1990 for '90s movies'; null if unconstrained")
    year_to: Optional[int] = Field(default=None, description="Latest release year, e.g. 1999 for '90s movies'; null if unconstrained")
    min_rating: Optional[float] = Field(default=None, description="Minimum TMDB vote average 0-10 when the user asked for 'good'/'highly rated' content; null otherwise")
    original_language: Optional[str] = Field(default=None, description="ISO 639-1 code of the original language when the user asked for e.g. French films; null otherwise")

class RecommendationPlan(BaseModel):
    has_filters: bool = Field(description="True only if the user expressed concrete constraints (genre, person, era, rating, language). False for generic requests like 'recommend something good'")
    filters: Optional[RecommendationFilters] = Field(default=None, description="The extracted constraints; null when has_filters is false")
    pool_label: str = Field(description="Short human-readable label for the request in English, e.g. 'Anne Hathaway comedies from the 90s'")

class RecommendationItem(BaseModel):
    title: str = Field(description="Title of the movie/show in the user's language")
    original_title: str = Field(description="Original title of the movie/show in its original language (usually English), used for database lookups")
    year: int = Field(description="Release year")
    overview: str = Field(description="Short overview/synopsis in the user's language")
    tmdb_id: Optional[int] = Field(default=None, description="TMDB ID of the movie/show. Omit if unknown.")

class RecommendationResponse(BaseModel):
    items: List[RecommendationItem] = Field(description="List of recommended items")

class InquiryResponse(BaseModel):
    reply_text: str = Field(description="The conversational text reply sent to the user")
    items: List[RecommendationItem] = Field(default_factory=list, description="List of movies or shows mentioned in the reply, if any. Empty if none.")
