"""Tests for bot.handlers — /start and rates-button handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bot.handlers import handle_start, handle_rates_button, RATES_BUTTON_TEXT


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_message(text: str = "") -> MagicMock:
    """Create a minimal fake aiogram Message object."""
    message = MagicMock()
    message.text = text
    message.answer = AsyncMock()
    return message


# ─── /start handler ────────────────────────────────────────────────────────────

class TestHandleStart:
    """Tests for the /start command handler."""

    async def test_sends_a_reply(self):
        message = _make_message()
        await handle_start(message)
        message.answer.assert_called_once()

    async def test_reply_contains_greeting(self):
        message = _make_message()
        await handle_start(message)
        call_kwargs = message.answer.call_args
        text_arg = call_kwargs.args[0] if call_kwargs.args else ""
        assert "Вітаю" in text_arg

    async def test_reply_mentions_usd_eur(self):
        message = _make_message()
        await handle_start(message)
        call_kwargs = message.answer.call_args
        text_arg = call_kwargs.args[0] if call_kwargs.args else ""
        assert "USD" in text_arg or "EUR" in text_arg

    async def test_reply_includes_keyboard(self):
        """The start handler must attach a reply keyboard."""
        message = _make_message()
        await handle_start(message)
        _, kwargs = message.answer.call_args
        assert "reply_markup" in kwargs


# ─── Rates-button handler ──────────────────────────────────────────────────────

MOCK_RATES = {
    "USD": {"buy": 41.5, "sell": 42.0},
    "EUR": {"buy": 44.8, "sell": 45.5},
}


class TestHandleRatesButton:
    """Tests for the 'Дізнатися курс валют' reply-button handler."""

    async def test_sends_html_message_on_success(self, mocker):
        """On successful API call the handler must reply with HTML parse_mode."""
        mocker.patch("bot.handlers.fetch_rates", return_value=MOCK_RATES)
        message = _make_message(RATES_BUTTON_TEXT)

        await handle_rates_button(message)

        message.answer.assert_called_once()
        _, kwargs = message.answer.call_args
        assert kwargs.get("parse_mode") == "HTML"

    async def test_message_contains_usd(self, mocker):
        mocker.patch("bot.handlers.fetch_rates", return_value=MOCK_RATES)
        message = _make_message(RATES_BUTTON_TEXT)

        await handle_rates_button(message)

        text = message.answer.call_args.args[0]
        assert "USD" in text

    async def test_message_contains_eur(self, mocker):
        mocker.patch("bot.handlers.fetch_rates", return_value=MOCK_RATES)
        message = _make_message(RATES_BUTTON_TEXT)

        await handle_rates_button(message)

        text = message.answer.call_args.args[0]
        assert "EUR" in text

    async def test_network_error_sends_user_friendly_message(self, mocker):
        """aiohttp.ClientError must be caught and a friendly message returned."""
        import aiohttp

        mocker.patch(
            "bot.handlers.fetch_rates",
            side_effect=aiohttp.ClientError("connection refused"),
        )
        message = _make_message(RATES_BUTTON_TEXT)

        await handle_rates_button(message)

        message.answer.assert_called_once()
        text = message.answer.call_args.args[0]
        assert "⚠️" in text

    async def test_value_error_sends_user_friendly_message(self, mocker):
        """ValueError from the parser must be caught and a friendly message returned."""
        mocker.patch(
            "bot.handlers.fetch_rates",
            side_effect=ValueError("rates not found"),
        )
        message = _make_message(RATES_BUTTON_TEXT)

        await handle_rates_button(message)

        message.answer.assert_called_once()
        text = message.answer.call_args.args[0]
        assert "⚠️" in text

    async def test_always_sends_exactly_one_message(self, mocker):
        """Handler must send exactly one message regardless of outcome."""
        mocker.patch("bot.handlers.fetch_rates", return_value=MOCK_RATES)
        message = _make_message(RATES_BUTTON_TEXT)

        await handle_rates_button(message)

        assert message.answer.call_count == 1
