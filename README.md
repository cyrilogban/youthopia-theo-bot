# Theo

Theo is a Telegram Bible bot built for the YouThopia Bible Community. It delivers daily scripture, category-based verse lookup, translation-aware responses, and automatic Bible reference detection for both private chats and groups.

## Highlights

- Daily Verse of the Day delivery at 6:00 AM Africa/Lagos
- Category-based scripture commands for:
  - `faith`
  - `love`
  - `peace`
  - `joy`
  - `hope`
  - `patience`
  - `forgiveness`
- Automatic Bible reference detection in chat messages
- Translation support for `KJV`, `WEB`, `BBE`, and `ASV`
- Group and DM subscription support
- Telegram-friendly scripture formatting with quote-style and expandable verse output
- Keep-alive HTTP endpoint for deployment environments that expect a bound port

## Current Feature Set

Theo currently supports:

- `/start` onboarding flow with today's Verse of the Day
- `/verse` category browsing and direct category lookup
- Dedicated category commands such as `/hope` and `/peace`
- `/enable_votd`, `/disable_votd`, and `/status`
- `/translation` for changing Bible versions per chat
- Automatic detection of references like `John 3:16` or `Psalm 23:1-6`
- Daily scheduled VOTD delivery to subscribed chats

## Example Output

```text
John 14:27 (KJV)

<blockquote>Peace I leave with you, my peace I give unto you...</blockquote>
```

On Telegram, scripture is rendered as a native quote block. Longer or multi-line passages are sent as expandable quote blocks to keep chats clean.

## Tech Stack

- Python
- `pyTelegramBotAPI`
- `requests`
- `pymongo`
- `supabase`
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
|-- data/          # Static verse configuration
|-- infra/         # MongoDB, scheduler, and cache implementations
`-- tests/         # Test suite
```

## Configuration

Theo reads configuration from a local `.env` file.

Required variables:

- `BOT_TOKEN` - Telegram bot token from BotFather
- `MONGO_URI` - MongoDB connection string
- `SUPABASE_URL` - Supabase project URL for verse/category data
- `SUPABASE_KEY` - Supabase API key for verse/category access

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
4. Create a `.env` file with your bot token and MongoDB URI.
5. Run the bot.

```powershell
pip install -r requirements.txt
python -m theo.app.main
```

## Telegram Commands

Core commands:

- `/start`
- `/help`
- `/verse`
- `/status`
- `/enable_votd`
- `/disable_votd`
- `/translation`

Category commands:

- `/faith`
- `/love`
- `/peace`
- `/joy`
- `/hope`
- `/patience`
- `/forgiveness`

## How It Works

Theo is structured with clear separation of concerns:

- `app/` boots the application and wires dependencies together
- `adapters/telegram/` handles Telegram-specific input and output
- `core/services/` contains scripture lookup, scheduling, translation, and detection logic
- `infra/` manages MongoDB persistence, caching, and the scheduler
- Supabase tables (`categories`, `verses`, and `votd_log`) are the source of truth for scripture categories, references, and daily VOTD rotation

The bot fetches live verse text from the Bible API rather than storing full verse text locally.

VOTD category is selected by weekday mapping:

- Monday: `faith`
- Tuesday: `love`
- Wednesday: `peace`
- Thursday: `joy`
- Friday: `hope`
- Saturday: `patience`
- Sunday: `forgiveness`

## Deployment Notes

Theo can run on platforms like Render. The built-in keep-alive server binds to `0.0.0.0:$PORT`, which helps when deploying to environments that expect an HTTP service.

Start command:

```text
python -m theo.app.main
```

## Roadmap

Planned improvements include:

- AI-generated reflections
- Prayer-oriented flows
- Deeper personalization
- Reading plans
- Saved verses and prayer requests
- Broader production hardening and validation

## Contributing

Contributions are welcome. If you want to improve Theo:

1. Create a feature branch
2. Make focused changes
3. Test your work
4. Open a pull request with a clear summary

## Project Direction

Theo is meant to feel intentional, spiritually grounded, and useful in real conversations. The goal is not just to return Bible text, but to create a dependable scripture companion for the YouThopia community.
