from theo.core.services.reference_detection_service import (
    find_reference_strings,
    find_scripture_references,
    normalize_reference_text,
    should_detect_scripture_references,
)


def test_normalize_reference_text_supports_vs_separator() -> None:
    assert normalize_reference_text("john 3vs16") == "john 3:16"


def test_normalize_reference_text_supports_spaced_vs_separator() -> None:
    assert normalize_reference_text("JOHN 3 VS 16") == "john 3:16"


def test_normalize_reference_text_supports_ranges() -> None:
    assert normalize_reference_text("John 3:1 - 20") == "john 3:1-20"


def test_should_detect_scripture_references_ignores_commands() -> None:
    assert should_detect_scripture_references("/verse") is False


def test_should_detect_scripture_references_accepts_normal_scripture_text() -> None:
    assert should_detect_scripture_references("John 3:16") is True


def test_find_scripture_references_detects_full_book_name() -> None:
    references = find_scripture_references("John 3:16")
    assert len(references) == 1
    assert references[0].reference == "John 3:16"


def test_find_scripture_references_detects_short_book_alias() -> None:
    references = find_scripture_references("Jn 3:16")
    assert len(references) == 1
    assert references[0].reference == "John 3:16"


def test_find_scripture_references_detects_vs_style_reference() -> None:
    references = find_scripture_references("john 3vs16")
    assert len(references) == 1
    assert references[0].reference == "John 3:16"


def test_find_scripture_references_detects_numbered_book_alias() -> None:
    references = find_scripture_references("1 Cor 13:4")
    assert len(references) == 1
    assert references[0].reference == "1 Corinthians 13:4"


def test_find_scripture_references_detects_range() -> None:
    references = find_scripture_references("John 3:1-20")
    assert len(references) == 1
    assert references[0].reference == "John 3:1-20"
    assert references[0].is_range is True


def test_find_scripture_references_detects_multiple_references_in_order() -> None:
    references = find_reference_strings("Read Jn 3:16 and John 14:27 today")
    assert references == ("John 3:16", "John 14:27")


def test_find_scripture_references_deduplicates_equivalent_matches() -> None:
    references = find_reference_strings("John 3:16 and Jn 3:16")
    assert references == ("John 3:16",)


def test_find_scripture_references_ignores_invalid_range_order() -> None:
    references = find_reference_strings("John 3:20-1")
    assert references == ()


def test_find_scripture_references_ignores_time_like_text() -> None:
    references = find_reference_strings("The meeting is by 6:00 tonight")
    assert references == ()


def test_find_scripture_references_requires_book_name() -> None:
    references = find_reference_strings("3:16 is a popular verse format")
    assert references == ()
