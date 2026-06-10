"""Telegram bot command and message handlers."""

import logging

import aiohttp
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from bot.api import fetch_rates, format_rates_message

logger = logging.getLogger(__name__)

router = Router()

# ─── Keyboard ──────────────────────────────────────────────────────────────────

RATES_BUTTON_TEXT = "Дізнатися курс валют"

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=RATES_BUTTON_TEXT)]],
    resize_keyboard=True,
    one_time_keyboard=False,
)


# ─── Handlers ──────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """/start command — greet the user and show the main keyboard."""
    await message.answer(
        "👋 Вітаю! Я бот для перегляду курсів валют.\n\n"
        "Натисніть кнопку нижче, щоб дізнатися актуальний курс USD та EUR до гривні.",
        reply_markup=main_keyboard,
    )


@router.message(lambda msg: msg.text == RATES_BUTTON_TEXT)
async def handle_rates_button(message: Message) -> None:
    """Handle the 'Дізнатися курс валют' reply button press."""
    async with aiohttp.ClientSession() as session:
        try:
            rates = await fetch_rates(session)
            text = format_rates_message(rates)
        except aiohttp.ClientError as exc:
            logger.error("Network error while fetching rates: %s", exc)
            text = "⚠️ Не вдалося з'єднатися з сервером. Спробуйте пізніше."
        except ValueError as exc:
            logger.error("Parsing error: %s", exc)
            text = "⚠️ Не вдалося обробити дані від банку. Спробуйте пізніше."

    await message.answer(text, parse_mode="HTML")
