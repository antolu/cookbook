from __future__ import annotations

from cookbook.models.user import User

# Re-exporting User for convenience if other modules still import it from here
__all__ = ["User"]

# The current_active_user and current_superuser dependencies are now
# implemented in cookbook.dependencies as get_current_user and get_current_admin_user.
