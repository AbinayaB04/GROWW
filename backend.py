import time
from typing import List, Dict, Any

import db
import price_fetcher
import anomaly_detector
import edge_cases

def update_stock(symbol: str) -> Dict[str, Any]:
    """
    Fetches latest data for a single stock, calculates anomalies,
    saves to DB, and returns the result.
    """
    try:
        data = price_fetcher.fetch_stock_data(symbol)
        if not data:
            return {"symbol": symbol, "error": "Could not fetch data"}
            
        current_price = data['current_price']
        current_date = data['date']
        
        # Save historical prices to DB
        for item in data['prices_30d']:
            db.save_price(symbol, item['date'], item['price'], item['volume'])
            
        # Get raw prices and volumes for calculation
        raw_prices = edge_cases.clean_duplicate_prices(data['prices_30d'])
        raw_volumes = [item['volume'] for item in data['prices_30d']]
        
        # Calculate anomaly
        result = {
            "symbol": symbol,
            "current_price": current_price,
            "date": current_date,
            "change_pct": 0.0,
            "status": "NORMAL",
            "sigma_distance": 0.0,
            "volume_status": "NORMAL",
            "news": [],
            "history": raw_prices # For the sparkline
        }
        
        # Calculate percentage change from yesterday (second to last item in history)
        if len(raw_prices) >= 2:
            yesterday_price = raw_prices[-2]
            result['change_pct'] = ((current_price - yesterday_price) / yesterday_price) * 100
        
        # Calculate standard deviation anomalies
        if edge_cases.has_sufficient_history(raw_prices):
            history_for_baseline = raw_prices[:-1] if len(raw_prices) > 1 else raw_prices
            volumes_for_baseline = raw_volumes[:-1] if len(raw_volumes) > 1 else raw_volumes
            current_volume = raw_volumes[-1] if raw_volumes else 0
            
            anomaly_data = anomaly_detector.detect_anomalies(
                history_for_baseline, 
                current_price,
                volumes=volumes_for_baseline,
                current_volume=current_volume
            )
            
            if anomaly_data:
                result['status'] = anomaly_data['status']
                result['sigma_distance'] = anomaly_data['sigma_distance']
                result['volume_status'] = anomaly_data['volume_status']
                
                # If there's an anomaly (price or volume), fetch news
                if anomaly_data['status'] in ['ANOMALY', 'VOL_ANOMALY']:
                    import yfinance as yf
                    ticker = yf.Ticker(symbol)
                    try:
                        # Grab top 2 news articles
                        news = ticker.news[:2]
                        result['news'] = [{"title": n.get('title', ''), "link": n.get('link', '')} for n in news]
                    except:
                        pass
                
                # Save anomaly to DB
                db.save_anomaly(
                    symbol, 
                    current_date, 
                    current_price, 
                    anomaly_data['sigma_distance'], 
                    anomaly_data['is_anomaly'], 
                    anomaly_data['status']
                )
        
        return result
        
    except Exception as e:
        print(f"Error updating {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}

def update_all_prices() -> List[Dict[str, Any]]:
    """
    Updates all stocks in the watchlist.
    """
    watchlist = db.get_watchlist()
    results = []
    
    for symbol in watchlist:
        res = update_stock(symbol)
        results.append(res)
        
    return results

def get_watchlist_with_anomalies() -> List[Dict[str, Any]]:
    """
    Main function called by UI to get the current state of the watchlist.
    """
    return update_all_prices()
