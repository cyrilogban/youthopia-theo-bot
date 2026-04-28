# Inline Query Feature Guide - Theo Bible Bot

## Overview

The **Inline Query** feature allows users to search Bible verses directly from the message input field without needing to use commands. Users simply type `@theo_bot_username` followed by their search query, and results appear as clickable suggestions.

**Status**: ✅ Implemented and ready for use

---

## How It Works

### User Experience

1. User opens any chat (private, group, or channel)
2. User types: `@iamtheobot [query]`
3. Theo returns up to 5 Bible verses matching the query
4. User clicks a result → verse is posted to that chat
5. User can interact via inline buttons: **Save | Next | Share**

### Example Queries

```
@iamtheobot hope
    → Returns 5 verses from the "hope" category

@iamtheobot John 3:16
    → Returns that specific scripture reference

@iamtheobot peace verses
    → Searches for "peace" category and returns verses

@iamtheobot love
    → Returns 5 verses from the "love" category
```

---

## Supported Query Types

### 1. **Category Search**
- **Format**: `@theo [category]` or `@theo [category] verses`
- **Categories**: faith, love, peace, joy, hope, patience, forgiveness
- **Result**: 5 random verses from that category
- **Example**: `@theo hope` → 5 hope verses

### 2. **Scripture Reference Search**
- **Format**: `@theo Book Chapter:Verse`
- **Supports aliases**: "John", "jhn", "jn", "1 Corinthians", "1 cor", etc.
- **Result**: That specific verse
- **Example**: `@theo John 3:16` → John 3:16 verse only
- **Caching**: 1 hour (API-cached for performance)

### 3. **Keyword Search**
- **Format**: `@theo [any text]`
- **Behavior**: Searches for keyword matches in categories
- **Result**: Verses from matching category or help message
- **Example**: `@theo hope verses` → searches for "hope", returns hope category verses

---

## Result Format

Each inline result shows:

```
📖 John 3:16
Preview: "For God so loved the world that he gave his one and only Son..."

[💾 Save] [➡️ Next] [📤 Share]
```

### Inline Buttons

| Button | Action | Behavior |
|--------|--------|----------|
| **💾 Save** | Saves verse | Saves verse to user's collection (private chat only) |
| **➡️ Next** | Next verse | Shows another verse from same category |
| **📤 Share** | Share info | Shows forwarding instructions |

---

## Enabling Inline Mode

### ⚙️ One-Time Setup (Via BotFather)

To enable inline mode, the bot owner must configure it with Telegram's BotFather:

1. **Open Telegram**, search for `@BotFather`
2. **Send**: `/mybots` → select your bot
3. **Send**: `/inline` → select your bot
4. **Option: Enable**

Once enabled, Telegram automatically handles inline query routing to your bot.

---

## Technical Implementation

### Architecture

```
User types: "@theo_bot_username query"
    ↓
Telegram sends: InlineQuery event
    ↓
_inline_query_handler() receives query
    ↓
_parse_inline_query() determines query type
    ↓
Routes to handler:
    - Category → _handle_inline_query_category()
    - Reference → _handle_inline_query_reference()
    - Keyword → _handle_inline_query_keyword()
    ↓
Returns: List of InlineQueryResultArticle
    ↓
User sees results and clicks one
    ↓
Verse posted to chat
```

### Polling Configuration

The bot's polling has been updated to include `inline_query`:

```python
bot.infinity_polling(
    allowed_updates=[
        "message", 
        "callback_query", 
        "my_chat_member", 
        "chat_member",
        "inline_query"  # ← Added for inline queries
    ]
)
```

### Files Modified

1. **[theo/adapters/telegram/handlers/verse.py](theo/adapters/telegram/handlers/verse.py)**
   - Added inline query handler
   - Added 8 new helper functions
   - Added inline result builder

2. **[theo/app/main.py](theo/app/main.py)**
   - Added `"inline_query"` to `allowed_updates`

---

## Response Details

### Category Query Response

```
Query: "@theo hope"

Results:
  1. Jeremiah 29:11 - "For I know the plans I have for you..."
  2. Romans 15:4 - "For everything that was written in the past..."
  3. Psalm 42:11 - "Why, my soul, are you downcast?..."
  4. (... 2 more verses)
```

### Reference Query Response

```
Query: "@theo John 3:16"

Result:
  1. John 3:16 - "For God so loved the world that he gave his one and only Son..."
  
Note: Reference queries are cached for 1 hour for performance
```

### Keyword Search Response

```
Query: "@theo peace scripture"

Results:
  1. John 14:27 - "Peace I leave with you..."
  2. Philippians 4:6 - "Do not be anxious about anything..."
  3. Isaiah 26:3 - "You will keep in perfect peace..."
  4. (... 2 more verses)
```

---

## Caching Strategy

| Query Type | Cache Time | Reason |
|-----------|-----------|--------|
| Category | 0 sec | Live results (varies per request) |
| Reference | 3600 sec (1hr) | Same reference always returns same verse |
| Keyword | 0 sec | Results may vary based on detection |

---

## Error Handling

### Empty Query
```
User: "@theo_bot_username"
Response: "Type a category (hope, peace, faith, etc.) or scripture reference"
```

### Invalid Category
```
User: "@theo invalid_category"
Response: Shows available categories as suggestion
```

### Failed Verse Lookup
```
User: "@theo John 99:99" (invalid reference)
Response: Silently returns empty results
```

---

## Limits & Considerations

| Aspect | Limit | Note |
|--------|-------|------|
| Results per query | 5 verses | Telegram inline default |
| Query length | 256 characters | Telegram limit |
| Result title | verse reference | e.g., "John 3:16" |
| Result description | 100 chars | Verse preview |
| Buttons per result | 3 | Save, Next, Share |

---

## Testing the Feature

### Quick Test Checklist

- [ ] Open a Telegram group or channel
- [ ] Type: `@iamtheobot hope`
- [ ] Verify 5 hope verses appear
- [ ] Click one verse → posts to chat
- [ ] Click "Next" button → shows different verse
- [ ] Click "Save" button → confirmation message
- [ ] Try reference: `@iamtheobot John 3:16`
- [ ] Try keyword: `@iamtheobot peace verses`

### Expected Behaviors

✅ Results appear instantly  
✅ Works in private chats, groups, channels  
✅ Buttons work and edit/save correctly  
✅ Category variations work (e.g., "hope", "hope verses", "hope scripture")  
✅ Reference aliases work (e.g., "jhn 3:16", "john 3:16")  

---

## Troubleshooting

### Issue: Inline queries not working

**Solution 1**: Verify BotFather inline mode is enabled
```
/mybots → select bot → /inline → Enable
```

**Solution 2**: Verify polling includes `inline_query`
- Check [main.py](theo/app/main.py) line ~126
- Should include: `"inline_query"` in allowed_updates

**Solution 3**: Restart the bot
```bash
# Stop the bot
Ctrl+C

# Start again
python -m theo.app.main
```

### Issue: Results show only error message

**Check logs** for:
- Category not found in config
- API failure to fetch verses
- Invalid query format

---

## Future Enhancements

- [ ] Keyword search across verse content (not just category names)
- [ ] Verse history integration
- [ ] User translation preference in inline results
- [ ] Randomize Next button to show truly different verses
- [ ] Add category filters as inline keyboard options
- [ ] Support for verse ranges (e.g., "John 3:16-18")

---

## Integration With Existing Features

### Callback System ✅
Inline results use the same callback pattern as command-based verses:
- `verse|save|category|reference`
- `verse|another|category|reference`
- `verse|forward`

### History Logging ✅
Inline verse clicks are logged to user history (private chats only)

### Translation Support ✅
Inline results respect user's translation preference

### Category Detection ✅
Uses existing `detect_category()` service

---

## Support

For issues or questions about the inline query feature:
- Check logs: `theo/app/logging_setup.py`
- Review handler: [verse.py](theo/adapters/telegram/handlers/verse.py)
- See guide: This file

---

**Status**: Ready for production  
**Last Updated**: April 28, 2026  
**Contributor**: Theo Development Team
