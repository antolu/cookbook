from __future__ import annotations

import logging
from pathlib import Path

import typer

from cookbook.core.markdown import MarkdownRecipeParser, validate_markdown_recipe

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer(help="Cookbook CLI for migrations and utilities")


# Migration commands removed — migrations are out-of-band for this project.


@app.command()
def validate_markdown_recipe_file(
    markdown_file: str = typer.Argument(..., help="Path to Markdown recipe file"),
) -> None:
    """Validate a Markdown recipe file."""

    file_path = Path(markdown_file)
    if not file_path.exists():
        typer.echo(f"Error: File '{markdown_file}' does not exist", err=True)
        raise typer.Exit(1)

    # Read and validate
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    errors = validate_markdown_recipe(content)

    if errors:
        typer.echo(f"❌ Validation failed for {file_path.name}:")
        for error in errors:
            typer.echo(f"  - {error}")
        raise typer.Exit(1)
    typer.echo(f"✅ {file_path.name} is valid")


@app.command()
def parse_markdown_recipe(
    markdown_file: str = typer.Argument(..., help="Path to Markdown recipe file"),
) -> None:
    """Parse and display a Markdown recipe file."""

    file_path = Path(markdown_file)
    if not file_path.exists():
        typer.echo(f"Error: File '{markdown_file}' does not exist", err=True)
        raise typer.Exit(1)

    # Read and parse
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    try:
        recipe = MarkdownRecipeParser.parse_recipe(content)

        typer.echo(f"Recipe: {recipe.name}")
        if recipe.description:
            typer.echo(f"Description: {recipe.description}")
        if recipe.servings:
            typer.echo(f"Servings: {recipe.servings}")
        if recipe.prep_time:
            typer.echo(f"Prep Time: {recipe.prep_time} minutes")
        if recipe.cook_time:
            typer.echo(f"Cook Time: {recipe.cook_time} minutes")
        if recipe.difficulty:
            typer.echo(f"Difficulty: {recipe.difficulty}")
        if recipe.cuisine:
            typer.echo(f"Cuisine: {recipe.cuisine}")
        if recipe.category:
            typer.echo(f"Category: {recipe.category}")
        if recipe.tags:
            typer.echo(f"Tags: {', '.join(recipe.tags)}")

    except Exception as e:
        typer.echo(f"❌ Failed to parse recipe: {e}", err=True)
        raise typer.Exit(1) from e


@app.command()
def export_sample_recipes() -> None:
    """Export sample Markdown recipes for testing."""

    samples = [
        {
            "filename": "chocolate-chip-cookies.md",
            "content": """---
name: "Classic Chocolate Chip Cookies"
description: "Crispy on the outside, chewy on the inside chocolate chip cookies"
servings: "24 cookies"
prep_time: "15 minutes"
cook_time: "12 minutes"
temperature: 375
difficulty: "easy"
category: "dessert"
cuisine: "american"
tags: ["cookies", "dessert", "baking", "chocolate"]
notes: ["Store in airtight container for up to 1 week"]
tips: ["For chewier cookies, slightly underbake"]
public: true
featured: true
---

## Description

Classic chocolate chip cookies that are crispy on the outside and perfectly chewy on the inside. This foolproof recipe delivers bakery-quality cookies every time.

## Ingredients

- 2¼ cups all-purpose flour
- 1 tsp baking soda
- 1 tsp salt
- 1 cup butter, softened
- ¾ cup granulated sugar
- ¾ cup packed brown sugar
- 2 large eggs
- 2 tsp vanilla extract
- 2 cups chocolate chips

## Instructions

1. Preheat oven to 375°F (190°C).
2. In a medium bowl, whisk together flour, baking soda, and salt.
3. In a large bowl, cream butter and both sugars until light and fluffy.
4. Beat in eggs one at a time, then vanilla extract.
5. Gradually add flour mixture, mixing until just combined.
6. Stir in chocolate chips.
7. Drop rounded tablespoons of dough onto ungreased baking sheets.
8. Bake for 9-11 minutes until edges are golden brown.
9. Cool on baking sheet for 5 minutes before transferring to wire rack.

## Notes

- For chewier cookies, slightly underbake
- For crispier cookies, bake an extra 1-2 minutes
- Dough can be refrigerated for up to 3 days or frozen for up to 3 months

## Tips

- Room temperature ingredients mix better
- Don't overmix the dough to avoid tough cookies
- Use parchment paper for easy cleanup
""",
        },
        {
            "filename": "spaghetti-carbonara.md",
            "content": """---
name: "Authentic Spaghetti Carbonara"
description: "Traditional Roman pasta dish with eggs, cheese, and pancetta"
servings: "4 people"
prep_time: "10 minutes"
cook_time: "15 minutes"
difficulty: "medium"
category: "main"
cuisine: "italian"
tags: ["pasta", "italian", "quick", "traditional"]
notes: ["No cream in authentic carbonara!", "Timing is crucial for silky sauce"]
public: true
featured: false
---

## Description

Authentic Roman carbonara made with just five ingredients: pasta, eggs, pecorino cheese, pancetta, and black pepper. The secret is in the technique to create a silky, creamy sauce without scrambling the eggs.

## Ingredients

- 1 lb spaghetti
- 6 oz pancetta or guanciale, diced
- 4 large egg yolks
- 1 whole egg
- 1 cup freshly grated Pecorino Romano
- Freshly ground black pepper
- Salt for pasta water

## Instructions

1. Bring a large pot of salted water to boil for pasta.
2. Cook pancetta in a large skillet over medium heat until crispy.
3. Meanwhile, whisk eggs, egg yolks, and cheese in a bowl.
4. Cook spaghetti according to package directions until al dente.
5. Reserve 1 cup pasta cooking water before draining.
6. Add hot pasta to skillet with pancetta off heat.
7. Quickly add egg mixture while tossing pasta constantly.
8. Add pasta water gradually until creamy sauce forms.
9. Season generously with black pepper and serve immediately.

## Notes

- No cream in authentic carbonara!
- Timing is crucial - work quickly to prevent eggs from scrambling
- Pecorino Romano is traditional, but Parmesan can substitute

## Tips

- Have all ingredients ready before starting
- The pan should be hot but not on heat when adding eggs
- Toss vigorously to emulsify the sauce
""",
        },
    ]

    output_dir = Path("sample_recipes")
    output_dir.mkdir(exist_ok=True)

    for sample in samples:
        file_path = output_dir / sample["filename"]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(sample["content"])
        typer.echo(f"✅ Created {file_path}")

    typer.echo(f"\nSample recipes created in {output_dir}")


if __name__ == "__main__":
    app()
