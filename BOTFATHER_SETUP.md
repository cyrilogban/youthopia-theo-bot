# Inline Query Setup - BotFather Configuration

## Quick Setup (5 minutes)

This guide shows how to enable **Inline Mode** for your Theo bot in Telegram.

---

## Step-by-Step Setup

### Step 1: Open BotFather

1. Open Telegram
2. Search for: `@BotFather`
3. Click "Start"

### Step 2: Select Your Bot

Send to BotFather: `/mybots`

```
BotFather shows list of your bots:
- theo_bot
- other_bots
```

Click on **theo_bot** (or your bot name)

### Step 3: Enable Inline Mode

BotFather shows bot menu. Send: `/inline`

```
BotFather shows:
  Current inline query messages: off
  
  Turn inline query handler on or off
```

Click **"ON"** to enable inline mode

---

## Verification

Once enabled, you should see in BotFather:

```
✅ Inline query handler: ON
```

---

## Testing

1. **Open any Telegram chat** (group or private)
2. **Type**: `@iamtheobot hope`
3. **Verify**: Inline verse suggestions appear

If you see suggestions, ✅ **Inline mode is working!**

---

## If It Doesn't Work

### Check 1: Bot has inline handler
```python
# This is already in verse.py:
@bot.inline_handler()
def _inline_query_handler(inline_query):
    # ...
```

### Check 2: Polling includes inline_query
```python
# This is already in main.py:
allowed_updates=["message", "callback_query", ..., "inline_query"]
```

### Check 3: Bot is running
```bash
python -m theo.app.main
# Should show: "Theo v2 starting polling..."
```

### Check 4: Restart bot after config change
```bash
# Stop bot
Ctrl + C

# Start bot again
python -m theo.app.main
```

---

## Common Issues

### Issue: "This bot can't be used inline"

**Solution**: Go back to BotFather `/inline` and enable it again

### Issue: Results don't appear

**Solution 1**: Verify polling config has `inline_query`  
**Solution 2**: Restart the bot  
**Solution 3**: Check bot logs for errors

### Issue: Empty results

**Solution**: Check bot is responding with verses for regular `/verse` command first

---

## After Setup

Your Theo bot now supports three ways to get verses:

| Method | Format |
|--------|--------|
| **Inline** | `@iamtheobot hope` |
| **Command** | `/verse` then select category |
| **Reference** | `@iamtheobot John 3:16` |

---

## What's Enabled Now

✅ Users can search verses inline  
✅ Results appear as you type  
✅ Click to post verse to any chat  
✅ Works in groups and channels  
✅ Buttons: Save, Next, Share  

---

**That's it!** Your Theo bot now has inline verse search. 🎉
