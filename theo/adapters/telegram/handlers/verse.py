from __future__ import annotations

import logging
import re
import threading
from typing import Optional

import telebot
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from theo.adapters.telegram.views.keyboards import (
    build_verse_actions_keyboard,
)
from theo.adapters.telegram.views.render import (
    render_forward_instruction,
    render_verse_lookup_error,
)
from theo.app.container import Container
from theo.core.services.category_detection_service import detect_category
from theo.core.services.translation_service import get_translation_or_default
from theo.core.services.verse_service import (
    UnknownCategoryError,
    VerseLookupError,
    format_reference_message,
    format_verse_message,
    fetch_scripture_text_by_reference,
    get_scripture_by_category,
    list_categories,
)
from theo.infra.supabase_user_repo import log_verse_to_history


logger = logging.getLogger(__name__)
CALLBACK_PREFIX = "verse|"


def register_verse(bot: telebot.TeleBot, container: Container) -> None:
    repo = container.group_repo

    def _translation_for_chat(chat_id: int) -> str:
        record = repo.get_group(chat_id)
        if not record:
            return get_translation_or_default(None)
        return get_translation_or_default(record.translation)

    def _resolve_category(category: str) -> str:
        if category == "general":
            from theo.infra.supabase_verse_repo import get_votd_category as get_day_category
            return get_day_category()
        return category

    def _reply_with_category_verse(
        message: telebot.types.Message,
        category: str,
        exclude_reference: str | None = None,
    ) -> None:
        try:
            resolved_category = _resolve_category(category)
            translation = _translation_for_chat(message.chat.id)
            verse_response = get_scripture_by_category(
                resolved_category,
                exclude_reference=exclude_reference,
                translation=translation,
            )
            bot.reply_to(
                message,
                format_verse_message(verse_response),
                reply_markup=build_verse_actions_keyboard(
                    verse_response.category,
                    verse_response.reference.reference,
                ),
                parse_mode="HTML",
            )
            
            # Log to verse history for private chats only
            if message.chat.type == "private":
                log_verse_to_history(
                    telegram_id=message.from_user.id,
                    book=verse_response.reference.book,
                    chapter=verse_response.reference.chapter,
                    verse=verse_response.reference.verse,
                    category=verse_response.category,
                    delivery_path="category_command",
                    translation=translation,
                )
        except (UnknownCategoryError, VerseLookupError):
            logger.exception("Failed to fetch scripture for category '%s'.", category)
            bot.reply_to(message, "Could not fetch a verse right now. Please try again.")

    def _edit_with_category_verse(
        call: CallbackQuery,
        category: str,
        exclude_reference: str | None = None,
    ) -> None:
        try:
            resolved_category = _resolve_category(category)
            translation = _translation_for_chat(call.message.chat.id)
            verse_response = get_scripture_by_category(
                resolved_category,
                exclude_reference=exclude_reference,
                translation=translation,
            )
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=format_verse_message(verse_response),
                reply_markup=build_verse_actions_keyboard(
                    verse_response.category,
                    verse_response.reference.reference,
                ),
                parse_mode="HTML",
            )
            bot.answer_callback_query(call.id)
            
            # Log to verse history for private chats only
            if call.message.chat.type == "private":
                log_verse_to_history(
                    telegram_id=call.from_user.id,
                    book=verse_response.reference.book,
                    chapter=verse_response.reference.chapter,
                    verse=verse_response.reference.verse,
                    category=verse_response.category,
                    delivery_path="next_button",
                    translation=translation,
                )
        except (UnknownCategoryError, VerseLookupError):
            logger.exception("Failed to fetch scripture for category '%s'.", category)
            bot.answer_callback_query(call.id, "Could not fetch a verse. Try again.")

    def _parse_callback_data(data: str) -> tuple[str, list[str]]:
        parts = data.split("|", 3)
        if len(parts) < 2 or parts[0] != "verse":
            raise ValueError("Unsupported callback data.")
        return parts[1], parts[2:]

    @bot.callback_query_handler(
        func=lambda call: str(getattr(call, "data", "")).startswith(CALLBACK_PREFIX)
    )
    def _verse_callbacks(call: CallbackQuery) -> None:
        try:
            action, payload = _parse_callback_data(call.data)
        except ValueError:
            bot.answer_callback_query(call.id)
            return

        if action == "another" and len(payload) == 2:
            _edit_with_category_verse(
                call,
                payload[0],
                exclude_reference=payload[1],
            )
            return

        if action == "forward":
            bot.answer_callback_query(
                call.id,
                render_forward_instruction(),
                show_alert=True,
            )
            return

        if action == "save" and len(payload) == 2:
            category = payload[0]
            reference = payload[1]

            try:
                parts = reference.split(" ")
                book = " ".join(parts[:-1])
                chapter_verse = parts[-1].split(":")
                chapter = int(chapter_verse[0])
                verse = int(chapter_verse[1])

                from theo.infra.supabase_user_repo import save_verse
                telegram_id = call.from_user.id

                saved = save_verse(
                    telegram_id=telegram_id,
                    book=book,
                    chapter=chapter,
                    verse=verse,
                    category=category,
                )

                if saved:
                    bot.answer_callback_query(
                        call.id,
                        "Verse saved successfully.",
                        show_alert=True,
                    )
                else:
                    bot.answer_callback_query(
                        call.id,
                        "This verse is already in your saved verses.",
                        show_alert=True,
                    )

            except Exception:
                logger.exception("Failed to save verse.")
                bot.answer_callback_query(
                    call.id,
                    "Could not save verse right now. Please try again.",
                    show_alert=True,
                )
            return

        bot.answer_callback_query(call.id)

    def _parse_inline_query(query: str) -> tuple[str, str]:
        """Parse inline query and return (query_type, query_value).
        
        Returns:
            - ("category", category_name) if query matches a category
            - ("reference", reference_string) if query looks like "Book Chapter:Verse"
            - ("keyword", query_string) if query is a keyword search
        """
        normalized_query = query.strip().lower()
        if not normalized_query:
            return ("help", "")

        categories = list_categories()
        
        # Check for exact category match or category with hint
        detected_category = detect_category(normalized_query, categories)
        if detected_category and (
            normalized_query == detected_category
            or any(hint in normalized_query for hint in ("scripture", "verse", "bible", "word"))
        ):
            return ("category", detected_category)

        # Check for scripture reference pattern (e.g., "John 3:16")
        if _looks_like_scripture_reference(normalized_query):
            return ("reference", query.strip())

        # Default to keyword search
        return ("keyword", normalized_query)

    def _looks_like_scripture_reference(text: str) -> bool:
        """Check if text looks like a scripture reference (e.g., 'John 3:16')."""
        # Pattern: Word(s) followed by number:number
        pattern = r"^[a-z\s0-9]+\s+\d+:\d+$"
        return bool(re.match(pattern, text.lower()))

    def _get_category_name_from_keyword(keyword: str) -> str | None:
        """Try to find a category matching the keyword."""
        categories = list_categories()
        detected = detect_category(keyword, categories)
        return detected

    def _build_inline_verse_result(
        verse_id: str,
        reference: str,
        verse_text: str,
        category: str,
        translation: str,
    ) -> InlineQueryResultArticle:
        """Build an inline query result for a verse."""
        # Create preview description (first 100 chars)
        preview = verse_text.strip()[:100]
        if len(verse_text) > 100:
            preview += "..."

        # Create the full formatted message
        full_message = format_reference_message(reference, verse_text, translation=translation)

        # Create inline keyboard with Save|Next|Share buttons
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton(
                "Save",
                callback_data=f"{CALLBACK_PREFIX}save|{category}|{reference}",
            ),
            InlineKeyboardButton(
                "Next",
                callback_data=f"{CALLBACK_PREFIX}another|{category}|{reference}",
            ),
            InlineKeyboardButton(
                "Share",
                callback_data=f"{CALLBACK_PREFIX}forward",
            ),
        )

        return InlineQueryResultArticle(
            id=verse_id,
            title=reference,
            description=preview,
            input_message_content=InputTextMessageContent(
                message_text=full_message,
                parse_mode="HTML",
            ),
            reply_markup=keyboard,
        )

    def _handle_inline_query_category(
        query_id: str,
        category: str,
        translation: str,
    ) -> None:
        """Handle inline query for a specific category with timeout protection."""
        results_container: dict[str, list] = {"results": []}

        def _fetch_verses():
            try:
                results: list[InlineQueryResultArticle] = []
                categories = list_categories()

                # Get up to 5 verses from the category (with timeout per fetch)
                for i in range(5):
                    exclude_ref = None
                    if i > 0 and results:
                        exclude_ref = results[-1].title

                    try:
                        verse_response = get_scripture_by_category(
                            category,
                            exclude_reference=exclude_ref,
                            translation=translation,
                        )
                        
                        verse_id = f"cat_{category}_{i}_{verse_response.reference.reference.replace(' ', '_').replace(':', '')}"
                        result = _build_inline_verse_result(
                            verse_id=verse_id,
                            reference=verse_response.reference.reference,
                            verse_text=verse_response.text,
                            category=verse_response.category,
                            translation=verse_response.translation,
                        )
                        results.append(result)
                    except (UnknownCategoryError, VerseLookupError):
                        break

                results_container["results"] = results
            except Exception as e:
                logger.debug("Error in category verse fetch: %s", str(e))

        # Run in thread with 4 second timeout
        thread = threading.Thread(target=_fetch_verses, daemon=True)
        thread.start()
        thread.join(timeout=4)

        try:
            if results_container["results"]:
                bot.answer_inline_query(query_id, results_container["results"], cache_time=0)
            elif not thread.is_alive():
                # Thread finished but no results
                bot.answer_inline_query(
                    query_id,
                    [],
                    switch_pm_text="No verses found. Try a different category.",
                    switch_pm_parameter="category",
                )
            # If thread still alive, don't answer - query will expire
        except Exception as e:
            logger.debug("Failed to answer category inline query: %s", str(e))

    def _handle_inline_query_reference(
        query_id: str,
        reference: str,
        translation: str,
    ) -> None:
        """Handle inline query for a specific scripture reference.
        
        Uses timeout protection to prevent Telegram query expiration.
        """
        # Use a container to share results between threads
        results_container: dict[str, Optional[InlineQueryResultArticle]] = {"result": None, "error": False}

        def _fetch_and_build():
            try:
                verse_text = fetch_scripture_text_by_reference(reference, translation=translation)
                
                # Determine category (default to "general")
                detected_category = detect_category(reference, list_categories())
                category = detected_category if detected_category else "general"

                verse_id = f"ref_{reference.replace(' ', '_').replace(':', '')}"
                result = _build_inline_verse_result(
                    verse_id=verse_id,
                    reference=reference,
                    verse_text=verse_text,
                    category=category,
                    translation=translation,
                )
                results_container["result"] = result
            except (VerseLookupError, Exception) as e:
                logger.debug("Failed to fetch reference '%s': %s", reference, str(e))
                results_container["error"] = True

        # Run fetch in thread with timeout
        thread = threading.Thread(target=_fetch_and_build, daemon=True)
        thread.start()
        thread.join(timeout=3)  # 3 second timeout for API calls

        # Only answer if we got a result in time
        if results_container["result"]:
            try:
                bot.answer_inline_query(query_id, [results_container["result"]], cache_time=3600)
            except Exception as e:
                logger.debug("Failed to answer inline query (may have expired): %s", str(e))
        elif thread.is_alive():
            # Timeout: don't try to answer, query will expire on Telegram side
            logger.debug("Inline reference query timeout for: %s", reference)
        else:
            # Error occurred
            try:
                bot.answer_inline_query(
                    query_id,
                    [],
                    switch_pm_text="Could not fetch that verse. Try a category like: hope, peace, faith",
                    switch_pm_parameter="reference_error",
                )
            except Exception as e:
                logger.debug("Failed to answer inline error query: %s", str(e))

    def _handle_inline_query_keyword(
        query_id: str,
        keyword: str,
        translation: str,
    ) -> None:
        """Handle inline query for keyword search with timeout protection."""
        results_container: dict[str, list] = {"results": []}

        def _search_by_keyword():
            try:
                results: list[InlineQueryResultArticle] = []
                categories = list_categories()

                # Try to find a category matching the keyword
                detected_category = _get_category_name_from_keyword(keyword)

                if detected_category:
                    # Get verses from the detected category (with timeout)
                    for i in range(5):
                        exclude_ref = None
                        if i > 0 and results:
                            exclude_ref = results[-1].title

                        try:
                            verse_response = get_scripture_by_category(
                                detected_category,
                                exclude_reference=exclude_ref,
                                translation=translation,
                            )
                            
                            verse_id = f"kw_{detected_category}_{i}_{verse_response.reference.reference.replace(' ', '_').replace(':', '')}"
                            result = _build_inline_verse_result(
                                verse_id=verse_id,
                                reference=verse_response.reference.reference,
                                verse_text=verse_response.text,
                                category=verse_response.category,
                                translation=verse_response.translation,
                            )
                            results.append(result)
                        except (UnknownCategoryError, VerseLookupError):
                            break

                results_container["results"] = results
            except Exception as e:
                logger.debug("Error in keyword search: %s", str(e))

        # Run in thread with 4 second timeout
        thread = threading.Thread(target=_search_by_keyword, daemon=True)
        thread.start()
        thread.join(timeout=4)

        try:
            if results_container["results"]:
                bot.answer_inline_query(query_id, results_container["results"], cache_time=0)
            elif not thread.is_alive():
                # Thread finished but no results
                categories = list_categories()
                category_list = ", ".join(category.title() for category in categories)
                bot.answer_inline_query(
                    query_id,
                    [],
                    switch_pm_text=f"Try a category: {category_list}",
                    switch_pm_parameter="help",
                )
            # If thread still alive, don't answer - query will expire
        except Exception as e:
            logger.debug("Failed to answer keyword inline query: %s", str(e))

    @bot.inline_handler()
    def _inline_query_handler(inline_query: telebot.types.InlineQuery) -> None:
        """Handle inline queries for scripture search with timeout protection."""
        try:
            query = inline_query.query.strip()
            
            # If empty query, show help
            if not query:
                bot.answer_inline_query(
                    inline_query.id,
                    [],
                    switch_pm_text="Type a category (hope, peace, faith, etc.) or scripture reference",
                    switch_pm_parameter="inline_help",
                )
                return

            # Get user's translation preference
            translation = _translation_for_chat(inline_query.from_user.id)

            # Parse query to determine type (this should be fast)
            query_type, query_value = _parse_inline_query(query)

            # Handler execution in thread with timeout to prevent query expiration
            handler_container: dict[str, bool] = {"executed": False}

            def _run_handler():
                try:
                    if query_type == "category":
                        _handle_inline_query_category(inline_query.id, query_value, translation)
                    elif query_type == "reference":
                        _handle_inline_query_reference(inline_query.id, query_value, translation)
                    elif query_type == "keyword":
                        _handle_inline_query_keyword(inline_query.id, query_value, translation)
                    handler_container["executed"] = True
                except Exception as e:
                    logger.debug("Handler exception: %s", str(e))

            # Run handler in thread with 8 second timeout max
            thread = threading.Thread(target=_run_handler, daemon=True)
            thread.start()
            thread.join(timeout=8)

            if not handler_container["executed"] and thread.is_alive():
                logger.debug("Inline handler timeout for query: %s", query)

        except Exception as e:
            logger.debug("Outer exception in inline query handler: %s", str(e))
            # Don't answer_inline_query here to avoid double-answer and query expiration