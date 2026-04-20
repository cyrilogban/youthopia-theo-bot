import random
from datetime import date
from theo.infra.supabase_client import supabase


def get_votd_category() -> str:
    """Get the VOTD category based on the day of the week."""
    day_to_category = {
        0: "faith",        # Monday
        1: "love",         # Tuesday
        2: "peace",        # Wednesday
        3: "joy",          # Thursday
        4: "hope",         # Friday
        5: "patience",     # Saturday
        6: "forgiveness",  # Sunday
    }
    today = date.today().weekday()
    return day_to_category[today]


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
    """
    Get today's VOTD verse.
    - Same verse all day regardless of restarts.
    - Never repeats a verse within a category until all verses are used.
    - Then resets and starts fresh for that category.
    """
    today = str(date.today())
    category = get_votd_category()

    # Check if today's verse is already logged
    existing = supabase.table("votd_log").select("*").eq("verse_date", today).execute()
    if existing.data:
        row = existing.data[0]
        return {
            "book": row["book"],
            "chapter": row["chapter"],
            "verse": row["verse"],
        }

    # Get all verses in today's category
    all_verses = get_verses_by_category(category)
    if not all_verses:
        return None

    # Get all verses already used for this category
    used = supabase.table("votd_log").select("book, chapter, verse").eq("category", category).execute()
    used_set = {
        (row["book"], row["chapter"], row["verse"])
        for row in used.data
    }

    # Find verses not yet used in this category
    unused = [
        v for v in all_verses
        if (v["book"], v["chapter"], v["verse"]) not in used_set
    ]

    # If all verses have been used reset and start fresh
    if not unused:
        unused = all_verses

    # Pick a random unused verse
    chosen = random.choice(unused)

    # Log it to votd_log
    supabase.table("votd_log").insert({
        "verse_date": today,
        "category": category,
        "book": chosen["book"],
        "chapter": chosen["chapter"],
        "verse": chosen["verse"],
    }).execute()

    return chosen


def get_all_categories() -> list:
    """Get all category names."""
    result = supabase.table("categories").select("name").execute()
    return [row["name"] for row in result.data]