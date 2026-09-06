import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional

def fetch_stock_data(symbol: str, days: int = 30) -> Optional[Dict[str, Any]]:
    """
    Fetches the latest daily closing price and historical prices for a stock symbol.
    Uses yfinance to avoid API keys and rate limits.
    """
    try:
        # yfinance uses '.NS' suffix for NSE (India) stocks.
        # e.g., RELIANCE.NS, TCS.NS. For US stocks like AAPL, no suffix is needed.
        ticker = yf.Ticker(symbol)
        
        # Get historical data for the last 1 year (to ensure we get enough trading days)
        # We will filter down to the requested 'days' of trading days.
        hist = ticker.history(period="3mo")
        
        if hist.empty:
            print(f"Warning: No data found for symbol {symbol}")
            return None
            
        # Get the last 'days' rows
        hist = hist.tail(days)
        
        if hist.empty:
            return None
            
        current_data = hist.iloc[-1]
        current_price = float(current_data['Close'])
        current_date = hist.index[-1].strftime('%Y-%m-%d')
        
        prices_history = []
        for index, row in hist.iterrows():
            prices_history.append({
                'date': index.strftime('%Y-%m-%d'),
                'price': float(row['Close']),
                'volume': int(row['Volume'])
            })
            
        return {
            'symbol': symbol,
            'current_price': current_price,
            'date': current_date,
            'prices_30d': prices_history
        }
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def fetch_current_price(symbol: str) -> Optional[float]:
    """Fetches just the most recent closing price."""
    data = fetch_stock_data(symbol, days=1)
    if data:
        return data['current_price']
    return None
