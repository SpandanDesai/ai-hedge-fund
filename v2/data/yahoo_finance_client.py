"""Yahoo Finance data client (via yfinance).

This mirrors the v2 :class:`~v2.data.protocol.DataClient` protocol.
All methods are best-effort and return empty lists/None on failure.
"""

from __future__ import annotations

import datetime as _dt
import logging
from typing import Any

from v2.data.models import CompanyFacts, CompanyNews, Earnings, FinancialMetrics, Price

logger = logging.getLogger(__name__)


def _import_yfinance():
    try:
        import yfinance as yf  # type: ignore

        return yf
    except Exception as exc:  # pragma: no cover
        logger.warning("yfinance is not available (%s). Install it to use YahooFinanceClient.", exc)
        return None


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if value != value:  # NaN
            return None
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        return None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


def _unix_ts_to_iso(value: Any) -> str | None:
    ts = _to_int(value)
    if ts is None:
        return None
    try:
        return _dt.datetime.fromtimestamp(ts, tz=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None


class YahooFinanceClient:
    def get_prices(self, ticker: str, start_date: str, end_date: str, **kwargs) -> list[Price]:
        yf = _import_yfinance()
        if yf is None:
            return []
        try:
            df = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1d", auto_adjust=False)
            if df is None or getattr(df, "empty", True):
                return []
            out: list[Price] = []
            for idx, row in df.iterrows():
                try:
                    day_str = idx.strftime("%Y-%m-%d")
                except Exception:
                    day_str = str(idx)
                out.append(
                    Price(
                        open=float(row.get("Open")),
                        close=float(row.get("Close")),
                        high=float(row.get("High")),
                        low=float(row.get("Low")),
                        volume=int(row.get("Volume") or 0),
                        time=day_str,
                    )
                )
            return out
        except Exception as exc:
            logger.warning("YahooFinanceClient.get_prices failed for %s: %s", ticker, exc)
            return []

    def get_financial_metrics(
        self,
        ticker: str,
        end_date: str,
        period: str = "ttm",
        limit: int = 10,
    ) -> list[FinancialMetrics]:
        yf = _import_yfinance()
        if yf is None:
            return []
        try:
            info = yf.Ticker(ticker).info or {}
            market_cap = _to_float(info.get("marketCap"))
            free_cashflow = _to_float(info.get("freeCashflow"))
            shares_outstanding = _to_float(info.get("sharesOutstanding") or info.get("impliedSharesOutstanding"))

            free_cash_flow_yield = None
            if free_cashflow is not None and market_cap:
                free_cash_flow_yield = free_cashflow / market_cap

            free_cash_flow_per_share = None
            if free_cashflow is not None and shares_outstanding:
                free_cash_flow_per_share = free_cashflow / shares_outstanding

            metrics = FinancialMetrics(
                ticker=ticker,
                report_period=end_date,
                period=period,
                currency=str(info.get("currency") or info.get("financialCurrency") or "USD"),
                market_cap=market_cap,
                enterprise_value=_to_float(info.get("enterpriseValue")),
                price_to_earnings_ratio=_to_float(info.get("trailingPE")),
                price_to_book_ratio=_to_float(info.get("priceToBook")),
                price_to_sales_ratio=_to_float(info.get("priceToSalesTrailing12Months")),
                enterprise_value_to_ebitda_ratio=_to_float(info.get("enterpriseToEbitda")),
                enterprise_value_to_revenue_ratio=_to_float(info.get("enterpriseToRevenue")),
                free_cash_flow_yield=free_cash_flow_yield,
                peg_ratio=_to_float(info.get("pegRatio") or info.get("trailingPegRatio")),
                gross_margin=_to_float(info.get("grossMargins")),
                operating_margin=_to_float(info.get("operatingMargins")),
                net_margin=_to_float(info.get("profitMargins")),
                return_on_equity=_to_float(info.get("returnOnEquity")),
                return_on_assets=_to_float(info.get("returnOnAssets")),
                return_on_invested_capital=None,
                asset_turnover=None,
                inventory_turnover=None,
                receivables_turnover=None,
                days_sales_outstanding=None,
                operating_cycle=None,
                working_capital_turnover=None,
                current_ratio=_to_float(info.get("currentRatio")),
                quick_ratio=_to_float(info.get("quickRatio")),
                cash_ratio=None,
                operating_cash_flow_ratio=None,
                debt_to_equity=_to_float(info.get("debtToEquity")),
                debt_to_assets=None,
                interest_coverage=_to_float(info.get("interestCoverage")),
                revenue_growth=_to_float(info.get("revenueGrowth")),
                earnings_growth=_to_float(info.get("earningsGrowth") or info.get("earningsQuarterlyGrowth")),
                book_value_growth=None,
                earnings_per_share_growth=None,
                free_cash_flow_growth=None,
                operating_income_growth=None,
                ebitda_growth=None,
                payout_ratio=_to_float(info.get("payoutRatio")),
                earnings_per_share=_to_float(info.get("trailingEps")),
                book_value_per_share=_to_float(info.get("bookValue")),
                free_cash_flow_per_share=free_cash_flow_per_share,
            )
            _ = limit
            return [metrics]
        except Exception as exc:
            logger.warning("YahooFinanceClient.get_financial_metrics failed for %s: %s", ticker, exc)
            return []

    def get_news(
        self,
        ticker: str,
        end_date: str,
        start_date: str | None = None,
        limit: int = 1000,
    ) -> list[CompanyNews]:
        yf = _import_yfinance()
        if yf is None:
            return []
        try:
            stock = yf.Ticker(ticker)
            try:
                raw_news = stock.get_news(count=min(limit, 100), tab="news")  # type: ignore[attr-defined]
            except Exception:
                raw_news = getattr(stock, "news", None)

            news_items = raw_news or []
            out: list[CompanyNews] = []
            for item in news_items:
                content = item.get("content", item) if isinstance(item, dict) else {}
                title = str(content.get("title") or item.get("title") or "")
                publisher = content.get("publisher") or item.get("publisher") or ""
                provider = content.get("provider") or {}
                if isinstance(provider, dict) and provider.get("displayName"):
                    publisher = provider.get("displayName")

                link = ""
                canonical = content.get("canonicalUrl") or {}
                if isinstance(canonical, dict) and canonical.get("url"):
                    link = canonical.get("url")
                if not link:
                    link = str(content.get("link") or item.get("link") or "")

                published = (
                    content.get("providerPublishTime")
                    or item.get("providerPublishTime")
                    or content.get("publishedAt")
                    or item.get("publishedAt")
                )
                date_iso = _unix_ts_to_iso(published) or None
                if date_iso:
                    day = date_iso[:10]
                    if start_date and day < start_date:
                        continue
                    if end_date and day > end_date:
                        continue

                out.append(
                    CompanyNews(
                        ticker=ticker,
                        title=title,
                        source=str(publisher or ""),
                        date=date_iso,
                        url=link,
                    )
                )
                if len(out) >= limit:
                    break
            return out
        except Exception as exc:
            logger.warning("YahooFinanceClient.get_news failed for %s: %s", ticker, exc)
            return []

    def get_insider_trades(
        self,
        ticker: str,
        end_date: str,
        start_date: str | None = None,
        limit: int = 1000,
    ):
        _ = (end_date, start_date, limit)
        return []

    def get_company_facts(self, ticker: str) -> CompanyFacts | None:
        yf = _import_yfinance()
        if yf is None:
            return None
        try:
            info = yf.Ticker(ticker).info or {}
            return CompanyFacts(
                ticker=ticker,
                name=str(info.get("longName") or info.get("shortName") or ""),
                sector=info.get("sector"),
                industry=info.get("industry"),
                exchange=info.get("exchange"),
                category=info.get("category"),
                cik=info.get("cik"),
            )
        except Exception as exc:
            logger.warning("YahooFinanceClient.get_company_facts failed for %s: %s", ticker, exc)
            return None

    def get_earnings(self, ticker: str) -> Earnings | None:
        _ = ticker
        return None

