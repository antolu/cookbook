from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.core.markdown import MarkdownRecipeParser
from cookbook.models.recipe import Recipe

logger = logging.getLogger(__name__)


class DjangoToSQLAlchemyMigrator:
    """Migrate recipes from Django JSON format to SQLAlchemy with Markdown content."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def migrate_recipe_from_django_data(
        self, django_data: dict[str, Any]
    ) -> Recipe:
        """Migrate a single recipe from Django format to new SQLAlchemy format."""

        # Parse the Django recipe data
        recipe_data = self._parse_django_recipe(django_data)

        # Generate Markdown content from structured data
        markdown_content = MarkdownRecipeParser.generate_markdown(recipe_data)

        # Create new recipe record
        new_recipe = Recipe(
            name=recipe_data["name"],
            slug=recipe_data.get("slug", self._generate_slug(recipe_data["name"])),
            language=recipe_data.get("language", "en"),
            description=recipe_data.get("description"),
            servings=recipe_data.get("servings"),
            prep_time=self._parse_duration(recipe_data.get("cooking_time")),
            cook_time=None,  # Separate prep/cook not available in old format
            temperature=recipe_data.get("temperature", 0)
            if recipe_data.get("temperature")
            else None,
            content=markdown_content,
            ingredients_json=recipe_data.get("ingredients"),  # Keep for transition
            instructions_json=recipe_data.get("instructions"),  # Keep for transition
            changelog=recipe_data.get("changelog"),
            notes=recipe_data.get("notes", []),
            tips=recipe_data.get("tips", []),
            difficulty=self._infer_difficulty(recipe_data),
            cuisine=None,  # Not available in old format
            category=None,  # Not available in old format
            tags=[],  # Not available in old format
            image_url=None,  # Not available in old format
            is_public=True,  # Default to public
            is_featured=False,  # Default to not featured
            created_at=recipe_data.get("pub_date", datetime.utcnow()),
            updated_at=recipe_data.get("last_changed", datetime.utcnow()),
            published_at=recipe_data.get("pub_date"),
        )

        # Add and commit
        self.db.add(new_recipe)
        await self.db.commit()
        await self.db.refresh(new_recipe)

        logger.info(f"Migrated recipe: {new_recipe.name} (ID: {new_recipe.id})")
        return new_recipe

    @staticmethod
    def _parse_django_recipe(django_data: dict[str, Any]) -> dict[str, Any]:
        """Parse Django recipe data and clean it up."""

        # Parse JSON fields if they're strings
        ingredients = django_data.get("ingredients")
        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except json.JSONDecodeError:
                ingredients = []

        instructions = django_data.get("instructions")
        if isinstance(instructions, str):
            try:
                instructions = json.loads(instructions)
            except json.JSONDecodeError:
                instructions = []

        changelog = django_data.get("changelog")
        if isinstance(changelog, str):
            try:
                changelog = json.loads(changelog)
            except json.JSONDecodeError:
                changelog = []

        # Parse dates
        pub_date = django_data.get("pub_date")
        if isinstance(pub_date, str):
            try:
                pub_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            except ValueError:
                pub_date = datetime.utcnow()

        last_changed = django_data.get("last_changed")
        if isinstance(last_changed, str):
            try:
                last_changed = datetime.fromisoformat(
                    last_changed.replace("Z", "+00:00")
                )
            except ValueError:
                last_changed = datetime.utcnow()

        return {
            "name": django_data.get("name", "Untitled Recipe"),
            "slug": django_data.get("slug"),
            "language": django_data.get("language", "en"),
            "description": django_data.get("description"),
            "servings": django_data.get("makes"),
            "cooking_time": django_data.get("cooking_time"),
            "temperature": django_data.get("temperature"),
            "ingredients": ingredients,
            "instructions": instructions,
            "changelog": changelog,
            "notes": django_data.get("notes", []),
            "tips": django_data.get("tips", []),
            "pub_date": pub_date,
            "last_changed": last_changed,
        }

    @staticmethod
    def _parse_duration(duration_val: Any) -> int | None:
        """Parse Django DurationField to minutes."""
        if not duration_val:
            return None

        if isinstance(duration_val, int):
            return duration_val

        # Handle various duration formats
        duration_str: str = str(duration_val).strip()

        # Format: "HH:MM:SS" or "H:MM:SS"
        if ":" in duration_str:
            parts = duration_str.split(":")
            if len(parts) >= 2:
                try:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    return hours * 60 + minutes
                except ValueError:
                    pass

        # Format: "X hours Y minutes" or similar
        time_match = re.search(
            r"(\d+)\s*(?:hours?|hrs?|h)", duration_str, re.IGNORECASE
        )
        minutes_match = re.search(
            r"(\d+)\s*(?:minutes?|mins?|m)", duration_str, re.IGNORECASE
        )

        total_minutes = 0
        if time_match:
            total_minutes += int(time_match.group(1)) * 60
        if minutes_match:
            total_minutes += int(minutes_match.group(1))

        return total_minutes if total_minutes > 0 else None

    @staticmethod
    def _map_difficulty(difficulty_code: str | int | None) -> str | None:
        if difficulty_code is None:
            return "easy"
        try:
            lookup_key = int(difficulty_code)
            mapping = {1: "easy", 2: "medium", 3: "hard"}
            return mapping.get(lookup_key, "easy")
        except (ValueError, TypeError):
            return "easy"

    def _infer_difficulty(self, recipe_data: dict[str, Any]) -> str | None:
        """Infer difficulty from recipe data."""
        # Simple heuristics based on cooking time and instruction count
        cooking_time = self._parse_duration(recipe_data.get("cooking_time"))
        instructions = recipe_data.get("instructions", [])

        instruction_count = 0
        if isinstance(instructions, list):
            for section in instructions:
                if isinstance(section, dict) and "list" in section:
                    instruction_count += len(section["list"])
                else:
                    instruction_count += 1

        # Simple difficulty inference
        if cooking_time and cooking_time > 180:  # More than 3 hours
            return "hard"
        if instruction_count > 10 or (cooking_time and cooking_time > 60):
            return "medium"
        return "easy"

    @staticmethod
    def _generate_slug(name: str) -> str:
        """Generate URL-friendly slug from recipe name."""
        slug = name.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")


async def run_full_migration(
    db_session: AsyncSession, django_recipes: list[dict[str, Any]]
) -> dict[str, Any]:
    """Run full migration from Django recipes to new format."""

    migrator = DjangoToSQLAlchemyMigrator(db_session)
    migration_results: dict[str, Any] = {"successful": 0, "failed": 0, "errors": []}

    for django_recipe in django_recipes:
        try:
            await migrator.migrate_recipe_from_django_data(django_recipe)
            migration_results["successful"] += 1
        except Exception as e:
            migration_results["failed"] += 1
            migration_results["errors"].append({
                "recipe": django_recipe.get("name", "Unknown"),
                "error": str(e),
            })
            logger.error(
                f"Failed to migrate recipe {django_recipe.get('name', 'Unknown')}: {e}"
            )

    logger.info(
        f"Migration completed: {migration_results['successful']} successful, {migration_results['failed']} failed"
    )
    return migration_results
