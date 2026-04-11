import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app as _fastapi_app  # noqa: E402


class _StripApiPrefix:
    """ASGI middleware that strips the /api prefix Vercel adds before forwarding to FastAPI."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] in ('http', 'websocket'):
            scope = dict(scope)
            path: str = scope.get('path', '/')
            if path.startswith('/api'):
                stripped = path[4:]
                scope['path'] = stripped if stripped else '/'
                raw: bytes = scope.get('raw_path', path.encode())
                scope['raw_path'] = raw[4:] if len(raw) > 4 else b'/'
        await self.app(scope, receive, send)


app = _StripApiPrefix(_fastapi_app)
