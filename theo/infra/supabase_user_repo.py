from datetime import datetime
from theo.infra.supabase_client import supabase


def get_user(telegram_id: int) -> dict | None:
    """Get a user by their Telegram ID. Returns None if not found."""
    try:
        result = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception:
        return None


def create_user(
    telegram_id: int,
    first_name: str | None = None,
    username: str | None = None,
) -> dict | None:
    """Create a new user record in Supabase."""
    try:
        result = supabase.table("users").insert({
            "telegram_id": telegram_id,
            "first_name": first_name,
            "username": username,
            "tone_preference": "warm",
            "translation": "kjv",
        }).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception:
        return None


def get_or_create_user(
    telegram_id: int,
    first_name: str | None = None,
    username: str | None = None,
) -> tuple[dict | None, bool]:
    """
    Get existing user or create a new one.
    Returns (user, is_new) where is_new is True if just created.
    """
    user = get_user(telegram_id)
    if user:
        return user, False

    new_user = create_user(telegram_id, first_name, username)
    return new_user, True