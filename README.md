Spider-Man🕷️
# Telegram Bot Boilerplate

A clean, reusable starter template for building Telegram bots with Python.

## Stack
- Python
- pyTelegramBotAPI
- Flask (keep-alive server)
- MongoDB (subscriptions and settings)
- Supabase (structured data)
- APScheduler (scheduled tasks)
- Render (deployment)

## Quick Start

1. Click Use this template on GitHub
2. Clone the new repo
3. Run the setup script to create project structure:
   .\setup.ps1
4. Copy .env.example to .env and fill in your values
5. Create and activate a virtual environment:
   python -m venv .venv
   .venv\Scripts\Activate.ps1
6. Install dependencies:
   pip install -r requirements.txt
7. Run the bot:
   python -m bot.app.main

## Project Structure

bot/
+-- adapters/
�   +-- telegram/
�       +-- handlers/   # Command handlers
�       +-- views/      # Message formatters
+-- app/                # Startup, config, container
+-- core/
�   +-- services/       # Business logic
+-- infra/
�   +-- db/             # Database connections
�   +-- cache/          # Caching layer
�   +-- scheduler/      # Scheduled tasks
�   +-- http/           # Keep-alive server
+-- tests/              # Test suite

## Environment Variables

See .env.example for all required variables.

## Deployment

Designed for Render. The keep-alive server binds to 0.0.0.0:\.

Start command:
python -m bot.app.main
