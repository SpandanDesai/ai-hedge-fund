"""Data provider abstraction layer with protocol and factory pattern."""

from abc import ABC, abstractmethod
from typing import Protocol, Optional
import os

from src.data.models import Price, FinancialMetrics, CompanyNews, CompanyFacts


class DataProvider(Protocol):
    """Protocol that all data providers must implement."""
    
    @abstractmethod
    def get_prices(self, ticker: str, start_date: str, end_date: str) -> list[Price]:
        """Fetch historical price data."""
        pass
    
    @abstractmethod
    def get_financial_metrics(self, ticker: str, end_date: str, 
                            period: str, limit: int) -> list[FinancialMetrics]:
        """Fetch financial metrics data."""
        pass
    
    @abstractmethod
    def get_news(self, ticker: str, end_date: str, 
                start_date: Optional[str], limit: int) -> list[CompanyNews]:
        """Fetch company news data."""
        pass
    
    @abstractmethod
    def get_company_facts(self, ticker: str) -> Optional[CompanyFacts]:
        """Fetch company facts data."""
        pass


def get_data_provider(provider_name: str = None) -> DataProvider:
    """Factory function to get the appropriate data provider."""
    provider_name = provider_name or os.environ.get("DATA_PROVIDER", "yahoo")
    
    if provider_name == "yahoo":
        from .yahoo_provider import YahooProvider
        return YahooProvider()
    elif provider_name == "financialdatasets":
        from .fd_provider import FDProvider
        return FDProvider()
    else:
        raise ValueError(f"Unknown data provider: {provider_name}")


# Export the protocol for type checking
__all__ = ['DataProvider', 'get_data_provider']