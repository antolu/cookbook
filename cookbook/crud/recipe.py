import typing
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from cookbook.models.recipe import Recipe
from cookbook.schemas.recipe import RecipeCreate, RecipeSearchParams, RecipeUpdate


async def create_recipe(db: AsyncSession, recipe: RecipeCreate) -> Recipe:
    """Create a new recipe."""
    # Generate slug from name
    slug = recipe.name.lower().replace(" ", "-").replace("'", "")

    # Ensure slug is unique
    base_slug = slug
    counter = 1
    while await get_recipe_by_slug(db, slug):
        slug = f"{base_slug}-{counter}"
        counter += 1

    db_recipe = Recipe(
        name=recipe.name,
        slug=slug,
        language=recipe.language or "en",
        description=recipe.description,
        servings=recipe.servings,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        temperature=recipe.temperature,
        content=recipe.content,
        difficulty=recipe.difficulty,
        cuisine=recipe.cuisine,
        category=recipe.category,
        tags=recipe.tags or [],
        image_url=recipe.image_url,
        notes=recipe.notes or [],
        tips=recipe.tips or [],
        is_public=recipe.is_public,
        is_featured=recipe.is_featured,
    )

    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe


async def get_recipe(db: AsyncSession, recipe_id: UUID) -> Recipe | None:
    """Get a recipe by ID."""
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    return typing.cast(Recipe | None, result.scalar_one_or_none())


async def get_recipe_by_slug(db: AsyncSession, slug: str) -> Recipe | None:
    """Get a recipe by slug."""
    result = await db.execute(select(Recipe).where(Recipe.slug == slug))
    return typing.cast(Recipe | None, result.scalar_one_or_none())


async def get_recipes(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 20,
    public_only: bool = False,
    featured_only: bool = False,
) -> list[Recipe]:
    """Get recipes with pagination."""
    query = select(Recipe)

    if public_only:
        query = query.where(Recipe.is_public)

    if featured_only:
        query = query.where(Recipe.is_featured)

    query = query.order_by(desc(Recipe.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    return typing.cast(list[Recipe], list(result.scalars().all()))


async def search_recipes(
    db: AsyncSession, search_params: RecipeSearchParams
) -> tuple[list[Recipe], int]:
    """Search recipes with filters."""
    query = select(Recipe)
    count_query = select(func.count(Recipe.id))

    conditions = []

    # Public recipes only for non-authenticated users
    conditions.append(Recipe.is_public)

    # Text search
    if search_params.q:
        search_text = f"%{search_params.q}%"
        text_conditions = or_(
            Recipe.name.ilike(search_text),
            Recipe.description.ilike(search_text),
            Recipe.content.ilike(search_text),
        )
        conditions.append(text_conditions)

    # Category filter
    if search_params.category:
        conditions.append(Recipe.category == search_params.category)

    # Cuisine filter
    if search_params.cuisine:
        conditions.append(Recipe.cuisine == search_params.cuisine)

    # Difficulty filter
    if search_params.difficulty:
        conditions.append(Recipe.difficulty == search_params.difficulty)

    # Tags filter
    if search_params.tags:
        conditions.extend(Recipe.tags.contains([tag]) for tag in search_params.tags)

    # Time filters
    if search_params.max_prep_time:
        conditions.append(Recipe.prep_time <= search_params.max_prep_time)

    if search_params.max_cook_time:
        conditions.append(Recipe.cook_time <= search_params.max_cook_time)

    if search_params.max_total_time:
        # Filter by total time (prep + cook)
        conditions.append(
            (Recipe.prep_time + Recipe.cook_time) <= search_params.max_total_time
        )

    # Featured filter
    if search_params.is_featured is not None:
        conditions.append(Recipe.is_featured == search_params.is_featured)

    # Apply conditions
    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    # Get total count
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Apply ordering, offset, and limit
    query = (
        query
        .order_by(desc(Recipe.is_featured), desc(Recipe.created_at))
        .offset(search_params.offset)
        .limit(search_params.limit)
    )

    result = await db.execute(query)
    recipes = typing.cast(list[Recipe], list(result.scalars().all()))

    return recipes, total


async def update_recipe(
    db: AsyncSession, recipe_id: UUID, recipe_update: RecipeUpdate
) -> Recipe | None:
    """Update a recipe."""
    db_recipe = await get_recipe(db, recipe_id)
    if not db_recipe:
        return None

    update_data = recipe_update.model_dump(exclude_unset=True)

    # Update slug if name changed
    if "name" in update_data:
        new_slug = update_data["name"].lower().replace(" ", "-").replace("'", "")

        # Ensure slug is unique (unless it's the same recipe)
        base_slug = new_slug
        counter = 1
        while True:
            existing = await get_recipe_by_slug(db, new_slug)
            if not existing or existing.id == recipe_id:
                break
            new_slug = f"{base_slug}-{counter}"
            counter += 1

        update_data["slug"] = new_slug

    for field, value in update_data.items():
        setattr(db_recipe, field, value)

    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe


async def delete_recipe(db: AsyncSession, recipe_id: UUID) -> bool:
    """Delete a recipe."""
    db_recipe = await get_recipe(db, recipe_id)
    if not db_recipe:
        return False

    await db.delete(db_recipe)
    await db.commit()
    return True


async def get_recipe_count(db: AsyncSession, *, public_only: bool = False) -> int:
    """Get total number of recipes."""
    query = select(func.count(Recipe.id))

    if public_only:
        query = query.where(Recipe.is_public)

    result = await db.execute(query)
    count = result.scalar()
    return int(count) if count is not None else 0


async def get_featured_recipes(db: AsyncSession, limit: int = 5) -> list[Recipe]:
    """Get featured recipes."""
    query = (
        select(Recipe)
        .where(and_(Recipe.is_public, Recipe.is_featured))
        .order_by(desc(Recipe.created_at))
        .limit(limit)
    )

    result = await db.execute(query)
    return typing.cast(list[Recipe], list(result.scalars().all()))


async def get_recent_recipes(
    db: AsyncSession, *, limit: int = 10, public_only: bool = True
) -> list[Recipe]:
    """Get recently created recipes."""
    query = select(Recipe).order_by(desc(Recipe.created_at)).limit(limit)

    if public_only:
        query = query.where(Recipe.is_public)

    result = await db.execute(query)
    return typing.cast(list[Recipe], list(result.scalars().all()))


async def get_recipes_by_category(
    db: AsyncSession, category: str, *, limit: int = 20, public_only: bool = True
) -> list[Recipe]:
    """Get recipes by category."""
    query = (
        select(Recipe)
        .where(Recipe.category == category)
        .order_by(desc(Recipe.created_at))
        .limit(limit)
    )

    if public_only:
        query = query.where(Recipe.is_public)

    result = await db.execute(query)
    return typing.cast(list[Recipe], list(result.scalars().all()))


async def get_unique_categories(db: AsyncSession) -> list[str]:
    """Get all unique categories."""
    query = (
        select(Recipe.category)
        .where(and_(Recipe.category.is_not(None), Recipe.is_public))
        .distinct()
    )

    result = await db.execute(query)
    return [cat for cat in result.scalars().all() if cat]


async def get_unique_cuisines(db: AsyncSession) -> list[str]:
    """Get all unique cuisines."""
    query = (
        select(Recipe.cuisine)
        .where(and_(Recipe.cuisine.is_not(None), Recipe.is_public))
        .distinct()
    )

    result = await db.execute(query)
    return [cuisine for cuisine in result.scalars().all() if cuisine]


async def get_unique_tags(db: AsyncSession) -> list[str]:
    """Get all unique tags."""
    query = select(Recipe.tags).where(and_(Recipe.tags.is_not(None), Recipe.is_public))

    result = await db.execute(query)
    all_tags = set()
    for tag_list in result.scalars().all():
        if tag_list:
            all_tags.update(tag_list)

    return sorted(all_tags)
