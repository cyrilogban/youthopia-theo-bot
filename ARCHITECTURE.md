# Architecture

## Current Design

Theo uses a layered architecture with clear separation of concerns:

- **App Layer (`theo/app`)** -> startup, config loading, logging, dependency wiring
- **Adapter Layer (`theo/adapters`)** -> Telegram handlers, routing, and response rendering
- **Core Layer (`theo/core`)** -> business logic (verse retrieval, scheduling flow, category/reference detection, translations)
- **Infrastructure Layer (`theo/infra`)** -> persistence (MongoDB), scheduler (APScheduler), cache, and Supabase verse repository
- **Main Entrypoint (`theo/app/main.py`)** -> composes all layers and starts polling

---

## Container Decision (Important)

There are two ways to structure runtime dependencies.

### Option B (Not used)

- Store Telegram bot instance inside the container
- Access as `container.bot`

Problems:

- Couples container to Telegram implementation
- Makes adapter changes harder if Telegram library changes

---

### Option A (Chosen)

The container stores infrastructure dependencies only.

- `container.py` -> settings + `group_repo`
- `main.py` -> creates `TeleBot`
- `schedule_service.py` -> accepts both `container` and `bot`

Example:

```python
start_scheduler(lambda: daily_job(container, bot))
```

This keeps infrastructure independent from Telegram-specific runtime objects.

---

## Persistence and Data Sources

Theo uses two data stores with different responsibilities.

### MongoDB (chat state, subscriptions, preferences)

Used via `MongoGroupRepo` behind the `GroupRepo` contract.

Responsibilities:

- Store chats/groups that interacted with Theo
- Track daily VOTD enable/disable state per chat
- Store chat metadata (title)
- Store selected translation per chat (e.g., `kjv`, `web`, `bbe`, `asv`)

Why:

- Simple document storage for chat-level state
- Clear repository abstraction for portability

---

### Supabase (scripture references, user data, and history logging)

Used via `supabase_verse_repo`, `supabase_user_repo`.

Responsibilities:

**Scripture Metadata:**
- Category catalog (`categories`)
- Verse references by category (`verses`) using structured fields:
  - `book`
  - `chapter`
  - `verse`
- Daily VOTD logging and non-repetition cycle (`votd_log`)

**User Persistence:**
- User profiles (`users`): telegram_id, first_name, username, tone_preference, translation, created_at
- Saved verses (`saved_verses`): user-curated favorites with user_id, book, chapter, verse, category, saved_at

**Verse History Logging:**
- Complete delivery log (`verse_history`): user_id, book, chapter, verse, category, delivery_path, translation, delivered_at
- Tracks all 5 delivery paths: votd, category_command, category_text_detect, reference_auto_detect, next_button
- Private DM only (groups excluded for privacy)
- Enables user history review and future personalization

VOTD category mapping is weekday-based:

- Monday -> `faith`
- Tuesday -> `love`
- Wednesday -> `peace`
- Thursday -> `joy`
- Friday -> `hope`
- Saturday -> `patience`
- Sunday -> `forgiveness`

---

## Verse Retrieval Pipeline

1. Category is determined (explicit command, detected user request, or VOTD mapping)
2. Verse reference candidates are loaded from Supabase
3. One reference is selected (with optional exclusion to avoid immediate repeat)
4. Verse text is fetched live from Bible API (`https://bible-api.com/`)
5. Response is formatted for Telegram HTML quote style
6. Translation is applied per chat preference (fallback default: `kjv`)

Notes:

- Verse text is not stored locally
- Retrieval retries are applied on transient failures
- Multi-verse references are normalized and formatted safely

---

## Scheduling Flow

Scheduler:

- APScheduler background cron
- Runs daily at **06:00 Africa/Lagos**

Job flow:

1. Load all enabled chats from MongoDB
2. Resolve the day's VOTD category
3. Select/resolve today's shared verse reference
4. Fetch verse text (translation-aware per chat)
5. Deliver message to each enabled chat (DM or group context)

---

## Telegram Interaction Flow

### Command-driven

- `/start`, `/help`
- `/verse` (+ optional category argument)
- Dedicated category commands: `/faith`, `/love`, `/peace`, `/joy`, `/hope`, `/patience`, `/forgiveness`
- Subscription controls: `/enable_votd`, `/disable_votd`, `/status`
- Translation controls: `/translation`

### Passive detection

- Category request detection from plain text
- Scripture reference detection in normal messages (e.g., `John 3:16`, `Psalm 23:1-6`)

---

## Runtime Components

- `pyTelegramBotAPI` for bot runtime and handlers
- `APScheduler` for daily VOTD cron
- `Flask` keep-alive endpoint (`0.0.0.0:$PORT`) for hosted environments
- `requests` for Bible API calls
- `pymongo` + `certifi` for MongoDB persistence
- `supabase` client for category/reference storage and VOTD logs

---

## Error Handling Principles

- Retry external verse fetches
- Fallback to alternate verse candidates when needed
- Guard unknown categories gracefully
- Never crash polling loop on handler/job errors
- Log failures with context for operational debugging

---

## Design Principles

- Keep adapters thin and platform-specific
- Keep core services pure and reusable
- Keep infrastructure replaceable behind contracts
- Keep output intentional, structured, and consistent
