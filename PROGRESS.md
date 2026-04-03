# Progress made So far.

## Current State
- Telegram bot is running with command handlers, inline actions, and daily scheduling
- Keep-alive HTTP server is wired into startup for hosting platforms that expect a bound port
- Daily VOTD is scheduled for 6:00 AM Africa/Lagos
- VOTD now works for both groups and DM subscriptions
- Daily VOTD now greets users by first name in DMs and greets groups by group title
- Category-based scripture flow is working
- Auto-detect scripture references in DMs and groups is working
- Translation system is wired through the live verse-delivery paths with `kjv` as default
- Scripture output now uses Telegram quote-style formatting
- Long or multi-line scripture output now uses expandable quote blocks
- HTML parse mode is applied only on scripture-delivery paths; the bot default still stays opt-in
- Supported translations are:
  - `kjv`
  - `web`
  - `bbe`
  - `asv`
- Enhanced welcome flow with today's VOTD in `/start` command
- First-time user tracking system operational (in-memory cache with 1-hour TTL)
- Group join welcome messages with VOTD verses
- Bot mention detection in groups (@iamtheobot tagging)
- Professional UI with compact emoji buttons (3 per row)
- Command menu configured and visible in Telegram
- Handler optimization: bot username cached at startup (not called per-message)

## Completed Features
- Wired `verse.py` into the Telegram router
- Added category scripture commands:
  - `/faith`
  - `/love`
  - `/peace`
  - `/joy`
  - `/hope`
  - `/patience`
  - `/forgiveness`
- Added `/verse` category browsing flow
- Removed `/scripture` from the command surface
- Added inline verse actions
- Replaced `Share Verse` with `Forward Verse`
- Fixed inline callback polling support
- Added category detection from plain user text
- Added Bible reference auto-detection for DMs and groups
- Added support for messy scripture input formats like:
  - `John 3:16`
  - `Jn 3:16`
  - `john 3vs16`
  - `JOHN 3 VS 16`
  - `John 3:1-20`
- Added support for multiple scripture references in one message
- Added numbered formatting for extended verse ranges
- Added DM subscription support for daily VOTD
- Added `/translation` command
- Added translation persistence to storage
- Wired saved translation into:
  - category scripture replies
  - auto-detected scripture replies
  - daily VOTD delivery
- Wired keep-alive startup into `main.py`
- Verse output now shows translation labels like `(KJV)` 
- Verse output now renders as Telegram blockquotes instead of plain quoted text 
- Added expandable scripture formatting for long and multi-verse output 
- Kept global bot parse mode unchanged and applied HTML only to scripture sends/edits
- Daily VOTD now includes a personalized greeting before the verse

## Recently Completed (Session 2)
- **Enhanced Welcome Flow**: `/start` command now delivers today's VOTD with category buttons
- **First-Time User Tracking**: Implemented in-memory cache (`FirstTimeUserCache`) with TTL tracking
- **Group Join Welcome**: Bot sends welcome message with VOTD when added to groups
- **Bot Mention Detection**: Implemented dynamic username detection for group tagging (@iamtheobot)
- **Professional Button UI**: Created compact emoji button design (3 per row, removed forgiveness category)
- **Command Menu Setup**: Configured visible command menu in Telegram (/start, /verse, /enable_votd, /translation, /help)
- **Handler Optimization**: Cached bot username at startup to eliminate per-message API calls
- **Security Audit**: Identified and documented 10 security vulnerabilities (saved to SECURITY_AUDIT.md)

## Storage / Data Progress
- `verses.json` is the source of truth for category scripture and VOTD category
- Chat records now store:
  - `chat_id`
  - `title`
  - `enabled`
  - `translation`
- Old records safely fall back to `kjv`

## Testing Progress
- Existing tests still cover category detection and verse service basics
- Added parser test file:
  - `test_reference_detection_service.py`
- Added verse-formatting coverage for:
  - standard Telegram blockquote rendering
  - expandable blockquote rendering for long or multi-line scripture
  - HTML escaping in scripture output
- Automated verification from terminal has been limited by local Python / PowerShell environment issues
- Live Telegram testing is still important for validation

## Current Commands
- `/verse` - Browse scripture
- `/translation` - Change translation
- `/enable_votd` - Subscribe to daily verses
- `/disable_votd` - Stop daily verses
- `/status` - Check subscription status

## Current Limitations
- AI reflection feature is not implemented yet
- Mindset prompt has been intentionally dropped for now
- Translation preference now exists and is wired into live delivery, but broader live validation is still needed
- Group-specific timezone scheduling is not implemented yet
- Some tests still need to be expanded for translation-aware flows and scheduler behavior
- Quote-style rendering still needs live validation across Telegram clients
- Security vulnerabilities identified (see SECURITY_AUDIT.md for details)

## Next Steps
- Implement AI reflection generation only
- Add translation-aware tests
- Live-verify Telegram quote and expandable scripture rendering
- Decide whether group translation should stay shared per chat or become more advanced later
- Design timezone-aware delivery for global scaling

## Potential Features

I hope to add the following features to Theo:

- **AI Reflection**
  Add a short human reflection after each verse that feels grounded, specific, and not generic.

- **Prayer Mode**
  Let users say things like `pray for me`, `I feel anxious`, or `I need strength`, and return:
  - a fitting verse
  - a short prayer
  - a gentle reflection

- **Mood / Need Check-ins**
  Add a simple flow like:
  - `How are you feeling today?`
  - `Anxious`
  - `Tired`
  - `Hopeful`
  - `Confused`
  Then match the user to scripture more personally.

- **Saved Preferences**
  Expand personalization beyond translation to include:
  - preferred delivery time
  - quiet hours
  - preferred tone
  - favorite categories

- **Prayer Journal / Saved Requests**
  Let users save prayer requests and come back later:
  - `Add prayer request`
  - `My prayer list`
  - `Answered prayers`

- **Follow-up Scripture**
  After a user gets a verse today, the bot can follow up tomorrow:
  - `Yesterday you asked for hope. Here is another verse for today.`

- **Favorites / Save Verse**
  Let users save verses they love:
  - `Save this verse`
  - `My saved verses`
  - `Send me one of my saved verses`

- **Scripture Companion Mode**
  Instead of only replying to commands, the bot can answer:
  - `I feel overwhelmed`
  - `I can't forgive someone`
  - `I need peace`
  Then detect the need and respond with verse + reflection.

- **Reading Plans**
  Add short plans like:
  - `3-day peace plan`
  - `7-day hope plan`
  - `forgiveness journey`

- **Weekly Spiritual Recap**
  In DMs, send something like:
  - top category the user asked for this week
  - one reflective question
  - one verse for the week ahead

- **Group Personalization**
  For groups, make VOTD feel community-based:
  - use group name
  - optional prayer prompt for the group
  - weekly group scripture theme

- **Shareable Devotional Cards**
  Turn verses into clean shareable text/card outputs for Telegram forwarding and status posting.

## Suggested Priority

1. AI reflection only
2. Mood / need check-in flow
3. Prayer mode
4. Favorites / saved verses
5. Reading plans

## Bugs / Watchlist
- Need live verification after major wiring because terminal-based automated checks have been limited
- Monitor group privacy settings for auto-detect behavior in groups
- All welcome flows should be tested after handler optimization:
  - `/start` in DM
  - First message in DM
  - Group join
  - Group mention (@botname)
- Security vulnerabilities from audit should be addressed before production deployment

