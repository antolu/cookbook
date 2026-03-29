from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, computed_field


class RecipeBase(BaseModel):
    """Base recipe fields."""

    name: str = Field(..., min_length=1, max_length=200, description="Recipe name")
    description: str | None = Field(None, description="Recipe description")
    servings: str | None = Field(
        None, max_length=100, description="Serving information"
    )

    # Timing
    prep_time: int | None = Field(None, ge=0, description="Preparation time in minutes")
    cook_time: int | None = Field(None, ge=0, description="Cooking time in minutes")
    temperature: int | None = Field(None, ge=0, description="Cooking temperature")

    # Content
    content: str | None = Field(None, description="Full recipe content in Markdown")

    # Metadata
    difficulty: str | None = Field(None, description="Difficulty level")
    cuisine: str | None = Field(None, description="Cuisine type")
    category: str | None = Field(None, description="Recipe category")
    tags: list[str] | None = Field(default_factory=list, description="Recipe tags")

    # Media
    image_url: str | None = Field(None, description="Recipe image URL")

    # Additional content
    notes: list[str] | None = Field(default_factory=list, description="Recipe notes")
    tips: list[str] | None = Field(default_factory=list, description="Recipe tips")

    # Visibility
    is_public: bool = Field(True, description="Whether recipe is publicly visible")
    is_featured: bool = Field(False, description="Whether recipe is featured")


class RecipeCreate(RecipeBase):
    """Schema for creating a recipe."""

    language: str | None = Field("en", description="Recipe language")


class RecipeUpdate(BaseModel):
    """Schema for updating a recipe."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    servings: str | None = None
    prep_time: int | None = Field(None, ge=0)
    cook_time: int | None = Field(None, ge=0)
    temperature: int | None = Field(None, ge=0)
    content: str | None = None
    difficulty: str | None = None
    cuisine: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    image_url: str | None = None
    notes: list[str] | None = None
    tips: list[str] | None = None
    is_public: bool | None = None
    is_featured: bool | None = None


class RecipeResponse(RecipeBase):
    """Schema for recipe responses."""

    id: UUID
    slug: str
    language: str
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None

    @computed_field
    @property
    def total_time(self) -> int | None:
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
    description: str | None = None
    servings: str | None = None
    total_time: int | None = None
    difficulty: str | None = None
    cuisine: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    image_url: str | None = None
    is_featured: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecipeSearchParams(BaseModel):
    """Schema for recipe search parameters."""

    q: str | None = Field(None, description="Search query")
    category: str | None = Field(None, description="Filter by category")
    cuisine: str | None = Field(None, description="Filter by cuisine")
    difficulty: str | None = Field(None, description="Filter by difficulty")
    tags: list[str] | None = Field(None, description="Filter by tags")
    max_prep_time: int | None = Field(None, ge=0, description="Maximum prep time")
    max_cook_time: int | None = Field(None, ge=0, description="Maximum cook time")
    max_total_time: int | None = Field(None, ge=0, description="Maximum total time")
    is_featured: bool | None = Field(None, description="Filter featured recipes")
    limit: int = Field(20, ge=1, le=100, description="Number of results")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class RecipeSearchResponse(BaseModel):
    """Schema for recipe search responses."""

    recipes: list[RecipeListItem]
    total: int
    limit: int
    offset: int

    @computed_field
    @property
    def has_more(self) -> bool:
        """Check if there are more results."""
        return self.offset + self.limit < self.total
