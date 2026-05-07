"""Comprehensive tests for FinancialDatasets data provider."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import json

from src.data.providers.fd_provider import FDProvider
from src.data.models import Price, FinancialMetrics, CompanyNews, CompanyFacts


class TestFDProvider:
    """Test suite for FDProvider class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Set API key for testing
        os.environ["FINANCIAL_DATASETS_API_KEY"] = "test-api-key"
        self.provider = FDProvider()
        self.ticker = "AAPL"
        self.start_date = "2024-01-01"
        self.end_date = "2024-01-10"

    def teardown_method(self):
        """Clean up test fixtures."""
        if "FINANCIAL_DATASETS_API_KEY" in os.environ:
            del os.environ["FINANCIAL_DATASETS_API_KEY"]

    @patch('src.data.providers.fd_provider.requests.Session')
    def test_get_prices_success(self, mock_session):
        """Test successful price data retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'prices': [
                {
                    'open': 150.0,
                    'close': 152.0,
                    'high': 155.0,
                    'low': 149.0,
                    'volume': 1000000,
                    'time': '2024-01-01'
                },
                {
                    'open': 152.0,
                    'close': 154.0,
                    'high': 156.0,
                    'low': 151.0,
                    'volume': 1200000,
                    'time': '2024-01-02'
                }
            ]
        }
        
        mock_session.return_value.get.return_value = mock_response

        # Call the method
        prices = self.provider.get_prices(self.ticker, self.start_date, self.end_date)

        # Assertions
        assert len(prices) == 2
        assert isinstance(prices[0], Price)
        assert prices[0].open == 150.0
        assert prices[0].close == 152.0
        assert prices[0].high == 155.0
        assert prices[0].low == 149.0
        assert prices[0].volume == 1000000
        assert prices[0].time == "2024-01-01"

        # Verify the request was made correctly
        mock_session.return_value.get.assert_called_once_with(
            f"https://api.financialdatasets.ai/prices/?ticker={self.ticker}&interval=day&interval_multiplier=1&start_date={self.start_date}&end_date={self.end_date}"
        )

    @patch('src.data.providers.fd_provider.requests.Session')
    def test_get_prices_api_error(self, mock_session):
        """Test handling of API errors in price data retrieval."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_session.return_value.get.return_value = mock_response

        prices = self.provider.get_prices(self.ticker, self.start_date, self.end_date)

        assert len(prices) == 0

    @patch('src.data.providers.fd_provider.requests.Session')
    def test_get_prices_network_error(self, mock_session):
        """Test handling of network errors."""
        mock_session.return_value.get.side_effect = Exception("Network error")

        prices = self.provider.get_prices(self.ticker, self.start_date, self.end_date)

        assert len(prices) == 0

    @patch('src.data.providers.fd_provider.requests.Session')
    def test_get_financial_metrics_success(self, mock_session):
        """Test successful financial metrics retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'financial_metrics': [
                {
                    'ticker': 'AAPL',
                    'period': '2024-01-10',
                    'period_type': 'ttm',
                    'pe_ratio': 25.0,
                    'pb_ratio': 35.0,
                    'profit_margin': 0.25,
                    'operating_margin': 0.22,
                    'return_on_assets': 0.18,
                    'return_on_equity': 0.45,
                    'revenue_growth': 0.08,
                    'earnings_growth': 0.12,
                    'current_ratio': 1.8,
                    'debt_to_equity': 1.2,
                    'free_cash_flow': 10000000000.0,
                    'operating_cash_flow': 12000000000.0,
                    'total_revenue': 400000000000.0,
                    'gross_profit': 180000000000.0,
                    'ebitda': 130000000000.0,
                    'net_income': 100000000000.0
                }
            ]
        }
        
        mock_session.return_value.get.return_value = mock_response

        metrics = self.provider.get_financial_metrics(
            self.ticker, self.end_date, "ttm", 10
        )

        assert len(metrics) == 1
        assert isinstance(metrics[0], FinancialMetrics)
        assert metrics[0].pe_ratio == 25.0
        assert metrics[0].profit_margin == 0.25
        assert metrics[0].return_on_equity == 0.45

    @patch('src.data.providers.fd_provider.requests.Session')
    def test_get_financial_metrics_empty_data(self, mock_session):
        """Test handling of empty financial metrics data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'financial_metrics': []}
        
        mock_session.return_value.get.return_value = mock_response

        metrics = self.provider.get_financial_metrics(
            self.ticker, self.end_date, "ttm", 10
        )

        assert len(metrics) == 0

    @patch('src.data.providers.fd_provider.requests.Session')
    def test_get_news_success(self, mock_session):
        """Test successful news retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'news': [
                {
                    'title': 'Apple Announces New iPhone',
                    'source': 'Reuters',
                    'url': 'https://example.com/news1',
                    'published_at': '2024-01-01T00:00:00Z',
                    'summary': 'Apple announced a new iPhone model.',
                    'sentiment_score': 0.8,
                    'sentiment_label': 'positive'
                },
                {
                    'title': 'Apple Earnings Beat Expectations',
                    'source': 'Bloomberg',
                    'url': 'https://example.com/news2',
                    'published_at': '2024-01-02T00:00:00Z',
                    'summary': 'Apple reported better than expected earnings.',
                    'sentiment_score': 0.9,
                    'sentiment_label': 'positive'
                }
            ]
        }
        
        mock_session.return_value.get.return_value = mock_response

        news = self.provider.get_news(
            self.ticker, self.end_date, self.start_date, 5
        )

        assert len(news) == 2
        assert isinstance(news[0], CompanyNews)
        assert news[0].title == "Apple Announces New iPhone"
        assert news[0].source == "Reuters"
        assert news[0].url == "https://example.com/news1"
        assert news[0].sentiment_score == 0.8

    @patch('src.data.providers.fd_provider.requests.Session')
    def test_get_company_facts_success(self, mock_session):
        """Test successful company facts retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'company_facts': {
                'company_name': 'Apple Inc.',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'employees': 164000,
                'website': 'https://www.apple.com',
                'country': 'United States',
                'city': 'Cupertino',
                'state': 'CA',
                'zip': '95014',
                'market_cap': 3000000000000.0,
                'currency': 'USD',
                'description': 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.'
            }
        }
        
        mock_session.return_value.get.return_value = mock_response

        facts = self.provider.get_company_facts(self.ticker)

        assert facts is not None
        assert isinstance(facts, CompanyFacts)
        assert facts.company_name == "Apple Inc."
        assert facts.sector == "Technology"
        assert facts.industry == "Consumer Electronics"
        assert facts.employees == 164000
        assert facts.market_cap == 3000000000000.0

    @patch('src.data.providers.fd_provider.requests.Session')
    def test_get_company_facts_not_found(self, mock_session):
        """Test handling of missing company facts."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        
        mock_session.return_value.get.return_value = mock_response

        facts = self.provider.get_company_facts(self.ticker)

        assert facts is None

    def test_api_key_required(self):
        """Test that API key is required for requests."""
        # Remove API key from environment
        if "FINANCIAL_DATASETS_API_KEY" in os.environ:
            del os.environ["FINANCIAL_DATASETS_API_KEY"]
        
        # Create new provider instance (will pick up the missing API key)
        provider = FDProvider()
        
        # The provider should still be created but requests may fail
        assert provider.api_key == ""

    def test_provider_implements_protocol(self):
        """Test that FDProvider implements the DataProvider protocol."""
        from src.data.providers import DataProvider
        
        # Check that all required methods exist
        assert hasattr(self.provider, 'get_prices')
        assert hasattr(self.provider, 'get_financial_metrics')
        assert hasattr(self.provider, 'get_news')
        assert hasattr(self.provider, 'get_company_facts')
        
        # Check that methods are callable
        assert callable(self.provider.get_prices)
        assert callable(self.provider.get_financial_metrics)
        assert callable(self.provider.get_news)
        assert callable(self.provider.get_company_facts)


@pytest.mark.integration
class TestFDProviderIntegration:
    """Integration tests for FDProvider (requires API key and internet connection)."""

    def setup_method(self):
        """Set up test fixtures."""
        # Only run if API key is available
        if not os.environ.get("FINANCIAL_DATASETS_API_KEY"):
            pytest.skip("FINANCIAL_DATASETS_API_KEY not set for integration tests")
        
        self.provider = FDProvider()
        self.ticker = "AAPL"
        self.start_date = "2024-01-01"
        self.end_date = "2024-01-10"

    @pytest.mark.skip("Enable for integration testing with valid API key")
    def test_get_prices_integration(self):
        """Integration test for price data retrieval."""
        prices = self.provider.get_prices(self.ticker, self.start_date, self.end_date)
        
        # Should return some data if API key is valid
        assert isinstance(prices, list)
        if len(prices) > 0:
            assert isinstance(prices[0], Price)

    @pytest.mark.skip("Enable for integration testing with valid API key")
    def test_get_financial_metrics_integration(self):
        """Integration test for financial metrics."""
        metrics = self.provider.get_financial_metrics(self.ticker, self.end_date, "ttm", 10)
        
        # Should return some data if API key is valid
        assert isinstance(metrics, list)
        if len(metrics) > 0:
            assert isinstance(metrics[0], FinancialMetrics)

    @pytest.mark.skip("Enable for integration testing with valid API key")
    def test_get_news_integration(self):
        """Integration test for news retrieval."""
        news = self.provider.get_news(self.ticker, self.end_date, self.start_date, 5)
        
        # Should return some data if API key is valid
        assert isinstance(news, list)
        if len(news) > 0:
            assert isinstance(news[0], CompanyNews)

    @pytest.mark.skip("Enable for integration testing with valid API key")
    def test_get_company_facts_integration(self):
        """Integration test for company facts."""
        facts = self.provider.get_company_facts(self.ticker)
        
        # Should return data if API key is valid
        if facts is not None:
            assert isinstance(facts, CompanyFacts)
            assert facts.company_name == "Apple Inc."