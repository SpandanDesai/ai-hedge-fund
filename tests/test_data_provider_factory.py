"""Tests for data provider factory and protocol implementation."""

import pytest
import os
from unittest.mock import patch, MagicMock

from src.data.providers import get_data_provider, DataProvider
from src.data.providers.yahoo_provider import YahooProvider
from src.data.providers.fd_provider import FDProvider


class TestDataProviderFactory:
    """Test suite for data provider factory function."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clear any existing DATA_PROVIDER environment variable
        if "DATA_PROVIDER" in os.environ:
            self.old_provider = os.environ["DATA_PROVIDER"]
            del os.environ["DATA_PROVIDER"]
        else:
            self.old_provider = None

    def teardown_method(self):
        """Clean up test fixtures."""
        # Restore original DATA_PROVIDER if it existed
        if self.old_provider is not None:
            os.environ["DATA_PROVIDER"] = self.old_provider
        elif "DATA_PROVIDER" in os.environ:
            del os.environ["DATA_PROVIDER"]

    def test_get_data_provider_default_yahoo(self):
        """Test that default provider is Yahoo when no environment variable is set."""
        provider = get_data_provider()
        assert isinstance(provider, YahooProvider)

    def test_get_data_provider_yahoo_explicit(self):
        """Test getting Yahoo provider explicitly."""
        provider = get_data_provider("yahoo")
        assert isinstance(provider, YahooProvider)

    def test_get_data_provider_financialdatasets_explicit(self):
        """Test getting FinancialDatasets provider explicitly."""
        provider = get_data_provider("financialdatasets")
        assert isinstance(provider, FDProvider)

    def test_get_data_provider_from_environment(self):
        """Test getting provider from environment variable."""
        # Test Yahoo provider from environment
        os.environ["DATA_PROVIDER"] = "yahoo"
        provider = get_data_provider()
        assert isinstance(provider, YahooProvider)

        # Test FinancialDatasets provider from environment
        os.environ["DATA_PROVIDER"] = "financialdatasets"
        provider = get_data_provider()
        assert isinstance(provider, FDProvider)

    def test_get_data_provider_invalid_provider(self):
        """Test error handling for invalid provider names."""
        with pytest.raises(ValueError, match="Unknown data provider: invalid"):
            get_data_provider("invalid")

    def test_get_data_provider_invalid_environment(self):
        """Test error handling for invalid provider in environment."""
        os.environ["DATA_PROVIDER"] = "invalid"
        with pytest.raises(ValueError, match="Unknown data provider: invalid"):
            get_data_provider()

    def test_provider_factory_returns_protocol_instance(self):
        """Test that factory returns objects that implement DataProvider protocol."""
        yahoo_provider = get_data_provider("yahoo")
        fd_provider = get_data_provider("financialdatasets")

        # Both should implement the protocol
        assert isinstance(yahoo_provider, DataProvider)
        assert isinstance(fd_provider, DataProvider)

    def test_provider_method_signatures(self):
        """Test that both providers implement all required methods with correct signatures."""
        yahoo_provider = YahooProvider()
        fd_provider = FDProvider()

        # Test that all required methods exist
        required_methods = ['get_prices', 'get_financial_metrics', 'get_news', 'get_company_facts']
        
        for method_name in required_methods:
            assert hasattr(yahoo_provider, method_name)
            assert hasattr(fd_provider, method_name)
            
            # Methods should be callable
            assert callable(getattr(yahoo_provider, method_name))
            assert callable(getattr(fd_provider, method_name))

    @patch('src.data.providers.yahoo_provider.YahooProvider')
    @patch('src.data.providers.fd_provider.FDProvider')
    def test_provider_instantiation(self, mock_fd_provider, mock_yahoo_provider):
        """Test that providers are instantiated correctly."""
        # Mock the provider classes
        mock_yahoo_instance = MagicMock()
        mock_yahoo_provider.return_value = mock_yahoo_instance
        
        mock_fd_instance = MagicMock()
        mock_fd_provider.return_value = mock_fd_instance

        # Test Yahoo provider instantiation
        yahoo_provider = get_data_provider("yahoo")
        assert yahoo_provider == mock_yahoo_instance
        mock_yahoo_provider.assert_called_once()

        # Test FD provider instantiation
        fd_provider = get_data_provider("financialdatasets")
        assert fd_provider == mock_fd_instance
        mock_fd_provider.assert_called_once()


class TestDataProviderProtocol:
    """Test suite for DataProvider protocol compliance."""

    def test_protocol_definition(self):
        """Test that DataProvider protocol is properly defined."""
        from src.data.providers import DataProvider
        
        # Check that protocol has all required abstract methods
        assert hasattr(DataProvider, 'get_prices')
        assert hasattr(DataProvider, 'get_financial_metrics')
        assert hasattr(DataProvider, 'get_news')
        assert hasattr(DataProvider, 'get_company_facts')
        
        # Check that methods are abstract
        assert getattr(DataProvider.get_prices, '__isabstractmethod__', False)
        assert getattr(DataProvider.get_financial_metrics, '__isabstractmethod__', False)
        assert getattr(DataProvider.get_news, '__isabstractmethod__', False)
        assert getattr(DataProvider.get_company_facts, '__isabstractmethod__', False)

    def test_yahoo_provider_implements_protocol(self):
        """Test that YahooProvider implements the DataProvider protocol."""
        from src.data.providers import DataProvider
        from src.data.providers.yahoo_provider import YahooProvider
        
        provider = YahooProvider()
        
        # Check that all protocol methods are implemented
        assert hasattr(provider, 'get_prices')
        assert hasattr(provider, 'get_financial_metrics')
        assert hasattr(provider, 'get_news')
        assert hasattr(provider, 'get_company_facts')
        
        # Check that methods are not abstract
        assert not getattr(provider.get_prices, '__isabstractmethod__', False)
        assert not getattr(provider.get_financial_metrics, '__isabstractmethod__', False)
        assert not getattr(provider.get_news, '__isabstractmethod__', False)
        assert not getattr(provider.get_company_facts, '__isabstractmethod__', False)

    def test_fd_provider_implements_protocol(self):
        """Test that FDProvider implements the DataProvider protocol."""
        from src.data.providers import DataProvider
        from src.data.providers.fd_provider import FDProvider
        
        provider = FDProvider()
        
        # Check that all protocol methods are implemented
        assert hasattr(provider, 'get_prices')
        assert hasattr(provider, 'get_financial_metrics')
        assert hasattr(provider, 'get_news')
        assert hasattr(provider, 'get_company_facts')
        
        # Check that methods are not abstract
        assert not getattr(provider.get_prices, '__isabstractmethod__', False)
        assert not getattr(provider.get_financial_metrics, '__isabstractmethod__', False)
        assert not getattr(provider.get_news, '__isabstractmethod__', False)
        assert not getattr(provider.get_company_facts, '__isabstractmethod__', False)


@pytest.mark.parametrize("provider_name,provider_class", [
    ("yahoo", YahooProvider),
    ("financialdatasets", FDProvider)
])
class TestProviderConsistency:
    """Parameterized tests for provider consistency."""

    def test_provider_consistency(self, provider_name, provider_class):
        """Test that all providers behave consistently."""
        provider = get_data_provider(provider_name)
        
        # All providers should have the same interface
        assert hasattr(provider, 'get_prices')
        assert hasattr(provider, 'get_financial_metrics')
        assert hasattr(provider, 'get_news')
        assert hasattr(provider, 'get_company_facts')
        
        # All methods should return appropriate types (empty lists/None on error)
        prices = provider.get_prices("TEST", "2024-01-01", "2024-01-02")
        assert isinstance(prices, list)
        
        metrics = provider.get_financial_metrics("TEST", "2024-01-01", "ttm", 10)
        assert isinstance(metrics, list)
        
        news = provider.get_news("TEST", "2024-01-01", "2024-01-01", 5)
        assert isinstance(news, list)
        
        facts = provider.get_company_facts("TEST")
        assert facts is None or isinstance(facts, type(provider).__module__.split('.')[-1] + 'CompanyFacts')