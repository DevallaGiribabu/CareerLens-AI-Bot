
"""Compatibility entry point for the CareerLens Telegram bot."""

from app.bot.main import (
    SESSION_DATA,
    analyze,
    handle_document,
    help_command,
    main,
    reset_session,
    start,
)

__all__ = [
    "SESSION_DATA",
    "analyze",
    "handle_document",
    "help_command",
    "main",
    "reset_session",
    "start",
]


if __name__ == "__main__":
    main()
