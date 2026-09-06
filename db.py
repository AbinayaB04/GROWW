import os
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Initialize and return the Supabase client."""
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in environment variables.")
        
    return create_client(url, key)

def initialize_tables():
    """
    Note: Supabase does not support DDL (CREATE TABLE) directly through the REST API 
    using the standard python client in this way easily without RPC. 
    It's highly recommended to run the SQL script provided in the README 
    in the Supabase SQL Editor to create the tables.
    """
    pass

def add_stock(symbol: str):
    """Add a stock to the watchlist."""
    supabase = get_supabase_client()
    # Check if exists
    existing = supabase.table("watchlist_stocks").select("*").eq("symbol", symbol).execute()
    if len(existing.data) == 0:
        supabase.table("watchlist_stocks").insert({"symbol": symbol}).execute()
        return True
    return False

def remove_stock(symbol: str):
    """Remove a stock from the watchlist."""
    supabase = get_supabase_client()
    supabase.table("watchlist_stocks").delete().eq("symbol", symbol).execute()

def get_watchlist():
    """Return all stocks in the watchlist."""
    supabase = get_supabase_client()
    response = supabase.table("watchlist_stocks").select("symbol").execute()
    return [row["symbol"] for row in response.data]

def save_price(symbol: str, date_str: str, price: float, volume: int):
    """Save daily price for a stock."""
    supabase = get_supabase_client()
    # Check if price for this date already exists
    existing = supabase.table("stock_prices").select("*").eq("symbol", symbol).eq("date", date_str).execute()
    if len(existing.data) == 0:
        supabase.table("stock_prices").insert({
            "symbol": symbol,
            "date": date_str,
            "price": price,
            "volume": volume
        }).execute()
    else:
        # Update if exists
        supabase.table("stock_prices").update({
            "price": price,
            "volume": volume
        }).eq("symbol", symbol).eq("date", date_str).execute()

def get_prices(symbol: str, days: int = 30):
    """Return last N days of prices for a stock."""
    supabase = get_supabase_client()
    response = supabase.table("stock_prices").select("*").eq("symbol", symbol).order("date", desc=True).limit(days).execute()
    return response.data

def save_anomaly(symbol: str, date_str: str, price: float, std_dev_distance: float, is_anomaly: bool, status: str):
    """Save an anomaly record."""
    supabase = get_supabase_client()
    supabase.table("anomalies").insert({
        "symbol": symbol,
        "date": date_str,
        "price": float(price),
        "std_dev_distance": float(std_dev_distance),
        "is_anomaly": is_anomaly,
        "status": status
    }).execute()
