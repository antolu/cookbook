from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.markdown import MarkdownRecipeParser, validate_markdown_recipe
from app.crud.recipe import (
    create_recipe,
    delete_recipe,
    get_recipe,
    get_recipe_by_slug,
    get_recipe_count,
    get_recipes,
    get_featured_recipes,
    get_recent_recipes,
    get_recipes_by_category,
    get_unique_categories,
    get_unique_cuisines,
    get_unique_tags,
    search_recipes,
    update_recipe,
)
from app.database import get_session
from app.schemas.recipe import (
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
    RecipeListItem,
    RecipeSearchParams,
    RecipeSearchResponse,
)

router = APIRouter()


def convert_to_response(db_recipe) -> RecipeResponse:
    """Convert a database Recipe model to response schema."""
    return RecipeResponse.model_validate(db_recipe)


def convert_to_list_item(db_recipe) -> RecipeListItem:
    """Convert a database Recipe model to list item schema."""
    return RecipeListItem.model_validate(db_recipe)


@router.get("/", response_model=List[RecipeListItem])
async def list_recipes(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    featured_only: bool = Query(False, description="Show only featured recipes"),
    db: AsyncSession = Depends(get_session),
):
    """List recipes with pagination."""
    recipes = await get_recipes(
        db, skip=skip, limit=limit, public_only=True, featured_only=featured_only
    )
    return [convert_to_list_item(recipe) for recipe in recipes]


@router.get("/search", response_model=RecipeSearchResponse)
async def search_recipes_endpoint(
    q: str = Query(None, description="Search query"),
    category: str = Query(None, description="Filter by category"),
    cuisine: str = Query(None, description="Filter by cuisine"),
    difficulty: str = Query(None, description="Filter by difficulty"),
    tags: List[str] = Query(None, description="Filter by tags"),
    max_prep_time: int = Query(None, ge=0, description="Maximum prep time"),
    max_cook_time: int = Query(None, ge=0, description="Maximum cook time"),
    max_total_time: int = Query(None, ge=0, description="Maximum total time"),
    is_featured: bool = Query(None, description="Filter featured recipes"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_session),
):
    """Search recipes with filters."""
    search_params = RecipeSearchParams(
        q=q,
        category=category,
        cuisine=cuisine,
        difficulty=difficulty,
        tags=tags,
        max_prep_time=max_prep_time,
        max_cook_time=max_cook_time,
        max_total_time=max_total_time,
        is_featured=is_featured,
        limit=limit,
        offset=offset,
    )

    recipes, total = await search_recipes(db, search_params)

    return RecipeSearchResponse(
        recipes=[convert_to_list_item(recipe) for recipe in recipes],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/featured", response_model=List[RecipeListItem])
async def get_featured_recipes_endpoint(
    limit: int = Query(5, ge=1, le=20, description="Number of featured recipes"),
    db: AsyncSession = Depends(get_session),
):
    """Get featured recipes."""
    recipes = await get_featured_recipes(db, limit=limit)
    return [convert_to_list_item(recipe) for recipe in recipes]


@router.get("/recent", response_model=List[RecipeListItem])
async def get_recent_recipes_endpoint(
    limit: int = Query(10, ge=1, le=20, description="Number of recent recipes"),
    db: AsyncSession = Depends(get_session),
):
    """Get recently created recipes."""
    recipes = await get_recent_recipes(db, limit=limit, public_only=True)
    return [convert_to_list_item(recipe) for recipe in recipes]


@router.get("/categories", response_model=List[str])
async def get_categories(db: AsyncSession = Depends(get_session)):
    """Get all unique recipe categories."""
    return await get_unique_categories(db)


@router.get("/cuisines", response_model=List[str])
async def get_cuisines(db: AsyncSession = Depends(get_session)):
    """Get all unique cuisines."""
    return await get_unique_cuisines(db)


@router.get("/tags", response_model=List[str])
async def get_tags(db: AsyncSession = Depends(get_session)):
    """Get all unique tags."""
    return await get_unique_tags(db)


@router.get("/category/{category}", response_model=List[RecipeListItem])
async def get_recipes_by_category_endpoint(
    category: str,
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    db: AsyncSession = Depends(get_session),
):
    """Get recipes by category."""
    recipes = await get_recipes_by_category(db, category, limit=limit, public_only=True)
    return [convert_to_list_item(recipe) for recipe in recipes]


@router.get("/{recipe_identifier}", response_model=RecipeResponse)
async def get_recipe_detail(
    recipe_identifier: str, db: AsyncSession = Depends(get_session)
):
    """Get recipe by ID or slug."""
    recipe = None

    # Try to parse as UUID first
    try:
        recipe_id = UUID(recipe_identifier)
        recipe = await get_recipe(db, recipe_id)
    except ValueError:
        # If not a valid UUID, treat as slug
        recipe = await get_recipe_by_slug(db, recipe_identifier)

    if not recipe or not recipe.is_public:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return convert_to_response(recipe)


@router.post("/", response_model=RecipeResponse)
async def create_recipe_endpoint(
    recipe: RecipeCreate,
    db: AsyncSession = Depends(get_session),
    # current_user=Depends(get_current_admin_user),  # TODO: Add auth
):
    """Create a new recipe (admin only)."""
    try:
        db_recipe = await create_recipe(db, recipe)
        return convert_to_response(db_recipe)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating recipe: {e!s}"
        ) from e


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe_endpoint(
    recipe_id: UUID,
    recipe_update: RecipeUpdate,
    db: AsyncSession = Depends(get_session),
    # current_user=Depends(get_current_admin_user),  # TODO: Add auth
):
    """Update recipe (admin only)."""
    recipe = await update_recipe(db, recipe_id, recipe_update)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return convert_to_response(recipe)


@router.delete("/{recipe_id}")
async def delete_recipe_endpoint(
    recipe_id: UUID,
    db: AsyncSession = Depends(get_session),
    # current_user=Depends(get_current_admin_user),  # TODO: Add auth
):
    """Delete recipe (admin only)."""
    success = await delete_recipe(db, recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {"message": "Recipe deleted successfully"}


@router.get("/stats/summary")
async def get_recipe_stats(
    db: AsyncSession = Depends(get_session),
    # current_user=Depends(get_current_admin_user),  # TODO: Add auth
):
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
    markdown_content: str,
):
    """Validate markdown recipe content and return errors/warnings."""
    errors = validate_markdown_recipe(markdown_content)

    # Try to parse to get field info
    parsed_data = None
    try:
        parsed_data = MarkdownRecipeParser.parse_recipe(markdown_content)
    except Exception:
        pass

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "parsed_fields": {
            "name": parsed_data.name if parsed_data else None,
            "difficulty": parsed_data.difficulty if parsed_data else None,
            "cuisine": parsed_data.cuisine if parsed_data else None,
            "category": parsed_data.category if parsed_data else None,
        } if parsed_data else None
    }


@router.post("/upload")
async def upload_recipe_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    # current_user=Depends(get_current_admin_user),  # TODO: Add auth
):
    """Upload a recipe file (Markdown format)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    if not file.filename.lower().endswith(('.md', '.markdown')):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please use .md or .markdown files"
        )

    try:
        content = await file.read()
        content_str = content.decode('utf-8')

        # Validate Markdown
        validation_errors = validate_markdown_recipe(content_str)
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid Markdown recipe: {'; '.join(validation_errors)}"
            )

        # Parse and create recipe
        recipe_data = MarkdownRecipeParser.parse_recipe(content_str)
        db_recipe = await create_recipe(db, recipe_data)

        return {
            "message": "Recipe uploaded successfully",
            "filename": file.filename,
            "recipe_id": str(db_recipe.id),
            "recipe_name": db_recipe.name,
            "recipe_slug": db_recipe.slug
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error processing file: {e!s}"
        ) from e


@router.get("/{recipe_id}/export/{format}")
async def export_recipe(
    recipe_id: UUID,
    format: str,
    db: AsyncSession = Depends(get_session),
):
    """Export recipe in various formats (markdown, json, pdf)."""
    recipe = await get_recipe(db, recipe_id)
    if not recipe or not recipe.is_public:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if format not in ["markdown", "json", "pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Use 'markdown', 'json', or 'pdf'"
        )

    try:
        if format == "markdown":
            # Convert recipe to Markdown
            recipe_dict = {
                'name': recipe.name,
                'description': recipe.description,
                'servings': recipe.servings,
                'prep_time': recipe.prep_time,
                'cook_time': recipe.cook_time,
                'total_time': (recipe.prep_time or 0) + (recipe.cook_time or 0) if recipe.prep_time or recipe.cook_time else None,
                'temperature': recipe.temperature,
                'difficulty': recipe.difficulty,
                'cuisine': recipe.cuisine,
                'category': recipe.category,
                'tags': recipe.tags or [],
                'notes': recipe.notes or [],
                'tips': recipe.tips or [],
                'is_public': recipe.is_public,
                'is_featured': recipe.is_featured,
                'language': recipe.language,
                'created_at': recipe.created_at,
                'updated_at': recipe.updated_at,
                'content': recipe.content or '',
                'ingredients_json': recipe.ingredients_json,
                'instructions_json': recipe.instructions_json,
            }

            markdown_content = MarkdownRecipeParser.generate_markdown(recipe_dict)

            return Response(
                content=markdown_content,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f'attachment; filename="{recipe.slug}.md"'
                }
            )

        elif format == "json":
            # Export as JSON
            recipe_data = convert_to_response(recipe)

            return Response(
                content=recipe_data.model_dump_json(indent=2),
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="{recipe.slug}.json"'
                }
            )

        else:  # format == "pdf"
            # TODO: Implement PDF export
            return {
                "message": "PDF export not yet implemented",
                "recipe_id": str(recipe_id),
                "format": format,
                "note": "PDF export functionality will be added in a future update"
            }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error exporting recipe: {e!s}"
        ) from e