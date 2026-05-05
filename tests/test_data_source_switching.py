import os
from unittest.mock import Mock, patch

from src.data.models import Price
from src.tools.api import get_prices


@patch("src.tools.api._cache")
@patch("src.tools.api._yahoo_client")
def test_get_prices_uses_yahoo_when_configured(mock_yahoo, mock_cache):
    mock_cache.get_prices.return_value = None
    mock_yahoo.get_prices.return_value = [
        Price(open=1.0, close=2.0, high=3.0, low=0.5, volume=10, time="2024-01-01"),
    ]

    with patch.dict(os.environ, {"DATA_SOURCE": "yahoo"}, clear=False):
        prices = get_prices("AAPL", "2024-01-01", "2024-01-02")

    assert len(prices) == 1
    assert prices[0].close == 2.0
    mock_yahoo.get_prices.assert_called_once_with("AAPL", "2024-01-01", "2024-01-02")


@patch("src.tools.api.requests.get")
@patch("src.tools.api._cache")
def test_get_prices_uses_financialdatasets_when_key_present(mock_cache, mock_get):
    mock_cache.get_prices.return_value = None

    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "ticker": "AAPL",
        "prices": [
            {
                "time": "2024-01-01T00:00:00Z",
                "open": 100.0,
                "close": 101.0,
                "high": 102.0,
                "low": 99.0,
                "volume": 1000,
            }
        ],
    }
    mock_get.return_value = mock_resp

    with patch.dict(os.environ, {"FINANCIAL_DATASETS_API_KEY": "test-key"}, clear=False):
        prices = get_prices("AAPL", "2024-01-01", "2024-01-02")

    assert len(prices) == 1
    assert prices[0].open == 100.0

