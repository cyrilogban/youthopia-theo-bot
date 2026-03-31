# Theo Bot

Theo is a Telegram bot that sends Bible verses to groups.

## Current Features
- Group registration
- Enable / Dsable VOTD(Verse of the Day)
- Scheduler (currently runs every minute for testing)
- Send VOTD(Verse of the Day) to enabled groups.

## Tech Stack
- Python
- TeleBot (Telegram API)
- MongoDB
- APScheduler

## Project Structure
- `main.py` → application entry point
- `container.py` → dependency container (settings + database)
- `schedule_service.py` → scheduler logic
- `router.py` → Telegram handlers

## Next Features
- Fetch real Bible verses from API
- Daily scheduled time (e.g. 6AM)
- Verse formatting
- Bible version selection