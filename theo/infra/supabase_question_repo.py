from theo.infra.supabase_client import supabase

def save_anonymous_question(user_id: int, question_text: str) -> int | None:
    """Save an anonymous question to Supabase. Returns the question ID."""
    try:
        result = supabase.table("anonymous_questions").insert({
            "user_id": user_id,
            "question_text": question_text
        }).execute()
        
        if result.data:
            return result.data[0]["id"]
        return None
    except Exception:
        return None

def get_question_asker(question_id: int) -> int | None:
    """Get the user_id of the person who asked a specific question."""
    try:
        result = supabase.table("anonymous_questions").select("user_id").eq("id", question_id).execute()
        if result.data:
            return result.data[0]["user_id"]
        return None
    except Exception:
        return None

def mark_question_answered(question_id: int) -> bool:
    """Mark a question as answered in the database."""
    try:
        supabase.table("anonymous_questions").update({
            "is_answered": True
        }).eq("id", question_id).execute()
        return True
    except Exception:
        return False
