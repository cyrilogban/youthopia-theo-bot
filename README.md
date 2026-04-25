# Theo

Theo is a Telegram Bible bot built for the YouThopia Bible Community. It delivers daily scripture, translation-aware responses, and automatic Bible reference detection for both private chats and groups.

## Highlights

- Daily Verse of the Day (VOTD) delivery at 6:00 AM Africa/Lagos
- VOTD rotates by day of the week across 7 categories
- No verse repeats within a category until all verses are exhausted
- Automatic Bible reference detection in chat messages
- Translation support for `KJV`, `WEB`, `BBE`, and `ASV`
- Group and DM subscription support
- Persistent user registration via Supabase
- Telegram-friendly scripture formatting with quote-style and expandable verse output
- Keep-alive HTTP endpoint for deployment environments that expect a bound port

## VOTD Day Rotation

Each day of the week maps to a different scripture category:

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

On Telegram, scripture is rendered as a native quote block. Longer or multi-line passages are sent as expandable quote blocks to keep chats clean. Every verse includes three action buttons: Save, Next, and Share.

## Tech Stack

- Python
- `pyTelegramBotAPI`
- `requests`
- `pymongo`
- `supabase==2.10.0`
- `APScheduler`
- `Flask`
- `python-dotenv`
- `certifi`

## Project Structure

```text
theo/
|-- adapters/      # Telegram handlers, views, and bot wiring
|-- app/           # Startup, config, container, logging, keep-alive
|-- core/          # Business logic and services
|-- infra/         # MongoDB, Supabase, scheduler, and cache
`-- tests/         # Test suite
```

## Supabase Tables

| Table | Purpose |
|-------|---------|
| `categories` | Stores the 7 scripture categories |
| `verses` | Stores 210+ curated verse references |
| `votd_log` | Tracks daily verse delivery and prevents repeats |
| `users` | Stores registered users and their preferences |
| `user_memory` | Reserved for future memory and personalization features |
| `verse_history` | Reserved for future verse history tracking |

## Configuration

Theo reads configuration from a local `.env` file.

Required variables:

- `BOT_TOKEN` - Telegram bot token from BotFather
- `MONGO_URI` - MongoDB connection string
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon/public key

Optional variables:

- `MONGO_DB_NAME` - Database name, defaults to `theo`
- `PORT` - Used by the keep-alive HTTP server, defaults to `8080`

Minimal `.env` example:

```env
BOT_TOKEN=your-telegram-bot-token
MONGO_URI=your-mongodb-uri
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
MONGO_DB_NAME=theo
PORT=8080
```

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