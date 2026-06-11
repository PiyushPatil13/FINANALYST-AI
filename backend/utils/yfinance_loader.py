import yfinance as ticker_engine
import pandas as pd

class YFinanceLoader:
    def __init__(self, ticker_symbol: str):
        self.ticker_symbol = ticker_symbol.upper()
        self.stock = ticker_engine.Ticker(ticker_symbol)

    def get_ticker_summary(self) -> dict:
        """Fetches fundamental data and key ratios."""
        info = self.stock.info
        return {
            "ticker": self.ticker_symbol,
            "name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "current_price": info.get("currentPrice", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
            "summary": info.get("longBusinessSummary", "N/A")
        }

    def get_recent_news(self) -> list:
        """Fetches and cleans recent news headlines."""
        raw_news = self.stock.news
        cleaned = []
        for item in raw_news[:5]:        # top 5 only
            content = item.get("content", {})
            cleaned.append({
                "title": content.get("title", "N/A"),
                "summary": content.get("summary", "N/A"),
                "url": content.get("canonicalUrl", {}).get("url", "N/A"),
            })
        return cleaned

    def get_financial_statements(self) -> str:
        """
        Fetches quarterly financials as a readable string for LLM.
        Returns empty string if data unavailable.
        """
        try:
            df = self.stock.quarterly_financials
            if df.empty:
                return "Financial statements not available."
            # to_string() works without tabulate dependency
            return df.to_string()
        except Exception as e:
            return f"Could not fetch financials: {str(e)}"

    def get_historical_prices(self, period: str = "1y") -> list:
        """
        Returns historical closing prices for charting.
        Period options: 1mo, 3mo, 6mo, 1y, 2y
        """
        try:
            hist = self.stock.history(period=period)
            if hist.empty:
                return []
            hist = hist.reset_index()
            return [
                {
                    "date": str(row["Date"].date()),
                    "close": round(row["Close"], 2)
                }
                for _, row in hist.iterrows()
            ]
        except Exception as e:
            return []