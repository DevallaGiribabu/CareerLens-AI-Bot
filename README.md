# CareerLens AI

CareerLens AI is a Telegram-based resume-to-job-description analyzer built in Python.

## Project structure

- app/bot: Telegram bot entrypoint
- app/parsers: PDF-to-text extraction
- app/config: environment configuration
- data/uploads: temporary upload storage

## Quick start

1. Create a virtual environment:
   python -m venv venv
2. Activate it:
   venv\Scripts\activate
3. Install dependencies:
   pip install -r requirements.txt
4. Copy environment variables:
   copy .env.example .env
5. Add your Telegram bot token in .env
6. Run the bot:
   python -m app.bot.main

## Current milestone

This version supports:
- /start
- /help
- /analyze
- resume PDF upload
- JD PDF upload
- text extraction from uploaded PDFs
- resume and job-description skill matching
- weighted match score and skill-gap suggestions
- certification recommendations

## Notes

This is the first MVP step. It does not yet include AI scoring, structured extraction, or database storage.
