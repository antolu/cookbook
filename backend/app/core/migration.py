from __future__ import annotations

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipe import Recipe
from app.core.markdown import MarkdownRecipeParser
from app.schemas.recipe import RecipeCreate

logger = logging.getLogger(__name__)


class DjangoToSQLAlchemyMigrator:
    """Migrate recipes from Django JSON format to SQLAlchemy with Markdown content."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def migrate_recipe_from_django_data(self, django_data: Dict[str, Any]) -> Recipe:
        """Migrate a single recipe from Django format to new SQLAlchemy format."""

        # Parse the Django recipe data
        recipe_data = self._parse_django_recipe(django_data)

        # Generate Markdown content from structured data
        markdown_content = MarkdownRecipeParser.generate_markdown(recipe_data)

        # Create new recipe record
        new_recipe = Recipe(
            name=recipe_data['name'],
            slug=recipe_data.get('slug', self._generate_slug(recipe_data['name'])),
            language=recipe_data.get('language', 'en'),
            description=recipe_data.get('description'),
            servings=recipe_data.get('servings'),
            prep_time=self._parse_duration(recipe_data.get('cooking_time')),
            cook_time=None,  # Separate prep/cook not available in old format
            temperature=recipe_data.get('temperature', 0) if recipe_data.get('temperature') else None,
            content=markdown_content,
            ingredients_json=recipe_data.get('ingredients'),  # Keep for transition
            instructions_json=recipe_data.get('instructions'),  # Keep for transition
            changelog=recipe_data.get('changelog'),
            notes=recipe_data.get('notes', []),
            tips=recipe_data.get('tips', []),
            difficulty=self._infer_difficulty(recipe_data),
            cuisine=None,  # Not available in old format
            category=None,  # Not available in old format
            tags=[],  # Not available in old format
            image_url=None,  # Not available in old format
            is_public=True,  # Default to public
            is_featured=False,  # Default to not featured
            created_at=recipe_data.get('pub_date', datetime.utcnow()),
            updated_at=recipe_data.get('last_changed', datetime.utcnow()),
            published_at=recipe_data.get('pub_date'),
        )

        # Add and commit
        self.db.add(new_recipe)
        await self.db.commit()
        await self.db.refresh(new_recipe)

        logger.info(f"Migrated recipe: {new_recipe.name} (ID: {new_recipe.id})")
        return new_recipe

    def _parse_django_recipe(self, django_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Django recipe data and clean it up."""

        # Parse JSON fields if they're strings
        ingredients = django_data.get('ingredients')
        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except json.JSONDecodeError:
                ingredients = []

        instructions = django_data.get('instructions')
        if isinstance(instructions, str):
            try:
                instructions = json.loads(instructions)
            except json.JSONDecodeError:
                instructions = []

        changelog = django_data.get('changelog')
        if isinstance(changelog, str):
            try:
                changelog = json.loads(changelog)
            except json.JSONDecodeError:
                changelog = []

        # Parse dates
        pub_date = django_data.get('pub_date')
        if isinstance(pub_date, str):
            try:
                pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            except ValueError:
                pub_date = datetime.utcnow()

        last_changed = django_data.get('last_changed')
        if isinstance(last_changed, str):
            try:
                last_changed = datetime.fromisoformat(last_changed.replace('Z', '+00:00'))
            except ValueError:
                last_changed = datetime.utcnow()

        return {
            'name': django_data.get('name', 'Untitled Recipe'),
            'slug': django_data.get('slug'),
            'language': django_data.get('language', 'en'),
            'description': django_data.get('description'),
            'servings': django_data.get('makes'),
            'cooking_time': django_data.get('cooking_time'),
            'temperature': django_data.get('temperature'),
            'ingredients': ingredients,
            'instructions': instructions,
            'changelog': changelog,
            'notes': django_data.get('notes', []),
            'tips': django_data.get('tips', []),
            'pub_date': pub_date,
            'last_changed': last_changed,
        }

    def _parse_duration(self, duration_str: Optional[str]) -> Optional[int]:
        """Parse Django DurationField to minutes."""
        if not duration_str:
            return None

        if isinstance(duration_str, int):
            return duration_str

        # Handle various duration formats
        duration_str = str(duration_str).strip()

        # Format: "HH:MM:SS" or "H:MM:SS"
        if ':' in duration_str:
            parts = duration_str.split(':')
            if len(parts) >= 2:
                try:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    return hours * 60 + minutes
                except ValueError:
                    pass

        # Format: "X hours Y minutes" or similar
        import re
        time_match = re.search(r'(\d+)\s*(?:hours?|hrs?|h)', duration_str, re.IGNORECASE)
        minutes_match = re.search(r'(\d+)\s*(?:minutes?|mins?|m)', duration_str, re.IGNORECASE)

        total_minutes = 0
        if time_match:
            total_minutes += int(time_match.group(1)) * 60
        if minutes_match:
            total_minutes += int(minutes_match.group(1))

        return total_minutes if total_minutes > 0 else None

    def _infer_difficulty(self, recipe_data: Dict[str, Any]) -> Optional[str]:
        """Infer difficulty from recipe data."""
        # Simple heuristics based on cooking time and instruction count
        cooking_time = self._parse_duration(recipe_data.get('cooking_time'))
        instructions = recipe_data.get('instructions', [])

        instruction_count = 0
        if isinstance(instructions, list):
            for section in instructions:
                if isinstance(section, dict) and 'list' in section:
                    instruction_count += len(section['list'])
                else:
                    instruction_count += 1

        # Simple difficulty inference
        if cooking_time and cooking_time > 180:  # More than 3 hours
            return 'hard'
        elif instruction_count > 10 or (cooking_time and cooking_time > 60):
            return 'medium'
        else:
            return 'easy'

    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug from recipe name."""
        import re
        slug = name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')


class QMLToMarkdownMigrator:
    """Migrate QML recipe files to Markdown format."""

    @staticmethod
    def migrate_qml_file(qml_file_path: str, output_dir: str) -> str:
        """Migrate a QML file to Markdown format."""
        import os
        from app.core.markdown import LegacyQMLConverter

        # Read QML file
        with open(qml_file_path, 'r', encoding='utf-8') as f:
            qml_content = f.read()

        # Convert to Markdown
        markdown_content = LegacyQMLConverter.convert_qml_to_markdown(qml_content)

        # Generate output filename
        base_name = os.path.splitext(os.path.basename(qml_file_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.md")

        # Write Markdown file
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Converted QML file {qml_file_path} to {output_path}")
        return output_path

    @staticmethod
    def batch_migrate_qml_directory(qml_dir: str, output_dir: str) -> List[str]:
        """Migrate all QML files in a directory to Markdown format."""
        import os

        migrated_files = []

        for filename in os.listdir(qml_dir):
            if filename.lower().endswith(('.qml', '.rcp')):
                qml_path = os.path.join(qml_dir, filename)
                try:
                    output_path = QMLToMarkdownMigrator.migrate_qml_file(qml_path, output_dir)
                    migrated_files.append(output_path)
                except Exception as e:
                    logger.error(f"Failed to migrate {qml_path}: {e}")

        logger.info(f"Migrated {len(migrated_files)} QML files to Markdown")
        return migrated_files


async def run_full_migration(db_session: AsyncSession, django_recipes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run full migration from Django recipes to new format."""

    migrator = DjangoToSQLAlchemyMigrator(db_session)
    migration_results = {
        'successful': 0,
        'failed': 0,
        'errors': []
    }

    for django_recipe in django_recipes:
        try:
            await migrator.migrate_recipe_from_django_data(django_recipe)
            migration_results['successful'] += 1
        except Exception as e:
            migration_results['failed'] += 1
            migration_results['errors'].append({
                'recipe': django_recipe.get('name', 'Unknown'),
                'error': str(e)
            })
            logger.error(f"Failed to migrate recipe {django_recipe.get('name', 'Unknown')}: {e}")

    logger.info(f"Migration completed: {migration_results['successful']} successful, {migration_results['failed']} failed")
    return migration_results