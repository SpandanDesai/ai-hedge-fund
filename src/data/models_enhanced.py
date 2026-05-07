"""Enhanced data models with comprehensive validation and type safety."""

from pydantic import BaseModel, Field, validator, condecimal, conint
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
import re
from enum import Enum


class Currency(str, Enum):
    """Supported currency types."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    INR = "INR"


class PeriodType(str, Enum):
    """Financial period types."""
    TTM = "ttm"  # Trailing twelve months
    Q1 = "q1"
    Q2 = "q2"
    Q3 = "q3"
    Q4 = "q4"
    FY = "fy"  # Fiscal year


class EnhancedPrice(BaseModel):
    """Enhanced price model with comprehensive validation."""
    
    open: condecimal(ge=0) = Field(..., description="Opening price", example=150.0)
    close: condecimal(ge=0) = Field(..., description="Closing price", example=152.0)
    high: condecimal(ge=0) = Field(..., description="Daily high price", example=155.0)
    low: condecimal(ge=0) = Field(..., description="Daily low price", example=149.0)
    volume: conint(ge=0) = Field(..., description="Trading volume", example=1000000)
    time: date = Field(..., description="Trading date")
    
    @validator('high')
    def high_greater_than_low(cls, v, values):
        if 'low' in values and v < values['low']:
            raise ValueError('High price must be greater than or equal to low price')
        return v
    
    @validator('time', pre=True)
    def validate_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class EnhancedFinancialMetrics(BaseModel):
    """Enhanced financial metrics with comprehensive validation."""
    
    ticker: str = Field(..., description="Stock ticker symbol", example="AAPL")
    report_period: date = Field(..., description="Report period end date")
    period: PeriodType = Field(..., description="Financial period type")
    currency: Currency = Field(default=Currency.USD, description="Reporting currency")
    
    # Valuation metrics
    market_cap: Optional[condecimal(ge=0)] = Field(None, description="Market capitalization")
    enterprise_value: Optional[condecimal(ge=0)] = Field(None, description="Enterprise value")
    price_to_earnings_ratio: Optional[condecimal(ge=0)] = Field(None, description="P/E ratio")
    price_to_book_ratio: Optional[condecimal(ge=0)] = Field(None, description="P/B ratio")
    price_to_sales_ratio: Optional[condecimal(ge=0)] = Field(None, description="P/S ratio")
    
    # Profitability metrics
    gross_margin: Optional[condecimal(ge=0, le=1)] = Field(None, description="Gross margin ratio")
    operating_margin: Optional[condecimal(ge=0, le=1)] = Field(None, description="Operating margin ratio")
    net_margin: Optional[condecimal(ge=0, le=1)] = Field(None, description="Net margin ratio")
    return_on_equity: Optional[condecimal(ge=0, le=1)] = Field(None, description="Return on equity")
    return_on_assets: Optional[condecimal(ge=0, le=1)] = Field(None, description="Return on assets")
    
    # Leverage metrics
    debt_to_equity: Optional[condecimal(ge=0)] = Field(None, description="Debt to equity ratio")
    debt_to_assets: Optional[condecimal(ge=0, le=1)] = Field(None, description="Debt to assets ratio")
    interest_coverage: Optional[condecimal(ge=0)] = Field(None, description="Interest coverage ratio")
    
    # Growth metrics
    revenue_growth: Optional[condecimal(ge=-1)] = Field(None, description="Revenue growth rate")
    earnings_growth: Optional[condecimal(ge=-1)] = Field(None, description="Earnings growth rate")
    
    # Per-share metrics
    earnings_per_share: Optional[condecimal(ge=0)] = Field(None, description="Earnings per share")
    book_value_per_share: Optional[condecimal(ge=0)] = Field(None, description="Book value per share")
    
    @validator('ticker')
    def validate_ticker(cls, v):
        if not re.match(r'^[A-Z]{1,5}$', v):
            raise ValueError('Ticker must be 1-5 uppercase letters')
        return v
    
    @validator('report_period', pre=True)
    def validate_report_period(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Report period must be in YYYY-MM-DD format')
        return v


class EnhancedCompanyNews(BaseModel):
    """Enhanced company news model with comprehensive validation."""
    
    ticker: str = Field(..., description="Stock ticker symbol", example="AAPL")
    title: str = Field(..., description="News title", min_length=1, max_length=500)
    author: Optional[str] = Field(None, description="Article author", max_length=100)
    source: str = Field(..., description="News source", max_length=100)
    date: datetime = Field(..., description="Publication date")
    url: str = Field(..., description="Article URL")
    sentiment: Optional[condecimal(ge=-1, le=1)] = Field(None, description="Sentiment score (-1 to 1)")
    
    @validator('ticker')
    def validate_ticker(cls, v):
        if not re.match(r'^[A-Z]{1,5}$', v):
            raise ValueError('Ticker must be 1-5 uppercase letters')
        return v
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @validator('date', pre=True)
    def validate_date(cls, v):
        if isinstance(v, str):
            try:
                # Try ISO format first
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try common date formats
                    return datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    try:
                        return datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        raise ValueError('Date must be in ISO format or YYYY-MM-DD HH:MM:SS')
        return v


class EnhancedCompanyFacts(BaseModel):
    """Enhanced company facts model with comprehensive validation."""
    
    ticker: str = Field(..., description="Stock ticker symbol", example="AAPL")
    name: str = Field(..., description="Company name", min_length=1, max_length=200)
    cik: Optional[str] = Field(None, description="CIK number", max_length=10)
    industry: Optional[str] = Field(None, description="Industry classification", max_length=100)
    sector: Optional[str] = Field(None, description="Sector classification", max_length=100)
    exchange: Optional[str] = Field(None, description="Stock exchange", max_length=10)
    is_active: Optional[bool] = Field(None, description="Whether company is active")
    listing_date: Optional[date] = Field(None, description="Listing date")
    market_cap: Optional[condecimal(ge=0)] = Field(None, description="Market capitalization")
    website_url: Optional[str] = Field(None, description="Company website URL")
    
    @validator('ticker')
    def validate_ticker(cls, v):
        if not re.match(r'^[A-Z]{1,5}$', v):
            raise ValueError('Ticker must be 1-5 uppercase letters')
        return v
    
    @validator('cik')
    def validate_cik(cls, v):
        if v and not re.match(r'^\d{10}$', v):
            raise ValueError('CIK must be 10 digits')
        return v
    
    @validator('website_url')
    def validate_website_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Website URL must start with http:// or https://')
        return v
    
    @validator('listing_date', pre=True)
    def validate_listing_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Listing date must be in YYYY-MM-DD format')
        return v


class EnhancedInsiderTrade(BaseModel):
    """Enhanced insider trade model with comprehensive validation."""
    
    ticker: str = Field(..., description="Stock ticker symbol", example="AAPL")
    issuer: Optional[str] = Field(None, description="Issuer name", max_length=200)
    name: Optional[str] = Field(None, description="Insider name", max_length=200)
    title: Optional[str] = Field(None, description="Insider title", max_length=100)
    is_board_director: Optional[bool] = Field(None, description="Is board director")
    transaction_date: Optional[date] = Field(None, description="Transaction date")
    transaction_shares: Optional[condecimal(ge=0)] = Field(None, description="Number of shares traded")
    transaction_price_per_share: Optional[condecimal(ge=0)] = Field(None, description="Price per share")
    transaction_value: Optional[condecimal(ge=0)] = Field(None, description="Total transaction value")
    shares_owned_before_transaction: Optional[condecimal(ge=0)] = Field(None, description="Shares owned before")
    shares_owned_after_transaction: Optional[condecimal(ge=0)] = Field(None, description="Shares owned after")
    security_title: Optional[str] = Field(None, description="Security title", max_length=100)
    filing_date: date = Field(..., description="Filing date")
    
    @validator('ticker')
    def validate_ticker(cls, v):
        if not re.match(r'^[A-Z]{1,5}$', v):
            raise ValueError('Ticker must be 1-5 uppercase letters')
        return v
    
    @validator('transaction_date', 'filing_date', pre=True)
    def validate_dates(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v


# Response models for enhanced data types
class EnhancedPriceResponse(BaseModel):
    ticker: str
    prices: List[EnhancedPrice]


class EnhancedFinancialMetricsResponse(BaseModel):
    financial_metrics: List[EnhancedFinancialMetrics]


class EnhancedCompanyNewsResponse(BaseModel):
    news: List[EnhancedCompanyNews]


class EnhancedCompanyFactsResponse(BaseModel):
    company_facts: EnhancedCompanyFacts


class EnhancedInsiderTradeResponse(BaseModel):
    insider_trades: List[EnhancedInsiderTrade]


# Utility functions for model conversion
def convert_to_enhanced_price(price: Any) -> EnhancedPrice:
    """Convert basic price model to enhanced version."""
    return EnhancedPrice(**price.model_dump())


def convert_to_enhanced_financial_metrics(metrics: Any) -> EnhancedFinancialMetrics:
    """Convert basic financial metrics to enhanced version."""
    return EnhancedFinancialMetrics(**metrics.model_dump())


# Export enhanced models
__all__ = [
    'Currency',
    'PeriodType',
    'EnhancedPrice',
    'EnhancedFinancialMetrics',
    'EnhancedCompanyNews',
    'EnhancedCompanyFacts',
    'EnhancedInsiderTrade',
    'EnhancedPriceResponse',
    'EnhancedFinancialMetricsResponse',
    'EnhancedCompanyNewsResponse',
    'EnhancedCompanyFactsResponse',
    'EnhancedInsiderTradeResponse',
    'convert_to_enhanced_price',
    'convert_to_enhanced_financial_metrics'
]