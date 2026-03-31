from __future__ import annotations


DEFAULT_TRANSLATION = "kjv"

SUPPORTED_TRANSLATIONS: dict[str, str] = {
    "kjv": "KJV",
    "web": "WEB",
    "bbe": "BBE",
    "asv": "ASV",
}


def list_supported_translations() -> tuple[str, ...]:
    return tuple(SUPPORTED_TRANSLATIONS.keys())


def get_default_translation() -> str:
    return DEFAULT_TRANSLATION


def is_supported_translation(translation: str) -> bool:
    normalized_translation = normalize_translation(translation)
    return normalized_translation in SUPPORTED_TRANSLATIONS


def normalize_translation(translation: str | None) -> str:
    if translation is None:
        return DEFAULT_TRANSLATION

    normalized_translation = translation.strip().lower()
    if not normalized_translation:
        return DEFAULT_TRANSLATION

    return normalized_translation


def validate_translation(translation: str | None) -> str:
    normalized_translation = normalize_translation(translation)
    if normalized_translation not in SUPPORTED_TRANSLATIONS:
        raise ValueError(f"Unsupported translation: {translation}")
    return normalized_translation


def get_translation_label(translation: str | None) -> str:
    normalized_translation = validate_translation(translation)
    return SUPPORTED_TRANSLATIONS[normalized_translation]


def get_translation_or_default(translation: str | None) -> str:
    normalized_translation = normalize_translation(translation)
    if normalized_translation not in SUPPORTED_TRANSLATIONS:
        return DEFAULT_TRANSLATION
    return normalized_translation


def render_translation_options() -> str:
    return ", ".join(SUPPORTED_TRANSLATIONS.values())
