# Inline Query Feature - Quick Reference

## What Was Added

**Inline Bible verse search** - Users type `@theo_bot` to search verses inline without using `/commands`

---

## How Users Use It

```
User types in ANY chat:  @iamtheobot hope
                         ↓
Bot returns:     Up to 5 hope verses with previews
                         ↓
User clicks verse → Posted to that chat
                         ↓
User can Save, Get Next verse, or Share
```

---

## Query Types Supported

| Query | Format | Result |
|-------|--------|--------|
| **Category** | `@iamtheobot hope` | 5 hope verses |
| **Reference** | `@iamtheobot John 3:16` | That verse |
| **Keyword** | `@iamtheobot peace verses` | Peace category verses |

**Categories**: faith, love, peace, joy, hope, patience, forgiveness

---

## Files Changed

| File | Change |
|------|--------|
| `theo/adapters/telegram/handlers/verse.py` | Added inline query handler (8 functions) |
| `theo/app/main.py` | Added `"inline_query"` to polling updates |
| `INLINE_QUERY_GUIDE.md` | (NEW) Full documentation |
| `BOTFATHER_SETUP.md` | (NEW) Setup instructions |

---

## One-Time Setup (Via BotFather)

```
Open Telegram → Search @BotFather
Send: /mybots → Select your bot
Send: /inline → Click "ON"
Restart bot
Done! ✅
```

---

## Implementation Details

### Query Parser
- Detects if user typed a **category** ("hope"), **reference** ("John 3:16"), or **keyword** ("peace verses")
- Uses existing category detection service
- Uses regex to validate reference pattern

### Result Builder
- Returns up to **5 verses** with previews
- Each verse has 3 buttons: **💾 Save | ➡️ Next | 📤 Share**
- Buttons use same callback pattern as existing `/verse` command
- Works in private chats, groups, and channels

### Caching
- **Category/keyword**: No cache (live results)
- **Reference**: 1-hour cache (API optimization)

### Error Handling
- Invalid category → Shows suggestions
- No verses found → Fallback help message
- API failure → Silent retry

---

## Testing

```bash
# 1. Start bot
python -m theo.app.main

# 2. Open Telegram, any chat
# 3. Type: @iamtheobot hope
# 4. Click result → verse posts

✅ If verses appear → Working!
```

---

## Key Features

✅ Works in groups and channels  
✅ No `/commands` needed  
✅ Save verses to collection  
✅ Navigate with Next button  
✅ Respects user translation preference  
✅ Instant results as you type  

---

## What to Tell Users

> "You can now search Bible verses inline! Just type `@iamtheobot` followed by a category like `hope`, `peace`, `faith`, or `love`. You can also search specific verses like `John 3:16`. Try it in any chat!"

---

## Architecture

```
@bot.inline_handler()
        ↓
_inline_query_handler() 
        ↓
_parse_inline_query() → (category|reference|keyword)
        ↓
Routes to:
  - _handle_inline_query_category()
  - _handle_inline_query_reference()
  - _handle_inline_query_keyword()
        ↓
Returns: List[InlineQueryResultArticle]
        ↓
User sees results and clicks
        ↓
Verse posted to chat
```

---

## Status

✅ **Implementation**: Complete  
✅ **Testing**: Ready  
✅ **Syntax**: Valid  
✅ **Errors**: None  
✅ **Documentation**: Complete  

---

**Ready to deploy!** Enable inline mode in BotFather, restart the bot, and you're done. 🚀
