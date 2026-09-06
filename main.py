import streamlit as st
import pandas as pd
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# We only import backend and db if env vars are present to avoid crash on startup
try:
    import db
    import backend
    ENV_LOADED = True
except Exception as e:
    ENV_LOADED = False
    ENV_ERROR = str(e)

st.set_page_config(
    page_title="Smart Market Watchlist",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 Smart Market Watchlist")

if not ENV_LOADED:
    st.error("Failed to load environment variables or connect to Database.")
    st.write(f"Error details: {ENV_ERROR}")
    st.warning("Please ensure `.env` file exists with `SUPABASE_URL` and `SUPABASE_KEY`.")
    st.stop()

# --- Sidebar ---
st.sidebar.header("Controls")
new_stock = st.sidebar.text_input("Add Stock Symbol (e.g. RELIANCE.NS, AAPL):", key="new_stock_input")
if st.sidebar.button("Add to Watchlist"):
    if new_stock:
        symbol = new_stock.strip().upper()
        if db.add_stock(symbol):
            st.sidebar.success(f"Added {symbol}!")
            st.cache_data.clear()
            st.rerun()
        else:
            st.sidebar.warning(f"{symbol} is already in the watchlist.")

st.sidebar.markdown("---")
filter_status = st.sidebar.radio(
    "Filter by Status:",
    ["All", "Warnings Only", "Anomalies Only"]
)

sort_by = st.sidebar.selectbox(
    "Sort by:",
    ["Symbol", "Price", "% Change", "Anomaly Score (Sigma)"]
)

if st.sidebar.button("Manual Refresh"):
    st.cache_data.clear()
    st.rerun()

# --- Main Logic ---

@st.cache_data(ttl=60) # Cache for 60 seconds
def load_data():
    return backend.get_watchlist_with_anomalies()

with st.spinner("Fetching latest market data..."):
    data = load_data()

if not data:
    st.info("Your watchlist is empty. Add a stock from the sidebar!")
else:
    # Convert to DataFrame for easier filtering/sorting
    df = pd.DataFrame(data)
    
    # Filter out errors
    errors_df = df[df['error'].notna()] if 'error' in df.columns else pd.DataFrame()
    if not errors_df.empty:
        for _, row in errors_df.iterrows():
            st.error(f"Error for {row['symbol']}: {row['error']}")
            
    # Valid data
    valid_df = df[df['error'].isna()] if 'error' in df.columns else df
    
    if not valid_df.empty:
        # Apply Filters
        if filter_status == "Warnings Only":
            valid_df = valid_df[valid_df['status'].isin(['WARNING', 'ANOMALY'])]
        elif filter_status == "Anomalies Only":
            valid_df = valid_df[valid_df['status'] == 'ANOMALY']
            
        # Apply Sorting
        if sort_by == "Symbol":
            valid_df = valid_df.sort_values(by="symbol")
        elif sort_by == "Price":
            valid_df = valid_df.sort_values(by="current_price", ascending=False)
        elif sort_by == "% Change":
            valid_df = valid_df.sort_values(by="change_pct", ascending=False)
        elif sort_by == "Anomaly Score (Sigma)":
            valid_df = valid_df.sort_values(by="sigma_distance", ascending=False)

        # Display Data
        st.markdown("### Watchlist")
        
        # Create columns for headers
        cols = st.columns((2, 2, 2, 2, 2, 2, 2, 1))
        cols[0].write("**Symbol**")
        cols[1].write("**Price**")
        cols[2].write("**% Change**")
        cols[3].write("**30D Trend**")
        cols[4].write("**Price Status**")
        cols[5].write("**Volume Status**")
        cols[6].write("**Score (σ)**")
        cols[7].write("**Action**")
        
        st.markdown("---")
        
        for _, row in valid_df.iterrows():
            cols = st.columns((2, 2, 2, 2, 2, 2, 2, 1))
            
            # Symbol
            cols[0].write(f"**{row['symbol']}**")
            
            # Price
            cols[1].write(f"{row['current_price']:,.2f}")
            
            # Change
            change_color = "green" if row['change_pct'] >= 0 else "red"
            cols[2].markdown(f"<span style='color:{change_color}'>{row['change_pct']:+.2f}%</span>", unsafe_allow_html=True)
            
            # Sparkline
            history = row.get('history', [])
            if history:
                # We use a tiny line chart. Hide axes to make it look like a sparkline.
                chart_df = pd.DataFrame(history, columns=["Price"])
                cols[3].line_chart(chart_df, height=60)
            
            # Price Status Badge
            status = row.get('status', 'NORMAL')
            if status == "ANOMALY":
                badge = "🔴 ANOMALY"
            elif status == "WARNING":
                badge = "🟠 WARNING"
            elif status == "VOL_ANOMALY":
                badge = "🟢 Normal" # Price is normal, but volume isn't
            else:
                badge = "🟢 Normal"
            cols[4].write(badge)
            
            # Volume Status Badge
            v_status = row.get('volume_status', 'NORMAL')
            if v_status == "ANOMALY":
                v_badge = "🌊 SPIKE"
            else:
                v_badge = "🟢 Normal"
            cols[5].write(v_badge)
            
            # Sigma
            p_sigma = row.get('sigma_distance', 0)
            v_sigma = row.get('volume_sigma', 0)
            highest_sigma = max(p_sigma, v_sigma)
            cols[6].write(f"{highest_sigma:.2f}σ")
            
            # Remove Button
            if cols[7].button("X", key=f"del_{row['symbol']}"):
                db.remove_stock(row['symbol'])
                st.cache_data.clear()
                st.rerun()
                
            # Expandable News Section if Anomaly
            if status in ["ANOMALY", "VOL_ANOMALY"] or v_status == "ANOMALY":
                news = row.get('news', [])
                if news:
                    with st.expander(f"📰 Context for {row['symbol']} movement"):
                        for n in news:
                            st.markdown(f"- [{n['title']}]({n['link']})")
                else:
                    with st.expander(f"📰 Context for {row['symbol']} movement"):
                        st.write("No recent news found.")
                        
            st.markdown("---")

st.markdown("---")
st.caption(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Data fetches automatically cache for 60 seconds.")
