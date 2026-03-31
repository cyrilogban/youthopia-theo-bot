from __future__ import annotations

import logging

import telebot

from theo.app.container import Container
from theo.core.services.reference_detection_service import (
    DetectedReference,
    find_scripture_references,
    should_detect_scripture_references,
)
from theo.core.services.translation_service import get_translation_or_default
from theo.core.services.verse_service import (
    VerseLookupError,
    fetch_scripture_text_by_reference,
    format_reference_message,
)


logger = logging.getLogger(__name__)



def register_autodetect(bot: telebot.TeleBot, container: Container) -> None:
    repo = container.group_repo

    def _is_bot_message(message: telebot.types.Message) -> bool:
        return bool(getattr(getattr(message, "from_user", None), "is_bot", False))

    def _current_translation(chat_id: int) -> str:
        record = repo.get_group(chat_id)
        if not record:
            return get_translation_or_default(None)
        return get_translation_or_default(record.translation)

    def _format_detected_scriptures(
        references: tuple[DetectedReference, ...],
        verse_texts: list[str],
        translation: str,
    ) -> str:
        sections: list[str] = []

        for reference, verse_text in zip(references, verse_texts):
            sections.append(
                format_reference_message(
                    reference.reference,
                    verse_text,
                    translation=translation,
                )
            )

        return "\n\n".join(sections)

    def _reply_with_detected_scriptures(message: telebot.types.Message) -> None:
        text = getattr(message, "text", "") or ""
        if not text or _is_bot_message(message):
            return

        if not should_detect_scripture_references(text):
            return

        references = find_scripture_references(text)
        if not references:
            return

        translation = _current_translation(message.chat.id)
        verse_texts: list[str] = []
        successful_references: list[DetectedReference] = []
        failed_references: list[str] = []

        for reference in references:
            try:
                verse_text = fetch_scripture_text_by_reference(
                    reference.reference,
                    translation=translation,
                )
                verse_texts.append(verse_text)
                successful_references.append(reference)
            except VerseLookupError:
                logger.exception(
                    "Failed to fetch detected scripture '%s'.",
                    reference.reference,
                )
                failed_references.append(reference.reference)

        if not successful_references:
            bot.reply_to(
                message,
                "I couldn't fetch that scripture right now. Please try again in a moment.",
            )
            return

        reply_text = _format_detected_scriptures(
            tuple(successful_references),
            verse_texts,
            translation,
        )

        if failed_references:
            reply_text = (
                f"{reply_text}\n\n"
                f"I couldn't fetch these references right now: {', '.join(failed_references)}"
            )

        bot.reply_to(message, reply_text)

    @bot.message_handler(
        content_types=["text"],
        func=lambda message: should_detect_scripture_references(
            getattr(message, "text", ""),
        ),
    )
    def _autodetect(message: telebot.types.Message) -> None:
        _reply_with_detected_scriptures(message)
