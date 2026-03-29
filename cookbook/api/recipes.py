from __future__ import annotations

import contextlib
import typing
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook.core.markdown import MarkdownRecipeParser, validate_markdown_recipe
from cookbook.crud.recipe import (
    create_recipe,
    delete_recipe,
    get_featured_recipes,
    get_recent_recipes,
    get_recipe,
    get_recipe_by_slug,
    get_recipe_count,
    get_recipes,
    get_recipes_by_category,
    get_unique_categories,
    get_unique_cuisines,
    get_unique_tags,
    search_recipes,
    update_recipe,
)
from cookbook.database import get_session
from cookbook.dependencies import (
    get_current_admin_user,
    get_current_user,
)
from cookbook.models.recipe import Recipe
from cookbook.models.user import User
from cookbook.schemas.recipe import (
    RecipeCreate,
    RecipeListItem,
    RecipeResponse,
    RecipeSearchParams,
    RecipeSearchResponse,
    RecipeUpdate,
)
from cookbook.schemas.recipe_schema import (
    RECIPE_FRONTMATTER_SCHEMA,
    get_enum_values,
    get_field_descriptions,
)

router = APIRouter()


def convert_to_response(db_recipe: Recipe) -> RecipeResponse:
    """Convert a database Recipe model to response schema."""
    return RecipeResponse.model_validate(db_recipe, from_attributes=True)  # type: ignore[no-any-return]


def convert_to_list_item(db_recipe: Recipe) -> RecipeListItem:
    """Convert a database Recipe model to list item schema."""
    return RecipeListItem.model_validate(db_recipe, from_attributes=True)  # type: ignore[no-any-return]


@router.get("/", response_model=list[RecipeListItem])
async def list_recipes(
    db: Annotated[AsyncSession, Depends(get_session)],
    *,
    skip: Annotated[int, Query(ge=0, description="Offset for pagination")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of results")] = 20,
    featured_only: Annotated[
        bool, Query(description="Show only featured recipes")
    ] = False,
) -> list[RecipeListItem]:
    """List recipes with pagination."""
    recipes = await get_recipes(
        db, skip=skip, limit=limit, public_only=True, featured_only=featured_only
    )
    return [convert_to_list_item(recipe) for recipe in recipes]


@router.get("/search", response_model=RecipeSearchResponse)
async def search_recipes_endpoint(
    db: Annotated[AsyncSession, Depends(get_session)],
    search_params: Annotated[RecipeSearchParams, Depends()],
) -> RecipeSearchResponse:
    """Search recipes with filters."""

    recipes, total = await search_recipes(db, search_params)

    return RecipeSearchResponse(
        recipes=[convert_to_list_item(recipe) for recipe in recipes],
        total=total,
        limit=search_params.limit,
        offset=search_params.offset,
    )


@router.get("/featured", response_model=list[RecipeListItem])
async def get_featured_recipes_endpoint(
    db: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[
        int, Query(ge=1, le=20, description="Number of featured recipes")
    ] = 5,
) -> list[RecipeListItem]:
    """Get featured recipes."""
    recipes = await get_featured_recipes(db, limit=limit)
    return [convert_to_list_item(recipe) for recipe in recipes]


@router.get("/recent", response_model=list[RecipeListItem])
async def get_recent_recipes_endpoint(
    db: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[
        int, Query(ge=1, le=20, description="Number of recent recipes")
    ] = 10,
) -> list[RecipeListItem]:
    """Get recently created recipes."""
    recipes = await get_recent_recipes(db, limit=limit, public_only=True)
    return [convert_to_list_item(recipe) for recipe in recipes]


@router.get("/categories", response_model=list[str])
async def get_categories(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> list[str]:
    """Get all unique recipe categories."""
    return await get_unique_categories(db)


@router.get("/cuisines", response_model=list[str])
async def get_cuisines(db: Annotated[AsyncSession, Depends(get_session)]) -> list[str]:
    """Get all unique cuisines."""
    return await get_unique_cuisines(db)


@router.get("/tags", response_model=list[str])
async def get_tags(db: Annotated[AsyncSession, Depends(get_session)]) -> list[str]:
    """Get all unique tags."""
    return await get_unique_tags(db)


@router.get("/category/{category}", response_model=list[RecipeListItem])
async def get_recipes_by_category_endpoint(
    category: str,
    db: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100, description="Number of results")] = 20,
) -> list[RecipeListItem]:
    """Get recipes by category."""
    recipes = await get_recipes_by_category(db, category, limit=limit, public_only=True)
    return [convert_to_list_item(recipe) for recipe in recipes]


@router.get("/{recipe_identifier}", response_model=RecipeResponse)
async def get_recipe_detail(
    recipe_identifier: str, db: Annotated[AsyncSession, Depends(get_session)]
) -> RecipeResponse:
    """Get recipe by ID or slug."""
    recipe = None

    # Try to parse as UUID first
    try:
        recipe_id = UUID(recipe_identifier)
        recipe = await get_recipe(db, recipe_id)
    except ValueError:
        # If not a valid UUID, treat as slug
        recipe = await get_recipe_by_slug(db, slug=recipe_identifier)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return convert_to_response(recipe)


@router.post("/", response_model=RecipeResponse)
async def create_recipe_endpoint(
    recipe: RecipeCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RecipeResponse:
    """
    Create a new recipe.
    Requires authentication via shared secret token.
    """
    try:
        recipe_data = recipe.model_dump()
        recipe_data["author_id"] = current_user.id

        db_recipe = await create_recipe(db, RecipeCreate(**recipe_data))
        return convert_to_response(db_recipe)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating recipe: {e!s}"
        ) from e


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe_endpoint(
    recipe_id: UUID,
    recipe_update: RecipeUpdate,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RecipeResponse:
    """
    Update recipe. Only author or admin can update.
    """
    # Only recipe author or admin can update
    # Get existing recipe
    existing_recipe = await get_recipe(db, recipe_id)
    if not existing_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    is_author = existing_recipe.author_id == current_user.id
    is_admin = getattr(current_user, "is_admin", False)
    if not (is_author or is_admin):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own recipes",
        )

    recipe = await update_recipe(db, recipe_id, recipe_update)
    assert recipe is not None
    return convert_to_response(recipe)


@router.delete("/{recipe_id}")
async def delete_recipe_endpoint(
    recipe_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """
    Delete recipe. Only author or admin can delete.
    """
    # Get existing recipe
    existing_recipe = await get_recipe(db, recipe_id)
    if not existing_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    is_author = existing_recipe.author_id == current_user.id
    is_admin = getattr(current_user, "is_admin", False)
    if not (is_author or is_admin):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own recipes",
        )

    success = await delete_recipe(db, recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {"message": "Recipe deleted successfully"}


@router.get("/stats/summary")
async def get_recipe_stats(
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
) -> dict[str, int]:
    """Get recipe statistics (admin only)."""
    total_recipes = await get_recipe_count(db)
    public_recipes = await get_recipe_count(db, public_only=True)

    return {
        "total_recipes": total_recipes,
        "public_recipes": public_recipes,
        "private_recipes": total_recipes - public_recipes,
    }


@router.post("/validate")
async def validate_recipe_markdown(
    markdown_content: str = Body(..., media_type="text/plain"),
) -> dict[str, typing.Any]:
    """Validate markdown recipe content and return errors/warnings."""
    errors = validate_markdown_recipe(markdown_content)

    # Try to parse to get field info
    parsed_data = None
    with contextlib.suppress(Exception):
        parsed_data = MarkdownRecipeParser.parse_recipe(markdown_content)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "parsed_fields": {
            "name": parsed_data.name if parsed_data else None,
            "difficulty": parsed_data.difficulty if parsed_data else None,
            "cuisine": parsed_data.cuisine if parsed_data else None,
            "category": parsed_data.category if parsed_data else None,
        }
        if parsed_data
        else None,
    }


@router.get("/editor/schema")
async def get_recipe_schema() -> dict[str, typing.Any]:
    """Get JSON Schema for recipe frontmatter validation."""
    return {
        "schema": RECIPE_FRONTMATTER_SCHEMA,
        "field_descriptions": get_field_descriptions(),
    }


@router.get("/editor/autocomplete")
async def get_autocomplete_data(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, list[str]]:
    """Get autocomplete data for recipe editor."""
    cuisines = await get_unique_cuisines(db)
    categories = await get_unique_categories(db)
    tags = await get_unique_tags(db)

    return {
        "cuisines": cuisines,
        "categories": categories,
        "tags": tags,
        "difficulty": typing.cast(list[str], get_enum_values("difficulty")),
    }


@router.post("/upload")
async def upload_recipe_file(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
) -> dict[str, str]:
    """Upload a recipe file (admin only)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    if not file.filename.lower().endswith((".md", ".markdown")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please use .md or .markdown files",
        )

    try:
        content = await file.read()
        content_str = content.decode("utf-8")

        # Validate Markdown
        validation_errors = validate_markdown_recipe(content_str)
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid Markdown recipe: {'; '.join(validation_errors)}",
            )

        # Parse and create recipe
        recipe_data = MarkdownRecipeParser.parse_recipe(content_str)
        db_recipe = await create_recipe(db, recipe_data)

        return {
            "message": "Recipe uploaded successfully",
            "filename": file.filename,
            "recipe_id": str(db_recipe.id),
            "recipe_name": str(db_recipe.name),
            "recipe_slug": str(db_recipe.slug),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error processing file: {e!s}"
        ) from e


@router.get("/{recipe_id}/export/{export_format}")
async def export_recipe(
    recipe_id: UUID,
    export_format: str,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> Response | dict[str, typing.Any]:
    """Export recipe in various formats (markdown, json, pdf)."""
    recipe = await get_recipe(db, recipe_id)
    if not recipe or not recipe.is_public:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if export_format not in {"markdown", "json", "pdf"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Use 'markdown', 'json', or 'pdf'",
        )

    try:
        if export_format == "markdown":
            # Convert recipe to Markdown
            recipe_dict = {
                "name": recipe.name,
                "description": recipe.description,
                "servings": recipe.servings,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "total_time": (recipe.prep_time or 0) + (recipe.cook_time or 0)
                if recipe.prep_time or recipe.cook_time
                else None,
                "temperature": recipe.temperature,
                "difficulty": recipe.difficulty,
                "cuisine": recipe.cuisine,
                "category": recipe.category,
                "tags": recipe.tags or [],
                "notes": recipe.notes or [],
                "tips": recipe.tips or [],
                "created_at": recipe.created_at,
                "updated_at": recipe.updated_at,
                "content": recipe.content or "",
                "ingredients_json": recipe.ingredients_json,
                "instructions_json": recipe.instructions_json,
            }

            markdown_content = MarkdownRecipeParser.generate_markdown(recipe_dict)

            return Response(
                content=markdown_content,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f'attachment; filename="{recipe.slug}.md"'
                },
            )

        if export_format == "json":
            # Export as JSON
            recipe_data = convert_to_response(recipe)

            return Response(
                content=recipe_data.model_dump_json(indent=2),
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="{recipe.slug}.json"'
                },
            )

        # format == "pdf"
        # TODO: Implement PDF export
        return {
            "message": "PDF export not yet implemented",
            "recipe_id": str(recipe_id),
            "format": format,
            "note": "PDF export functionality will be added in a future update",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error exporting recipe: {e!s}"
        ) from e
