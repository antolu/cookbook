#!/bin/bash
set -e

echo "Starting cookbook..."

# Function to wait for database
wait_for_db() {
    echo "Waiting for database to be ready..."
    # Simple check using python
    python << END
import asyncio
import asyncpg
import os
import time
import sys

async def check_db():
    host = os.getenv('COOKBOOK_DATABASE_HOST', 'localhost')
    port = int(os.getenv('COOKBOOK_DATABASE_PORT', 5432))
    user = os.getenv('COOKBOOK_DATABASE_USER', 'cookbook')
    password = os.getenv('COOKBOOK_DATABASE_PASSWORD', 'cookbook')
    database = os.getenv('COOKBOOK_DATABASE_NAME', 'cookbook')

    max_attempts = 30
    attempt = 0
    while attempt < max_attempts:
        try:
            # Check if we can connect
            conn = await asyncpg.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                timeout=5
            )
            await conn.close()
            print("Database is ready!")
            return True
        except Exception as e:
            attempt += 1
            print(f"Database not ready (attempt {attempt}/{max_attempts}): {e}")
            time.sleep(2)
    return False

if __name__ == "__main__":
    result = asyncio.run(check_db())
    sys.exit(0 if result else 1)
END
}

# Wait for DB if not in test mode or something
if [ "$SKIP_DB_WAIT" != "true" ]; then
    wait_for_db
fi

# Run migrations
if [ -d "alembic" ] && [ -f "alembic.ini" ]; then
    echo "Running migrations..."
    # Ensure alembic uses the correct database URL from env
    alembic upgrade head
fi

# Execute CMD
exec "$@"
