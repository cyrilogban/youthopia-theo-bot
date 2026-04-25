# NOTE: This file is no longer used in production.
# Replaced by Supabase user registration in supabase_user_repo.py
# Kept for documentation and reference purposes only.
"""Simple in-memory cache for tracking first-time users."""

from typing import Set
import time


class FirstTimeUserCache:
    """Tracks which users/chats have already received the welcome verse."""
    
    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize cache.
        
        Args:
            ttl_seconds: How long to remember a user (1 hour = 3600s)
        """
        self.ttl_seconds = ttl_seconds
        self._cache: dict[int, float] = {}  # {user_id: timestamp}
    
    def is_first_time(self, user_id: int) -> bool:
        """Check if user is visiting for the first time (or cache expired)."""
        now = time.time()
        
        if user_id not in self._cache:
            self._cache[user_id] = now
            return True
        
        cached_time = self._cache[user_id]
        if now - cached_time > self.ttl_seconds:
            # Cache expired, treat as first time
            self._cache[user_id] = now
            return True
        
        # Already seen in this session
        return False
    
    def mark_seen(self, user_id: int) -> None:
        """Mark user as seen."""
        self._cache[user_id] = time.time()


# Global instance
first_time_cache = FirstTimeUserCache(ttl_seconds=3600)
