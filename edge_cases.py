import datetime
from typing import List, Dict, Any

def has_sufficient_history(prices: List[float], min_days: int = 5) -> bool:
    """Check if we have enough price history to calculate std dev meaningfully."""
    return len(prices) >= min_days

def is_market_closed(current_time: datetime.datetime = None) -> bool:
    """
    Very basic check if market is closed (weekends).
    More advanced version would check exchange holidays.
    """
    if current_time is None:
        current_time = datetime.datetime.now()
    
    # 5 is Saturday, 6 is Sunday
    return current_time.weekday() >= 5

def clean_duplicate_prices(prices_data: List[Dict[str, Any]]) -> List[float]:
    """
    Extracts closing prices and removes consecutive identical prices 
    if they represent a data error (though sometimes prices don't move).
    For standard deviation, we'll just take the raw closing prices.
    """
    return [item['price'] for item in prices_data]
