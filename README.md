# 📈 Smart Market Watchlist (Hackathon MVP)

A highly intelligent, anomaly-detecting stock market dashboard built for professional retail traders. Rather than just showing the current price, this application calculates standard deviation across both **price** and **trading volume** to alert users of unusual market activity in real-time.

## ✨ Features

- **Price Anomaly Detection:** Calculates the 30-day standard deviation ($\sigma$) of the closing price. If the price moves $>2\sigma$, it visually triggers an 🔴 **ANOMALY** alert.
- **Volume Spike Detection:** Institutional trading is often hidden in volume. The app monitors for abnormal trading volume spikes ($>2\sigma$) and flags them with a 🌊 **SPIKE** badge.
- **Automated Contextual News:** If an anomaly is detected, the app automatically fetches the top breaking news stories for that ticker to explain *why* it moved.
- **Sparkline Trend Visuals:** Instant 30-day trend lines rendered directly in the data table for quick technical context.
- **Cloud State Persistence:** Powered by Supabase (PostgreSQL). Your watchlist state and historical price calculations are saved persistently in the cloud.

## 🛠 Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) (Python)
- **Backend Logic:** Python (NumPy for Statistical Math)
- **Database:** [Supabase](https://supabase.com/) (Headless PostgreSQL)
- **Data Ingestion:** `yfinance` (Bypasses traditional rate-limited APIs by intercepting live Yahoo Finance JSON endpoints).

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd GROWW
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your Supabase credentials:
   ```ini
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

5. **Initialize Database:**
   Run the SQL provided in `schema.sql` within your Supabase SQL Editor to create the necessary tables.

6. **Run the App:**
   ```bash
   streamlit run main.py
   ```

## 🧠 Why we built it this way (Pitch)
Traditional watchlists are incredibly noisy and require the user to guess what is important. By applying a mathematical anomaly detection engine (Standard Deviation) to both Price and Volume, this app shifts the paradigm from *passive tracking* to *active alerting*, enabling traders to react to structural market changes immediately.
