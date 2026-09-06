import numpy as np
from typing import List, Dict, Any, Optional

def detect_anomalies(prices: List[float], current_price: float, volumes: List[int] = None, current_volume: int = None) -> Optional[Dict[str, Any]]:
    """
    Calculates if the current price or volume is an anomaly based on historical data.
    """
    # Edge case: not enough data
    if not prices or len(prices) < 5:
        return None
        
    prices_array = np.array(prices)
    mean_price = np.mean(prices_array)
    std_dev_price = np.std(prices_array)
    
    # Edge case: std_dev is 0 (all prices same) or NaN
    if std_dev_price == 0 or np.isnan(std_dev_price):
        return None
        
    # Calculate price sigmas
    sigma_distance = abs(current_price - mean_price) / std_dev_price
    
    status = 'NORMAL'
    explanation = f'Price is {sigma_distance:.2f}σ away (normal volatility)'
    
    if sigma_distance > 2:
        status = 'ANOMALY'
        explanation = f'Price is {sigma_distance:.2f}σ away (moved significantly more than usual)'
    elif sigma_distance > 1:
        status = 'WARNING'
        explanation = f'Price is {sigma_distance:.2f}σ away (moved more than usual)'

    # Volume Anomaly Detection
    volume_status = 'NORMAL'
    volume_sigma = 0.0
    if volumes and current_volume is not None and len(volumes) >= 5:
        vol_array = np.array(volumes)
        mean_vol = np.mean(vol_array)
        std_dev_vol = np.std(vol_array)
        if std_dev_vol > 0 and not np.isnan(std_dev_vol):
            volume_sigma = (current_volume - mean_vol) / std_dev_vol
            if volume_sigma > 2:
                volume_status = 'ANOMALY'
                if status == 'NORMAL':
                    status = 'VOL_ANOMALY'
                    explanation = f'Volume spiked {volume_sigma:.2f}σ above normal (institutional activity?)'

    return {
        'current_price': round(current_price, 2),
        'mean': round(mean_price, 2),
        'std_dev': round(std_dev_price, 2),
        'sigma_distance': round(sigma_distance, 2),
        'status': status,
        'explanation': explanation,
        'is_anomaly': bool(sigma_distance > 2),
        'volume_status': volume_status,
        'volume_sigma': round(volume_sigma, 2)
    }
