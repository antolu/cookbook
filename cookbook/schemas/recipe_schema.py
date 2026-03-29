import typing
from typing import Any

# JSON Schema for recipe frontmatter validation
RECIPE_FRONTMATTER_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["name"],
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200,
            "description": "Recipe name",
        },
        "description": {
            "type": "string",
            "maxLength": 500,
            "description": "Brief description of the recipe",
        },
        "servings": {
            "type": "string",
            "description": "Number of servings (e.g., '4 people', '12 cookies')",
        },
        "prep_time": {
            "type": "string",
            "pattern": "^\\d+\\s*(minutes?|mins?|hours?|hrs?|h)?(\\s+\\d+\\s*(minutes?|mins?))?$",
            "description": "Preparation time (e.g., '15 minutes', '1 hour 30 minutes')",
        },
        "cook_time": {
            "type": "string",
            "pattern": "^\\d+\\s*(minutes?|mins?|hours?|hrs?|h)?(\\s+\\d+\\s*(minutes?|mins?))?$",
            "description": "Cooking time (e.g., '30 minutes', '2 hours')",
        },
        "temperature": {
            "type": "integer",
            "minimum": 0,
            "maximum": 600,
            "description": "Cooking temperature in Fahrenheit",
        },
        "difficulty": {
            "type": "string",
            "enum": ["easy", "medium", "hard"],
            "description": "Recipe difficulty level",
        },
        "cuisine": {
            "type": "string",
            "maxLength": 100,
            "description": "Cuisine type (e.g., 'italian', 'chinese', 'french')",
        },
        "category": {
            "type": "string",
            "maxLength": 100,
            "description": "Recipe category (e.g., 'dessert', 'main', 'appetizer')",
        },
        "tags": {
            "type": "array",
            "items": {"type": "string", "maxLength": 50},
            "uniqueItems": True,
            "description": "Recipe tags for categorization",
        },
        "notes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Additional notes about the recipe",
        },
        "tips": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Cooking tips and tricks",
        },
        "public": {
            "type": "boolean",
            "default": True,
            "description": "Whether the recipe is publicly visible",
        },
        "featured": {
            "type": "boolean",
            "default": False,
            "description": "Whether the recipe is featured",
        },
        "language": {
            "type": "string",
            "default": "en",
            "pattern": "^[a-z]{2}$",
            "description": "Recipe language code (ISO 639-1)",
        },
    },
    "additionalProperties": False,
}


def get_field_descriptions() -> dict[str, str]:
    """Extract field descriptions from schema for autocomplete."""
    descriptions = {}
    for field, props in RECIPE_FRONTMATTER_SCHEMA["properties"].items():
        if "description" in props:
            descriptions[field] = props["description"]
    return descriptions


def get_enum_values(field: str) -> list[str] | None:
    """Get enum values for a field if it has any."""
    props = typing.cast(dict[str, Any], RECIPE_FRONTMATTER_SCHEMA["properties"]).get(
        field
    )
    if props and "enum" in props:
        return typing.cast(list[str], props["enum"])
    return None
