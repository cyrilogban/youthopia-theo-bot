from __future__ import annotations

from unittest.mock import Mock

from theo.core.services import verse_service



def test_list_categories_matches_config() -> None:
    assert verse_service.list_categories() == (
        "faith",
        "love",
        "peace",
        "joy",
        "hope",
        "patience",
        "forgiveness",
    )



def test_fetch_verse_uses_requested_category(monkeypatch) -> None:
    reference = verse_service.VerseReference(book="John", chapter=14, verse=27)
    monkeypatch.setattr(verse_service.random, "shuffle", lambda items: None)
    monkeypatch.setattr(verse_service, "_fetch_verse_text", lambda _, translation=None: "Peace I leave with you.")

    verse_response = verse_service.get_scripture_by_category("peace")

    assert verse_response.category == "peace"
    assert verse_response.reference == reference
    assert verse_response.text == "Peace I leave with you."



def test_fetch_verse_skips_current_reference_for_another_verse(monkeypatch) -> None:
    monkeypatch.setattr(verse_service.random, "shuffle", lambda items: None)
    monkeypatch.setattr(verse_service, "_fetch_verse_text", lambda reference, translation=None: reference.reference)

    verse_response = verse_service.get_scripture_by_category(
        "peace",
        exclude_reference="John 14:27",
    )

    assert verse_response.reference.reference == "Philippians 4:6"



def test_fetch_verse_hits_votd_category_when_not_provided(monkeypatch) -> None:
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"text": "Peace I leave with you."}
    mocked_get = Mock(return_value=mock_response)

    monkeypatch.setattr(verse_service.requests, "get", mocked_get)
    monkeypatch.setattr(verse_service.random, "shuffle", lambda items: None)

    message = verse_service.fetch_verse()

    assert message.startswith("\U0001F4D6 John 14:27")
    mocked_get.assert_called_once()

def test_format_reference_message_uses_blockquote_for_short_verse() -> None:
    message = verse_service.format_reference_message(
        "John 14:27",
        "Peace I leave with you.",
        translation="kjv",
    )

    assert message == (
        "\U0001F4D6 John 14:27 (KJV)\n\n"
        "<blockquote>Peace I leave with you.</blockquote>"
    )


def test_format_reference_message_uses_expandable_quote_for_long_or_multiline_verse() -> None:
    message = verse_service.format_reference_message(
        "Psalm 119:105",
        "Line one\nLine two & more",
        translation="kjv",
    )

    assert "<blockquote expandable>" in message
    assert "Line two &amp; more" in message

