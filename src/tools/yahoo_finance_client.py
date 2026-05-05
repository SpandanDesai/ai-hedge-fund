from __future__ import annotations

import datetime as _dt
import logging
from typing import Any

from src.data.models import CompanyFacts, CompanyNews, FinancialMetrics, LineItem, Price

logger = logging.getLogger(__name__)


def _import_yfinance():
    try:
        import yfinance as yf  # type: ignore

        return yf
    except Exception as exc:  # pragma: no cover
        logger.warning("yfinance is not available (%s). Install it to use DATA_SOURCE=yahoo.", exc)
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


_POS_WORDS = {
    "beat",
    "beats",
    "surge",
    "surges",
    "soar",
    "soars",
    "jump",
    "jumps",
    "rally",
    "rallies",
    "upgrade",
    "upgrades",
    "raises",
    "raise",
    "record",
    "growth",
    "profits",
    "profit",
    "strong",
    "outperform",
    "buy",
}
_NEG_WORDS = {
    "miss",
    "misses",
    "drop",
    "drops",
    "fall",
    "falls",
    "plunge",
    "plunges",
    "downgrade",
    "downgrades",
    "cuts",
    "cut",
    "lawsuit",
    "probe",
    "investigation",
    "weak",
    "underperform",
    "sell",
}


def _headline_sentiment(title: str) -> str | None:
    text = (title or "").lower()
    if not text:
        return None
    pos = sum(1 for w in _POS_WORDS if w in text)
    neg = sum(1 for w in _NEG_WORDS if w in text)
    if pos > neg and pos > 0:
        return "positive"
    if neg > pos and neg > 0:
        return "negative"
    if pos == neg and pos > 0:
        return "neutral"
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
    """Yahoo Finance data client (via yfinance).

    Methods are best-effort and never raise â€” they return empty lists/None on failure.
    """

    def get_prices(self, ticker: str, start_date: str, end_date: str, **kwargs) -> list[Price]:
        yf = _import_yfinance()
        if yf is None:
            return []

        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date, interval="1d", auto_adjust=False)
            if df is None or getattr(df, "empty", True):
                return []

            prices: list[Price] = []
            for idx, row in df.iterrows():
                # yfinance uses a DatetimeIndex; normalize to YYYY-MM-DD for compatibility.
                try:
                    day_str = idx.strftime("%Y-%m-%d")
                except Exception:
                    day_str = str(idx)

                prices.append(
                    Price(
                        open=float(row.get("Open")),
                        close=float(row.get("Close")),
                        high=float(row.get("High")),
                        low=float(row.get("Low")),
                        volume=int(row.get("Volume") or 0),
                        time=day_str,
                    )
                )
            return prices
        except Exception as exc:
            logger.warning("YahooFinanceClient.get_prices failed for %s: %s", ticker, exc)
            return []

    def get_financial_metrics(
        self,
        ticker: str,
        end_date: str,
        period: str = "ttm",
        limit: int = 10,
        **kwargs,
    ) -> list[FinancialMetrics]:
        yf = _import_yfinance()
        if yf is None:
            return []

        try:
            info = yf.Ticker(ticker).info or {}

            market_cap = _to_float(info.get("marketCap"))
            free_cashflow = _to_float(info.get("freeCashflow"))
            shares_outstanding = _to_float(info.get("sharesOutstanding") or info.get("impliedSharesOutstanding"))
            total_debt = _to_float(info.get("totalDebt"))
            total_assets = _to_float(info.get("totalAssets"))

            free_cash_flow_yield = None
            if free_cashflow is not None and market_cap:
                free_cash_flow_yield = free_cashflow / market_cap

            free_cash_flow_per_share = None
            if free_cashflow is not None and shares_outstanding:
                free_cash_flow_per_share = free_cashflow / shares_outstanding

            debt_to_assets = None
            if total_debt is not None and total_assets:
                debt_to_assets = total_debt / total_assets

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
                debt_to_assets=debt_to_assets,
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
            # Yahoo's info is current-only; return one record.
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
        **kwargs,
    ) -> list[CompanyNews]:
        yf = _import_yfinance()
        if yf is None:
            return []

        try:
            stock = yf.Ticker(ticker)

            # Prefer get_news(count=...) when available, else fall back to .news
            try:
                raw_news = stock.get_news(count=min(limit, 100), tab="news")  # type: ignore[attr-defined]
            except Exception:
                raw_news = getattr(stock, "news", None)

            news_items = raw_news or []
            out: list[CompanyNews] = []

            start = start_date or None
            end = end_date or None

            for item in news_items:
                # yfinance sometimes nests content under "content"
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
                date_iso = _unix_ts_to_iso(published) or str(published or "")

                # Filter by requested date window when we can (date string is YYYY-MM-DD...).
                date_day = (date_iso or "")[:10]
                if start and date_day and date_day < start:
                    continue
                if end and date_day and date_day > end:
                    continue

                out.append(
                    CompanyNews(
                        ticker=ticker,
                        title=title,
                        source=str(publisher or ""),
                        date=date_iso,
                        url=link,
                        sentiment=_headline_sentiment(title),
                    )
                )

                if len(out) >= limit:
                    break

            return out
        except Exception as exc:
            logger.warning("YahooFinanceClient.get_news failed for %s: %s", ticker, exc)
            return []

    def get_company_facts(self, ticker: str, **kwargs) -> CompanyFacts | None:
        yf = _import_yfinance()
        if yf is None:
            return None

        try:
            info = yf.Ticker(ticker).info or {}
            return CompanyFacts(
                ticker=ticker,
                name=str(info.get("longName") or info.get("shortName") or ""),
                industry=info.get("industry"),
                sector=info.get("sector"),
                exchange=info.get("exchange"),
                market_cap=_to_float(info.get("marketCap")),
                website_url=info.get("website"),
            )
        except Exception as exc:
            logger.warning("YahooFinanceClient.get_company_facts failed for %s: %s", ticker, exc)
            return None

    def search_line_items(
        self,
        ticker: str,
        line_items: list[str],
        end_date: str,
        period: str = "ttm",
        limit: int = 10,
        **kwargs,
    ) -> list[LineItem]:
        """Best-effort line item lookup from Yahoo financial statements.

        This is not a 1:1 replacement for Financial Datasets' line-items search.
        We attempt to map a small set of common names used by existing agents.
        """
        yf = _import_yfinance()
        if yf is None:
            return []

        # Map requested period names to yfinance frequencies.
        freq = "yearly"
        if period in {"quarter", "quarterly"}:
            freq = "quarterly"
        elif period in {"ttm", "trailing"}:
            freq = "trailing"

        try:
            stock = yf.Ticker(ticker)

            # Use pretty row names for better matching.
            try:
                income = stock.get_income_stmt(freq=freq, pretty=True)  # type: ignore[attr-defined]
            except Exception:
                income = getattr(stock, "income_stmt", None) if freq == "yearly" else getattr(stock, f"{freq}_income_stmt", None)

            try:
                balance = stock.get_balance_sheet(freq="yearly" if freq == "trailing" else freq, pretty=True)  # type: ignore[attr-defined]
            except Exception:
                balance = getattr(stock, "balance_sheet", None) if freq == "yearly" else getattr(stock, f"{freq}_balance_sheet", None)

            try:
                cashflow = stock.get_cashflow(freq=freq, pretty=True)  # type: ignore[attr-defined]
            except Exception:
                cashflow = getattr(stock, "cashflow", None) if freq == "yearly" else getattr(stock, f"{freq}_cashflow", None)

            # Convert to dict-of-dicts: {line_name: {date: value}}
            def _table_lookup(table, row_names: list[str], col) -> float | None:
                if table is None or getattr(table, "empty", True):
                    return None
                for rn in row_names:
                    if rn in table.index:
                        try:
                            return _to_float(table.loc[rn, col])
                        except Exception:
                            continue
                return None

            # Determine report periods from the income statement columns; fall back to balance/cashflow.
            cols = []
            for t in (income, balance, cashflow):
                if t is not None and not getattr(t, "empty", True):
                    cols = list(getattr(t, "columns", []))
                    break
            if not cols:
                return []

            # Most-recent first; cap by limit.
            cols = cols[:limit]

            info = stock.info or {}
            currency = str(info.get("currency") or info.get("financialCurrency") or "USD")

            # Requested line item -> candidate row names across statements / info keys
            mapping: dict[str, dict[str, Any]] = {
                "revenue": {"table": "income", "rows": ["Total Revenue", "Operating Revenue"]},
                "net_income": {"table": "income", "rows": ["Net Income", "Net Income Common Stockholders"]},
                "earnings_per_share": {"table": "income", "rows": ["Diluted EPS", "Basic EPS"]},
                "book_value_per_share": {"table": "info", "key": "bookValue"},
                "total_assets": {"table": "balance", "rows": ["Total Assets"]},
                "total_liabilities": {"table": "balance", "rows": ["Total Liabilities Net Minority Interest", "Total Liabilities"]},
                "current_assets": {"table": "balance", "rows": ["Current Assets", "Total Current Assets"]},
                "current_liabilities": {"table": "balance", "rows": ["Current Liabilities", "Total Current Liabilities"]},
                "dividends_and_other_cash_distributions": {"table": "cashflow", "rows": ["Cash Dividends Paid", "Dividends Paid"]},
                "outstanding_shares": {"table": "info", "key": "sharesOutstanding"},
            }

            out: list[LineItem] = []
            for col in cols:
                # Convert report_period column (Timestamp/date) to YYYY-MM-DD
                try:
                    report_period = col.date().strftime("%Y-%m-%d")
                except Exception:
                    report_period = str(col)

                payload: dict[str, Any] = {
                    "ticker": ticker,
                    "report_period": report_period,
                    "period": period,
                    "currency": currency,
                }

                for requested in line_items:
                    spec = mapping.get(requested)
                    if not spec:
                        payload[requested] = None
                        continue

                    if spec["table"] == "info":
                        payload[requested] = _to_float(info.get(spec.get("key")))
                        continue

                    table = income if spec["table"] == "income" else balance if spec["table"] == "balance" else cashflow
                    payload[requested] = _table_lookup(table, spec.get("rows", []), col)

                out.append(LineItem(**payload))

            return out
        except Exception as exc:
            logger.warning("YahooFinanceClient.search_line_items failed for %s: %s", ticker, exc)
            return []

