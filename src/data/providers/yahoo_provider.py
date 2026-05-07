"""Yahoo Finance data provider implementation."""

import yfinance as yf
import pandas as pd
from typing import List, Optional
import logging
from datetime import datetime

from src.data.models import Price, FinancialMetrics, CompanyNews, CompanyFacts
from . import DataProvider

logger = logging.getLogger(__name__)


class YahooProvider(DataProvider):
    """Yahoo Finance data provider implementation."""
    
    def __init__(self):
        self.cache = {}
    
    def get_prices(self, ticker: str, start_date: str, end_date: str) -> List[Price]:
        """Fetch historical price data from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date, interval="1d")
            
            if df.empty:
                logger.warning(f"No price data found for {ticker} from {start_date} to {end_date}")
                return []
            
            prices = []
            for idx, row in df.iterrows():
                prices.append(Price(
                    open=float(row['Open']),
                    close=float(row['Close']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    volume=int(row['Volume']),
                    time=idx.strftime('%Y-%m-%d')
                ))
            return prices
        except Exception as e:
            logger.error(f"Error fetching prices for {ticker}: {e}")
            return []
    
    def get_financial_metrics(self, ticker: str, end_date: str, 
                           period: str = "ttm", limit: int = 10) -> List[FinancialMetrics]:
        """Fetch financial metrics from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info:
                logger.warning(f"No financial metrics found for {ticker}")
                return []
            
            metrics = FinancialMetrics(
                ticker=ticker,
                report_period=end_date,
                period=period,
                currency=info.get('currency', 'USD'),
                market_cap=info.get('marketCap'),
                enterprise_value=info.get('enterpriseValue'),
                price_to_earnings_ratio=info.get('trailingPE'),
                price_to_book_ratio=info.get('priceToBook'),
                price_to_sales_ratio=info.get('priceToSalesTrailing12Months'),
                gross_margin=info.get('grossMargins'),
                operating_margin=info.get('operatingMargins'),
                net_margin=info.get('profitMargins'),
                return_on_equity=info.get('returnOnEquity'),
                return_on_assets=info.get('returnOnAssets'),
                debt_to_equity=info.get('debtToEquity'),
                revenue_growth=info.get('revenueGrowth'),
                earnings_growth=info.get('earningsGrowth'),
                earnings_per_share=info.get('trailingEps'),
                book_value_per_share=info.get('bookValue')
            )
            return [metrics]
        except Exception as e:
            logger.error(f"Error fetching financial metrics for {ticker}: {e}")
            return []
    
    def get_news(self, ticker: str, end_date: str, 
                start_date: Optional[str] = None, limit: int = 1000) -> List[CompanyNews]:
        """Fetch company news from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news or []
            
            company_news = []
            for item in news[:limit]:
                company_news.append(CompanyNews(
                    ticker=ticker,
                    title=item.get('title', ''),
                    source=item.get('publisher', ''),
                    date=item.get('publishedAt', ''),
                    url=item.get('link', ''),
                    sentiment=None  # Yahoo Finance doesn't provide sentiment analysis
                ))
            return company_news
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            return []
    
    def get_company_facts(self, ticker: str) -> Optional[CompanyFacts]:
        """Fetch company facts from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info:
                return None
            
            return CompanyFacts(
                ticker=ticker,
                name=info.get('longName', ''),
                industry=info.get('industry', ''),
                sector=info.get('sector', ''),
                exchange=info.get('exchange', ''),
                market_cap=info.get('marketCap'),
                website_url=info.get('website', '')
            )
        except Exception as e:
            logger.error(f"Error fetching company facts for {ticker}: {e}")
            return None


# Export the provider
__all__ = ['YahooProvider']