# Theo

Theo is a Telegram Bible bot built for the YouThopia Bible Community. It delivers daily scripture, translation-aware responses, automatic Bible reference detection, and comprehensive verse history tracking for both private chats and groups.

## Key Features

### Scripture Delivery (5 Paths)
- **Daily Verse of the Day (VOTD)** - 6:00 AM Africa/Lagos with personalized greetings
- **Category Commands** - `/faith`, `/love`, `/peace`, `/joy`, `/hope`, `/patience`, `/forgiveness`
- **Category Detection** - "I need hope" detects category automatically
- **Bible Reference Auto-Detection** - "John 3:16" or "Psalm 23:1-5" auto-fetched
- **Interactive Browsing** - "Next" button for category browsing

### User Profile & Preferences
- **My Profile** - View user details, preferences, and membership date
- **Saved Verses** - User-curated favorite scriptures
- **Verse History** - Complete log of all delivered verses with context
- **Translation Preferences** - Choose between KJV, WEB, BBE, ASV
- **Tone Preferences** - Upcoming personalization feature

### Technical Features
- Daily VOTD rotates by weekday across 7 categories (no repeats within category until exhausted)
- Translation-aware delivery across all 5 verse paths
- Telegram-native quote formatting with expandable blocks for long passages
- Group and DM subscription support with admin-only controls
- Persistent user registration and preferences via Supabase
- Keep-alive HTTP endpoint for deployment environments
- Automatic group welcome messages with VOTD
- Bot mention detection in groups (@iamtheobot)

## VOTD Weekday Rotation

| Day | Category |
|-----|----------|
| Monday | Faith |
| Tuesday | Love |
| Wednesday | Peace |
| Thursday | Joy |
| Friday | Hope |
| Saturday | Patience |
| Sunday | Forgiveness |

## Example Output

```text
John 14:27 (KJV)

Peace I leave with you, my peace I give unto you...
```

On Telegram, scripture is rendered as a native quote block. Longer or multi-line passages are sent as expandable quote blocks to keep chats clean. Every verse includes action buttons: Save, Next, and Share.

## Verse History Feature

Users can view their complete verse history in the Profile menu:
- Displays last 20 delivered verses
- Shows full verse text for each entry
- Includes metadata: category, delivery path, translation used
- Tracks 5 delivery paths: VOTD, category_command, category_text_detect, reference_auto_detect, next_button
- Only tracks private DM history (groups excluded for privacy)

## Tech Stack

- Python 3.9+
- `pyTelegramBotAPI` - Telegram bot runtime
- `requests` - HTTP library for Bible API
- `pymongo` - Chat state and subscriptions
- `supabase==2.10.0` - Scripture references and user data
- `APScheduler` - Daily VOTD scheduling
- `Flask` - Keep-alive HTTP server
- `python-dotenv` - Configuration management
- `certifi` - SSL certificate handling

## Project Structure

```text
theo/
├── adapters/           # Telegram handlers, views, keyboards, rendering
│   └── telegram/
│       ├── handlers/   # /profile, /verse, /groups, /autodetect, /start, /help, /autoregister
│       └── views/      # keyboards.py, render.py
├── app/                # Startup, config, container, logging, keep-alive
├── core/               # Business logic services
│   ├── models/         # Data structures (events, responses, state)
│   ├── policies/       # Permissions and validation
│   └── services/       # category_detection, reference_detection, schedule, subscription, translation, verse
├── infra/              # Infrastructure layer
│   ├── supabase_*      # Verse repo, user repo, client
│   ├── db/             # MongoDB repo, repo contract, mock
│   ├── cache/          # Memory cache
│   ├── http/           # Health server
│   └── scheduler/      # APScheduler setup
└── tests/              # Service tests
```

## Supabase Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `categories` | Scripture categories | id, name |
| `verses` | Curated verse references | id, category_id, book, chapter, verse |
| `votd_log` | Daily VOTD tracking | verse_date, category, book, chapter, verse |
| `users` | User profiles and preferences | telegram_id, first_name, username, tone_preference, translation, created_at |
| `saved_verses` | User-curated favorites | user_id, book, chapter, verse, category, saved_at |
| `verse_history` | All delivered verses log | user_id, book, chapter, verse, category, delivery_path, translation, delivered_at |

## Configuration

Theo reads configuration from a local `.env` file.

**Required variables:**
- `BOT_TOKEN` - Telegram bot token from BotFather
- `MONGO_URI` - MongoDB connection string
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon/public key

**Optional variables:**
- `MONGO_DB_NAME` - Database name (default: `theo`)
- `PORT` - Keep-alive HTTP server port (default: `8080`)

**Minimal `.env` example:**
```env
BOT_TOKEN=your-telegram-bot-token
MONGO_URI=your-mongodb-uri
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
MONGO_DB_NAME=theo
PORT=8080
```

## Commands

- `/start` - Welcome message with today's VOTD
- `/verse` - Browse scriptures by category
- `/faith`, `/love`, `/peace`, `/joy`, `/hope`, `/patience`, `/forgiveness` - Category shortcuts
- `/enable_votd` - Subscribe to daily VOTD (DM) or enable for group (admin only)
- `/disable_votd` - Unsubscribe from VOTD
- `/status` - Check subscription status
- `/translation` - View or change translation preference
- `/profile` - View user profile and preferences
- `/help` - Show command help

## Supported Translations

- `KJV` - King James Version
- `WEB` - World English Bible
- `BBE` - Bible in Basic English
- `ASV` - American Standard Version

## Local Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Create a `.env` file with your credentials.
5. Run the bot.

```powershell
pip install -r requirements.txt
python -m theo.app.main
```

## Telegram Commands

- `/start` - Onboarding flow with today's Verse of the Day
- `/help` - Help and available commands
- `/enable_votd` - Subscribe to daily verse delivery
- `/disable_votd` - Unsubscribe from daily verse delivery
- `/status` - Check subscription status
- `/translation` - View or change Bible translation

## How It Works

Theo is structured with clear separation of concerns:

- `app/` boots the application and wires dependencies together
- `adapters/telegram/` handles Telegram-specific input and output
- `core/services/` contains scripture lookup, scheduling, translation, and detection logic
- `infra/` manages MongoDB persistence, Supabase queries, scheduling, and caching

Scripture references typed in chat like `John 3:16` or `Psalm 23:1-6` are automatically detected and fetched in both DMs and groups. Live verse text is always fetched from the Bible API to support all four translations.

## Deployment Notes

Theo runs on Render. The built-in keep-alive server binds to `0.0.0.0:$PORT`.

Start command:

```text
python -m theo.app.main
```

## Roadmap

- Saved verses feature
- User profile command
- AI-generated verse reflections
- Prayer mode
- Reading plans
- Semantic verse search with Pinecone
- Mood and need-based scripture matching

## Contributing

Contributions are welcome. If you want to improve Theo:

1. Create a feature branch
2. Make focused changes
3. Test your work
4. Open a pull request with a clear summary

## Project Direction

Theo is meant to feel intentional, spiritually grounded, and useful in real conversations. The goal is not just to return Bible text, but to create a dependable scripture companion for the YouThopia community.