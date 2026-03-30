"""
Deprecated migration utilities
--------------------------------

The previous code provided a migration path from an older Django-based
recipe export format into this application's SQLAlchemy/Markdown format.
That migration path depended on Django-specific data shapes and introduced
compatibility complexity that we no longer want in the main codebase.

To avoid accidental usage, the migration helpers have been removed and the
public entrypoint `run_full_migration` now raises an explicit error. If you
need to migrate data from an old Django export, extract the Django JSON and
run a one-off migration script outside of this repository that adapts the
data to the current Markdown recipe format.

If you intentionally depend on automated migration, please reach out so we
can provide a dedicated migration tool in a separate repository.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


def run_full_migration(
    db_session: AsyncSession, django_recipes: list[dict[str, Any]]
) -> None:
    """Disabled migration entrypoint.

    Raises a RuntimeError to make callers explicitly handle migration outside
    of the application runtime.
    """
    msg = (
        "Django-to-SQLAlchemy migration support has been removed from the main "
        "codebase. Extract your Django export and run a dedicated migration "
        "script that converts it to the Markdown/frontmatter format expected "
        "by this project."
    )
    raise RuntimeError(msg)
