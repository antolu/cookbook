from __future__ import annotations

# ruff: noqa: PLR0912, PLR0915, PLR1702
import re
from datetime import datetime
from typing import Any

import frontmatter
import yaml

from cookbook.schemas.recipe import RecipeCreate


class MarkdownRecipeParser:
    """Parser for Markdown recipe files with YAML frontmatter."""

    @staticmethod
    def parse_recipe(markdown_content: str) -> RecipeCreate:
        """Parse a Markdown recipe file into a RecipeCreate object."""
        # Parse frontmatter and content
        post = frontmatter.loads(markdown_content)
        metadata = post.metadata
        content = post.content

        # Extract basic information
        name = metadata.get("name", "Untitled Recipe")
        description = metadata.get("description")
        servings = metadata.get("servings") or metadata.get("makes")

        # Parse timing and difficulty
        prep_time = MarkdownRecipeParser.parse_duration(metadata.get("prep_time"))
        cook_time = MarkdownRecipeParser.parse_duration(metadata.get("cook_time"))
        difficulty = metadata.get("difficulty")

        # Parse cuisine and category
        cuisine = metadata.get("cuisine")
        category = metadata.get("category")

        # Handle all lists and other metadata in a specialized helper to reduce local variables
        extra_data = MarkdownRecipeParser._extract_extra_metadata(metadata)

        return RecipeCreate(
            name=name,
            description=description,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
            temperature=metadata.get("temperature"),
            image_url=metadata.get("image"),
            content=content,
            difficulty=difficulty,
            cuisine=cuisine,
            category=category,
            tags=extra_data["tags"],
            notes=extra_data["notes"],
            tips=extra_data["tips"],
            is_public=extra_data["is_public"],
            is_featured=extra_data["is_featured"],
            language=extra_data["language"],
        )

    @staticmethod
    def _extract_extra_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        """Extra helper to extract list-based and visibility metadata."""
        return {
            "tags": MarkdownRecipeParser._parse_list(metadata.get("tags", [])),
            "notes": MarkdownRecipeParser._parse_list(metadata.get("notes", [])),
            "tips": MarkdownRecipeParser._parse_list(metadata.get("tips", [])),
            "is_public": metadata.get("public", True),
            "is_featured": metadata.get("featured", False),
            "language": metadata.get("language", "en") or "en",
        }

    @staticmethod
    def _parse_list(value: Any) -> list[str]:
        """Parse a value that could be a string or a list into a list of strings."""
        if not value:
            return []
        if isinstance(value, str):
            if "," in value:
                return [item.strip() for item in value.split(",")]
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]

    @staticmethod
    def parse_duration(time_val: Any) -> int | None:
        """Parse time string or number to minutes."""
        if not time_val:
            return None

        if isinstance(time_val, int):
            return time_val

        time_str: str = str(time_val).lower().strip()

        # Extract number and unit
        match = re.match(r"(\d+(?:\.\d+)?)\s*(minutes?|mins?|hours?|hrs?|h)?", time_str)
        if not match:
            return None

        value = float(match.group(1))
        unit = match.group(2) or "minutes"

        # Convert to minutes
        if unit in {"hours", "hour", "hrs", "hr", "h"}:
            return int(value * 60)
        return int(value)

    @staticmethod
    def generate_markdown(recipe_data: dict[str, Any]) -> str:
        """Generate Markdown content from recipe data."""
        # Prepare frontmatter
        frontmatter_data = {
            "name": recipe_data.get("name"),
            "description": recipe_data.get("description"),
            "servings": recipe_data.get("servings"),
            "prep_time": MarkdownRecipeParser._format_time(
                recipe_data.get("prep_time")
            ),
            "cook_time": MarkdownRecipeParser._format_time(
                recipe_data.get("cook_time")
            ),
            "total_time": MarkdownRecipeParser._format_time(
                recipe_data.get("total_time")
            ),
            "temperature": recipe_data.get("temperature"),
            "difficulty": recipe_data.get("difficulty"),
            "cuisine": recipe_data.get("cuisine"),
            "category": recipe_data.get("category"),
            "tags": recipe_data.get("tags", []),
            "notes": recipe_data.get("notes", []),
            "tips": recipe_data.get("tips", []),
            "public": recipe_data.get("is_public", True),
            "featured": recipe_data.get("is_featured", False),
            "language": recipe_data.get("language", "en"),
            "created_at": recipe_data.get("created_at", datetime.now()).isoformat()
            if isinstance(recipe_data.get("created_at"), datetime)
            else recipe_data.get("created_at"),
            "updated_at": recipe_data.get("updated_at", datetime.now()).isoformat()
            if isinstance(recipe_data.get("updated_at"), datetime)
            else recipe_data.get("updated_at"),
        }

        # Remove None values
        frontmatter_data = {k: v for k, v in frontmatter_data.items() if v is not None}

        # Generate YAML frontmatter
        yaml_content = yaml.dump(
            frontmatter_data, default_flow_style=False, allow_unicode=True
        )

        # Get content or generate from structured data
        content = recipe_data.get("content", "")
        if not content:
            content = MarkdownRecipeParser._generate_content_from_data(recipe_data)

        # Combine frontmatter and content
        return f"---\n{yaml_content}---\n\n{content}"

    @staticmethod
    def _format_time(minutes: int | None) -> str | None:
        """Format time in minutes to human-readable string."""
        if not minutes:
            return None

        if minutes < 60:
            return f"{minutes} minutes"
        if minutes % 60 == 0:
            return f"{minutes // 60} hours"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours} hours {mins} minutes"

    @staticmethod
    def _generate_content_from_data(recipe_data: dict[str, Any]) -> str:
        """Generate Markdown content from structured recipe data."""
        content_parts = []

        # Description
        if recipe_data.get("description"):
            content_parts.append(recipe_data["description"])
            content_parts.append("")

        # Ingredients (if structured data exists)
        ingredients = recipe_data.get("ingredients_json") or recipe_data.get(
            "ingredients", []
        )
        if ingredients:
            content_parts.append("## Ingredients")
            content_parts.append("")
            if isinstance(ingredients, list):
                for ingredient in ingredients:
                    if isinstance(ingredient, dict):
                        # Handle structured ingredient format
                        if "list" in ingredient:
                            if ingredient.get("part"):
                                content_parts.append(f"### {ingredient['part']}")
                            content_parts.extend(
                                f"- {item}" for item in ingredient["list"]
                            )
                        else:
                            content_parts.append(f"- {ingredient}")
                    else:
                        content_parts.append(f"- {ingredient}")
            content_parts.append("")

        # Instructions (if structured data exists)
        instructions = recipe_data.get("instructions_json") or recipe_data.get(
            "instructions", []
        )
        if instructions:
            content_parts.append("## Instructions")
            content_parts.append("")
            if isinstance(instructions, list):
                step_num = 1
                for instruction in instructions:
                    if isinstance(instruction, dict):
                        # Handle structured instruction format
                        if "list" in instruction:
                            if instruction.get("part"):
                                content_parts.append(f"### {instruction['part']}")
                            for item in instruction["list"]:
                                content_parts.append(f"{step_num}. {item}")
                                step_num += 1
                        else:
                            content_parts.append(f"{step_num}. {instruction}")
                            step_num += 1
                    else:
                        content_parts.append(f"{step_num}. {instruction}")
                        step_num += 1
            content_parts.append("")

        # Notes
        notes = recipe_data.get("notes", [])
        if notes and any(notes):
            content_parts.append("## Notes")
            content_parts.append("")
            content_parts.extend(f"- {note}" for note in notes if note)
            content_parts.append("")

        # Tips
        tips = recipe_data.get("tips", [])
        if tips and any(tips):
            content_parts.append("## Tips")
            content_parts.append("")
            content_parts.extend(f"- {tip}" for tip in tips if tip)
            content_parts.append("")

        return "\n".join(content_parts).strip()


def validate_markdown_recipe(markdown_content: str) -> list[str]:
    """Validate a Markdown recipe and return list of errors."""
    errors = []

    try:
        post = frontmatter.loads(markdown_content)
        metadata = post.metadata

        # Check required fields
        if not metadata.get("name"):
            errors.append("Recipe name is required in frontmatter")

        # Validate time formats - use list.extend to satisfy ruff
        errors.extend([
            f"Invalid time format for {tf}"
            for tf in ["prep_time", "cook_time"]
            if tf in metadata and not MarkdownRecipeParser.parse_duration(metadata[tf])
        ])

        # Validate difficulty
        difficulty = metadata.get("difficulty")
        if difficulty and difficulty not in {"easy", "medium", "hard"}:
            errors.append("Difficulty must be 'easy', 'medium', or 'hard'")

        # Check content sections
        content = post.content.lower()
        if "ingredients" not in content and "instructions" not in content:
            errors.append("Recipe should contain ingredients and instructions sections")

    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML frontmatter: {e}")
    except Exception as e:
        errors.append(f"Error parsing recipe: {e}")

    return errors
