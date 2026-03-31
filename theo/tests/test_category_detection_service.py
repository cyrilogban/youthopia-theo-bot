from theo.core.services.category_detection_service import (
    detect_category,
    should_handle_category_request,
)



def test_detect_category_from_phrase() -> None:
    categories = ("faith", "love", "peace", "joy", "hope", "patience", "forgiveness")
    assert detect_category("I need hope scripture", categories) == "hope"



def test_should_handle_plain_category_message() -> None:
    categories = ("faith", "love", "peace")
    assert should_handle_category_request("peace", categories) is True



def test_should_ignore_non_scripture_message() -> None:
    categories = ("faith", "love", "peace")
    assert should_handle_category_request("peaceful evening everyone", categories) is False
