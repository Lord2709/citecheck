"""Who is calling.  Sign-in happens in the browser with Supabase (an e-mailed 6-digit code); every API request then
carries the Supabase access token, which we check by asking Supabase who it belongs to (works whatever signing keys
the project uses).  Answers are cached for a few minutes so a page full of requests costs one check."""
from __future__ import annotations

import hashlib
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class User:
    id: str
    email: str


class AuthError(Exception):
    pass


def supabase_lookup(settings) -> Callable:
    """token -> User, by calling GET {SUPABASE_URL}/auth/v1/user."""
    import httpx

    def lookup(token: str) -> User:
        try:
            r = httpx.get(f"{settings.supabase_url}/auth/v1/user", timeout=10,
                          headers={"Authorization": f"Bearer {token}", "apikey": settings.supabase_anon_key})
        except httpx.HTTPError as e:
            raise AuthError(f"could not reach the sign-in service ({type(e).__name__})") from e
        if r.status_code != 200:
            raise AuthError("your session has expired; please sign in again")
        j = r.json()
        if not j.get("id"):
            raise AuthError("invalid session")
        return User(id=j["id"], email=(j.get("email") or "").lower())
    return lookup


class TokenVerifier:
    def __init__(self, settings, lookup: Optional[Callable] = None, ttl: float = 300.0, clock=time.monotonic):
        self.settings, self.ttl, self.clock = settings, ttl, clock
        self.lookup = lookup or (supabase_lookup(settings) if settings.auth_mode == "supabase" else None)
        self._cache, self._lock = {}, threading.Lock()

    def verify(self, authorization: Optional[str]) -> User:
        if self.settings.auth_mode == "off":
            return User(id="dev-user", email=self.settings.dev_user_email)
        if not authorization or not authorization.lower().startswith("bearer "):
            raise AuthError("please sign in")
        token = authorization.split(" ", 1)[1].strip()
        key = hashlib.sha256(token.encode()).hexdigest()
        now = self.clock()
        with self._lock:
            hit = self._cache.get(key)
            if hit and hit[1] > now:
                return hit[0]
        user = self.lookup(token)
        with self._lock:
            if len(self._cache) > 5000:
                self._cache.clear()
            self._cache[key] = (user, now + self.ttl)
        return user
