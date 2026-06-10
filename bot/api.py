"""Monobank public API client and exchange rate parsing utilities."""

import aiohttp

MONOBANK_API_URL = "https://api.monobank.ua/bank/currency"

# Monobank currency codes (ISO 4217 numeric)
USD_CODE = 840
EUR_CODE = 978
UAH_CODE = 980


def parse_rates(data: list[dict]) -> dict[str, dict[str, float]]:
    """Parse a Monobank currency list response into a structured rates dict.

    Args:
        data: Raw JSON list from the Monobank /bank/currency endpoint.

    Returns:
        A dict with keys "USD" and "EUR", each containing "buy" and "sell"
        float values expressed in UAH.

    Raises:
        ValueError: If USD or EUR rates against UAH are not found in data.
    """
    rates: dict[str, dict[str, float]] = {}

    currency_map = {
        USD_CODE: "USD",
        EUR_CODE: "EUR",
    }

    for entry in data:
        currency_code_a = entry.get("currencyCodeA")
        currency_code_b = entry.get("currencyCodeB")

        if currency_code_b != UAH_CODE:
            continue

        if currency_code_a in currency_map:
            name = currency_map[currency_code_a]
            rates[name] = {
                "buy": float(entry["rateBuy"]),
                "sell": float(entry["rateSell"]),
            }

    missing = [name for name in ("USD", "EUR") if name not in rates]
    if missing:
        raise ValueError(f"Rates not found for: {', '.join(missing)}")

    return rates


def format_rates_message(rates: dict[str, dict[str, float]]) -> str:
    """Format parsed exchange rates into a human-readable Telegram message.

    Args:
        rates: A dict as returned by :func:`parse_rates`.

    Returns:
        A formatted multi-line string ready to send as a Telegram message.
    """
    usd = rates["USD"]
    eur = rates["EUR"]

    return (
        "💱 <b>Актуальний курс валют</b> (НБУ / Monobank)\n\n"
        f"🇺🇸 <b>USD</b>\n"
        f"  Купівля:  <code>{usd['buy']:.2f} ₴</code>\n"
        f"  Продаж:   <code>{usd['sell']:.2f} ₴</code>\n\n"
        f"🇪🇺 <b>EUR</b>\n"
        f"  Купівля:  <code>{eur['buy']:.2f} ₴</code>\n"
        f"  Продаж:   <code>{eur['sell']:.2f} ₴</code>"
    )


async def fetch_rates(session: aiohttp.ClientSession) -> dict[str, dict[str, float]]:
    """Fetch and parse current USD/EUR → UAH rates from the Monobank API.

    Args:
        session: An active :class:`aiohttp.ClientSession` to use for the request.

    Returns:
        A dict with "USD" and "EUR" keys, each with "buy" and "sell" floats.

    Raises:
        aiohttp.ClientError: On network-level failures.
        ValueError: If expected currency pairs are absent in the response.
    """
    async with session.get(MONOBANK_API_URL) as response:
        response.raise_for_status()
        data: list[dict] = await response.json()

    return parse_rates(data)
