from datetime import datetime, timedelta
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


def log_verse_to_history(
    telegram_id: int,
    book: str,
    chapter: int,
    verse: int,
    category: str,
    delivery_path: str,
    translation: str = "kjv",
) -> bool:
    """Log a verse delivery to user's verse history. Returns True if logged successfully."""
    try:
        user = get_user(telegram_id)
        if not user:
            return False

        user_id = user["id"]

        supabase.table("verse_history").insert({
            "user_id": user_id,
            "book": book,
            "chapter": chapter,
            "verse": verse,
            "category": category,
            "delivery_path": delivery_path,
            "translation": translation,
        }).execute()

        return True

    except Exception:
        return False


def get_verse_history(telegram_id: int, limit: int = 50) -> list:
    """Get verse history for a user, limited to most recent verses."""
    try:
        user = get_user(telegram_id)
        if not user:
            return []

        user_id = user["id"]

        result = supabase.table("verse_history").select("*").eq(
            "user_id", user_id
        ).order("delivered_at", desc=True).limit(limit).execute()

        return result.data or []

    except Exception:
        return []
    
def update_user_tone(telegram_id: int, tone: str) -> bool:
    """Update the tone preference for a user."""
    try:
        supabase.table("users").update({
            "tone_preference": tone
        }).eq("telegram_id", telegram_id).execute()
        return True
    except Exception:
        return False

def get_community_stats() -> dict:
    """Aggregate high-level community engagement metrics from Supabase."""
    stats = {
        "total_users": 0,
        "total_saved_verses": 0,
        "verses_last_24h": 0,
    }
    try:
        # 1. Total users
        res_users = supabase.table("users").select("telegram_id", count="exact").execute()
        stats["total_users"] = res_users.count or 0

        # 2. Total saved verses
        res_saved = supabase.table("saved_verses").select("id", count="exact").execute()
        stats["total_saved_verses"] = res_saved.count or 0

        # 3. Verses sent in last 24 hours
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        res_history = supabase.table("verse_history").select("id", count="exact").filter("delivered_at", "gte", yesterday).execute()
        stats["verses_last_24h"] = res_history.count or 0

    except Exception:
        pass

    return stats