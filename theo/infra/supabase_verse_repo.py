import random
from theo.infra.supabase_client import supabase


def get_votd_category() -> str:
    """Get the category marked as VOTD source."""
    result = supabase.table("categories").select("name").eq("is_votd_source", True).single().execute()
    return result.data["name"]


def get_verses_by_category(category_name: str) -> list:
    """Get all verse references for a given category."""
    category = supabase.table("categories").select("id").eq("name", category_name).single().execute()
    category_id = category.data["id"]

    verses = supabase.table("verses").select("*").eq("category_id", category_id).execute()
    return verses.data


def get_random_verse_by_category(category_name: str) -> dict:
    """Get a single random verse reference from a category."""
    verses = get_verses_by_category(category_name)
    if not verses:
        return None
    return random.choice(verses)


def get_votd_verse() -> dict:
    """Get a random verse from the VOTD category."""
    category = get_votd_category()
    return get_random_verse_by_category(category)


def get_all_categories() -> list:
    """Get all category names."""
    result = supabase.table("categories").select("name").execute()
    return [row["name"] for row in result.data]