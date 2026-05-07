"""FinancialDatasets.ai data provider implementation."""

import os
import requests
from typing import List, Optional
import logging

from src.data.models import Price, FinancialMetrics, CompanyNews, CompanyFacts
from . import DataProvider

logger = logging.getLogger(__name__)


class FDProvider(DataProvider):
    """FinancialDatasets.ai data provider implementation."""
    
    def __init__(self):
        self.base_url = "https://api.financialdatasets.ai"
        self.api_key = os.environ.get("FINANCIAL_DATASETS_API_KEY", "")
        self.session = requests.Session()
        self.session.headers["X-API-Key"] = self.api_key
    
    def _make_request(self, url: str, method: str = "GET", json_data: dict = None):
        """Make API request with error handling."""
        try:
            if method.upper() == "POST":
                response = self.session.post(url, json=json_data)
            else:
                response = self.session.get(url)
            
            if response.status_code == 200:
                return response
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            return None
    
    def get_prices(self, ticker: str, start_date: str, end_date: str) -> List[Price]:
        """Fetch historical price data from FinancialDatasets.ai."""
        url = f"{self.base_url}/prices/?ticker={ticker}&interval=day&interval_multiplier=1&start_date={start_date}&end_date={end_date}"
        response = self._make_request(url)
        
        if not response:
            return []
        
        try:
            data = response.json()
            prices = data.get('prices', [])
            return [Price(**price) for price in prices]
        except Exception as e:
            logger.error(f"Error parsing price data for {ticker}: {e}")
            return []
    
    def get_financial_metrics(self, ticker: str, end_date: str, 
                           period: str = "ttm", limit: int = 10) -> List[FinancialMetrics]:
        """Fetch financial metrics from FinancialDatasets.ai."""
        url = f"{self.base_url}/financial-metrics/?ticker={ticker}&report_period_lte={end_date}&limit={limit}&period={period}"
        response = self._make_request(url)
        
        if not response:
            return []
        
        try:
            data = response.json()
            metrics = data.get('financial_metrics', [])
            return [FinancialMetrics(**metric) for metric in metrics]
        except Exception as e:
            logger.error(f"Error parsing financial metrics for {ticker}: {e}")
            return []
    
    def get_news(self, ticker: str, end_date: str, 
                start_date: Optional[str] = None, limit: int = 1000) -> List[CompanyNews]:
        """Fetch company news from FinancialDatasets.ai."""
        url = f"{self.base_url}/news/?ticker={ticker}&end_date={end_date}&limit={limit}"
        if start_date:
            url += f"&start_date={start_date}"
        
        response = self._make_request(url)
        
        if not response:
            return []
        
        try:
            data = response.json()
            news = data.get('news', [])
            return [CompanyNews(**item) for item in news]
        except Exception as mind:
            logger.error(f"Error parsing news for {ticker}: {e}")
            return []
    
    def get_company_facts(self, ticker: str) -> Optional[CompanyFacts]:
        """Fetch company facts from FinancialDatasets.ai."""
        url = f"{self.base_url}/company/facts/?ticker={ticker}"
        response = self._make_request(url)
        
        if not response:
            return None
        
        try:
            data = response.json()
            facts = data.get('company_facts', {})
            return CompanyFacts(**facts)
        except Exception as e:
            logger.error(f"Error parsing company facts for {ticker}: {e}")
            return None


# Export the provider
__all__ = ['FDProvider']