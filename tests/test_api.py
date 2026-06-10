"""Tests for bot.api — parse_rates(), format_rates_message(), fetch_rates()."""

import pytest

from bot.api import (
    EUR_CODE,
    UAH_CODE,
    USD_CODE,
    format_rates_message,
    parse_rates,
    fetch_rates,
)


# ─── Fixtures ──────────────────────────────────────────────────────────────────

VALID_API_RESPONSE = [
    # USD → UAH
    {
        "currencyCodeA": USD_CODE,
        "currencyCodeB": UAH_CODE,
        "rateBuy": 41.5,
        "rateSell": 42.0,
    },
    # EUR → UAH
    {
        "currencyCodeA": EUR_CODE,
        "currencyCodeB": UAH_CODE,
        "rateBuy": 44.8,
        "rateSell": 45.5,
    },
    # Unrelated pair — must be ignored
    {
        "currencyCodeA": USD_CODE,
        "currencyCodeB": EUR_CODE,
        "rateBuy": 0.92,
        "rateSell": 0.94,
    },
]


# ─── parse_rates() ─────────────────────────────────────────────────────────────

class TestParseRates:
    """Unit tests for the pure parse_rates() function."""

    def test_returns_usd_and_eur_keys(self):
        rates = parse_rates(VALID_API_RESPONSE)
        assert "USD" in rates
        assert "EUR" in rates

    def test_usd_buy_value(self):
        rates = parse_rates(VALID_API_RESPONSE)
        assert rates["USD"]["buy"] == pytest.approx(41.5)

    def test_usd_sell_value(self):
        rates = parse_rates(VALID_API_RESPONSE)
        assert rates["USD"]["sell"] == pytest.approx(42.0)

    def test_eur_buy_value(self):
        rates = parse_rates(VALID_API_RESPONSE)
        assert rates["EUR"]["buy"] == pytest.approx(44.8)

    def test_eur_sell_value(self):
        rates = parse_rates(VALID_API_RESPONSE)
        assert rates["EUR"]["sell"] == pytest.approx(45.5)

    def test_ignores_unrelated_currency_pairs(self):
        """USD/EUR pair (not against UAH) must not pollute the result."""
        rates = parse_rates(VALID_API_RESPONSE)
        assert len(rates) == 2

    def test_returns_float_values(self):
        rates = parse_rates(VALID_API_RESPONSE)
        assert isinstance(rates["USD"]["buy"], float)
        assert isinstance(rates["EUR"]["sell"], float)

    def test_raises_value_error_when_usd_missing(self):
        data = [
            {
                "currencyCodeA": EUR_CODE,
                "currencyCodeB": UAH_CODE,
                "rateBuy": 44.8,
                "rateSell": 45.5,
            }
        ]
        with pytest.raises(ValueError, match="USD"):
            parse_rates(data)

    def test_raises_value_error_when_eur_missing(self):
        data = [
            {
                "currencyCodeA": USD_CODE,
                "currencyCodeB": UAH_CODE,
                "rateBuy": 41.5,
                "rateSell": 42.0,
            }
        ]
        with pytest.raises(ValueError, match="EUR"):
            parse_rates(data)

    def test_raises_value_error_on_empty_list(self):
        with pytest.raises(ValueError):
            parse_rates([])


# ─── format_rates_message() ────────────────────────────────────────────────────

class TestFormatRatesMessage:
    """Unit tests for format_rates_message() output structure."""

    @pytest.fixture
    def rates(self):
        return parse_rates(VALID_API_RESPONSE)

    def test_contains_usd_label(self, rates):
        msg = format_rates_message(rates)
        assert "USD" in msg

    def test_contains_eur_label(self, rates):
        msg = format_rates_message(rates)
        assert "EUR" in msg

    def test_contains_usd_buy_value(self, rates):
        msg = format_rates_message(rates)
        assert "41.50" in msg

    def test_contains_usd_sell_value(self, rates):
        msg = format_rates_message(rates)
        assert "42.00" in msg

    def test_contains_eur_buy_value(self, rates):
        msg = format_rates_message(rates)
        assert "44.80" in msg

    def test_contains_eur_sell_value(self, rates):
        msg = format_rates_message(rates)
        assert "45.50" in msg

    def test_contains_html_bold_tags(self, rates):
        """Message must use HTML formatting as required by parse_mode='HTML'."""
        msg = format_rates_message(rates)
        assert "<b>" in msg
        assert "</b>" in msg

    def test_contains_hryvnia_symbol(self, rates):
        msg = format_rates_message(rates)
        assert "₴" in msg

    def test_is_string(self, rates):
        assert isinstance(format_rates_message(rates), str)


# ─── fetch_rates() ────────────────────────────────────────────────────────────

class TestFetchRates:
    """Integration-style tests for fetch_rates() using a mocked HTTP session."""

    async def test_fetch_rates_returns_parsed_dict(self, mocker):
        """fetch_rates() should return a properly parsed rates dict."""
        mock_response = mocker.AsyncMock()
        mock_response.raise_for_status = mocker.Mock()
        mock_response.json = mocker.AsyncMock(return_value=VALID_API_RESPONSE)
        mock_response.__aenter__ = mocker.AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = mocker.AsyncMock(return_value=False)

        mock_session = mocker.MagicMock()
        mock_session.get = mocker.MagicMock(return_value=mock_response)

        rates = await fetch_rates(mock_session)

        assert "USD" in rates
        assert "EUR" in rates
        assert rates["USD"]["buy"] == pytest.approx(41.5)
        assert rates["EUR"]["sell"] == pytest.approx(45.5)

    async def test_fetch_rates_calls_correct_url(self, mocker):
        """fetch_rates() must call the Monobank API endpoint."""
        from bot.api import MONOBANK_API_URL

        mock_response = mocker.AsyncMock()
        mock_response.raise_for_status = mocker.Mock()
        mock_response.json = mocker.AsyncMock(return_value=VALID_API_RESPONSE)
        mock_response.__aenter__ = mocker.AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = mocker.AsyncMock(return_value=False)

        mock_session = mocker.MagicMock()
        mock_session.get = mocker.MagicMock(return_value=mock_response)

        await fetch_rates(mock_session)

        mock_session.get.assert_called_once_with(MONOBANK_API_URL)
