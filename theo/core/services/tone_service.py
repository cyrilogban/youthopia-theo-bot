from theo.infra.supabase_user_repo import get_user


TONE_INTROS = {
    "warm": [
        "Good morning, {name}. Here is your verse for today.",
        "Hey {name}, here is a word for you today.",
        "Good morning {name}. Start your day with this.",
    ],
    "devotional": [
        "Take a moment with this word today, {name}. Let it speak to you.",
        "Pause and reflect on this verse today, {name}.",
        "Here is your scripture for quiet time today, {name}.",
    ],
    "bold": [
        "This verse is for you today, {name}. Stand on it and walk in it.",
        "{name}, this word is not a suggestion. Receive it and move.",
        "Here is your word for today, {name}. Let it fuel you.",
    ],
    "gentle": [
        "Whenever you are ready, {name}, here is a word just for you.",
        "No rush, {name}. Here is a verse to carry with you today.",
        "This one is for you today, {name}. Take it easy.",
    ],
}

DEFAULT_TONE = "warm"


def get_tone_intro(telegram_id: int | None, name: str) -> str:
    """Get a tone-based intro for a user by their telegram_id."""
    import random

    tone = DEFAULT_TONE

    if telegram_id:
        try:
            user = get_user(telegram_id)
            if user:
                tone = user.get("tone_preference") or DEFAULT_TONE
        except Exception:
            tone = DEFAULT_TONE

    intros = TONE_INTROS.get(tone, TONE_INTROS[DEFAULT_TONE])
    return random.choice(intros).format(name=name)


def get_tone_intro_for_group(tone: str, name: str) -> str:
    """Get a tone-based intro using a known tone string."""
    import random

    intros = TONE_INTROS.get(tone, TONE_INTROS[DEFAULT_TONE])
    return random.choice(intros).format(name=name)