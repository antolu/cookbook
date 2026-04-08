from typing import Any

class Post:
    metadata: dict[str, Any]
    content: str

def loads(s: str) -> Post: ...
