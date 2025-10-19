from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, computed_field


class RecipeBase(BaseModel):
    """Base recipe fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Recipe name")
    description: Optional[str] = Field(None, description="Recipe description")
    servings: Optional[str] = Field(None, max_length=100, description="Serving information")

    # Timing
    prep_time: Optional[int] = Field(None, ge=0, description="Preparation time in minutes")
    cook_time: Optional[int] = Field(None, ge=0, description="Cooking time in minutes")
    temperature: Optional[int] = Field(None, ge=0, description="Cooking temperature")

    # Content
    content: Optional[str] = Field(None, description="Full recipe content in Markdown")

    # Metadata
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    cuisine: Optional[str] = Field(None, description="Cuisine type")
    category: Optional[str] = Field(None, description="Recipe category")
    tags: Optional[List[str]] = Field(default_factory=list, description="Recipe tags")

    # Media
    image_url: Optional[str] = Field(None, description="Recipe image URL")

    # Additional content
    notes: Optional[List[str]] = Field(default_factory=list, description="Recipe notes")
    tips: Optional[List[str]] = Field(default_factory=list, description="Recipe tips")

    # Visibility
    is_public: bool = Field(True, description="Whether recipe is publicly visible")
    is_featured: bool = Field(False, description="Whether recipe is featured")


class RecipeCreate(RecipeBase):
    """Schema for creating a recipe."""
    language: Optional[str] = Field("en", description="Recipe language")


class RecipeUpdate(BaseModel):
    """Schema for updating a recipe."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    servings: Optional[str] = None
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    temperature: Optional[int] = Field(None, ge=0)
    content: Optional[str] = None
    difficulty: Optional[str] = None
    cuisine: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    notes: Optional[List[str]] = None
    tips: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None


class RecipeResponse(RecipeBase):
    """Schema for recipe responses."""
    id: UUID
    slug: str
    language: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    @computed_field
    @property
    def total_time(self) -> Optional[int]:
        """Compute total time from prep and cook times."""
        if self.prep_time is not None and self.cook_time is not None:
            return self.prep_time + self.cook_time
        return None

    model_config = {"from_attributes": True}


class RecipeListItem(BaseModel):
    """Simplified schema for recipe lists."""
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    servings: Optional[str] = None
    total_time: Optional[int] = None
    difficulty: Optional[str] = None
    cuisine: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    is_featured: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecipeSearchParams(BaseModel):
    """Schema for recipe search parameters."""
    q: Optional[str] = Field(None, description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    cuisine: Optional[str] = Field(None, description="Filter by cuisine")
    difficulty: Optional[str] = Field(None, description="Filter by difficulty")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    max_prep_time: Optional[int] = Field(None, ge=0, description="Maximum prep time")
    max_cook_time: Optional[int] = Field(None, ge=0, description="Maximum cook time")
    max_total_time: Optional[int] = Field(None, ge=0, description="Maximum total time")
    is_featured: Optional[bool] = Field(None, description="Filter featured recipes")
    limit: int = Field(20, ge=1, le=100, description="Number of results")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class RecipeSearchResponse(BaseModel):
    """Schema for recipe search responses."""
    recipes: List[RecipeListItem]
    total: int
    limit: int
    offset: int

    @computed_field
    @property
    def has_more(self) -> bool:
        """Check if there are more results."""
        return self.offset + self.limit < self.total