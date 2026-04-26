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

def save_verse(
    telegram_id: int,
    book: str,
    chapter: int,
    verse: int,
    category: str | None = None,
) -> bool:
    """Save a verse for a user. Returns True if saved successfully."""
    try:
        user = get_user(telegram_id)
        if not user:
            return False

        user_id = user["id"]

        # Check if already saved
        existing = supabase.table("saved_verses").select("id").eq(
            "user_id", user_id
        ).eq("book", book).eq("chapter", chapter).eq("verse", verse).execute()

        if existing.data:
            return False

        supabase.table("saved_verses").insert({
            "user_id": user_id,
            "book": book,
            "chapter": chapter,
            "verse": verse,
            "category": category,
        }).execute()

        return True

    except Exception:
        return False


def get_saved_verses(telegram_id: int) -> list:
    """Get all saved verses for a user."""
    try:
        user = get_user(telegram_id)
        if not user:
            return []

        user_id = user["id"]

        result = supabase.table("saved_verses").select("*").eq(
            "user_id", user_id
        ).order("saved_at", desc=True).execute()

        return result.data or []

    except Exception:
        return []


def delete_saved_verse(telegram_id: int, saved_verse_id: int) -> bool:
    """Delete a saved verse by its id. Returns True if deleted successfully."""
    try:
        user = get_user(telegram_id)
        if not user:
            return False

        user_id = user["id"]

        supabase.table("saved_verses").delete().eq(
            "id", saved_verse_id
        ).eq("user_id", user_id).execute()

        return True

    except Exception:
        return False
    
def update_user_translation(telegram_id: int, translation: str) -> bool:
    """Update the translation preference for a user."""
    try:
        supabase.table("users").update({
            "translation": translation
        }).eq("telegram_id", telegram_id).execute()
        return True
    except Exception:
        return False