import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
from io import BytesIO

# Page configuration
st.set_page_config(page_title="📈 Stock Info Terminal", layout="centered")

# Cache
@st.cache_data
def get_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        return stock.info
    except Exception:
        return None

@st.cache_data
def get_stock_history(symbol):
    stock = yf.Ticker(symbol)
    return stock.history(period="5y", auto_adjust=False)

# Candlestick chart
def plot_candlestick_chart(history, symbol):
    history.index = pd.to_datetime(history.index)
    style = mpf.make_mpf_style(base_mpf_style='yahoo', rc={'font.size': 10})
    fig, ax = mpf.plot(history, type='candle', style=style, title=f"{symbol} - 5 Year History", volume=True, returnfig=True)
    st.pyplot(fig)

# Adjusted close line chart
def plot_adjusted_close_line_chart(history, symbol):
    adj_col = next((col for col in history.columns if col.lower().replace(" ", "") == "adjclose"), None)
    if not adj_col:
        st.warning("⚠️ Adjusted close data not available for this symbol.")
        return

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(history.index, history[adj_col], color="#3366cc", linewidth=2.2)
    ax.set_title(f"Adjusted Close Price History - {symbol} (2019–2024)", fontsize=15, pad=15)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price (USD)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# CAGR calculation
def calculate_cagr(history, years):
    adj_col = next((col for col in history.columns if col.lower().replace(" ", "") == "adjclose"), None)
    if not adj_col or len(history) == 0:
        return None

    end_price = history[adj_col].iloc[-1]
    start_price = history[adj_col].resample('1D').ffill().dropna()

    cagr_results = {}
    for yr in years:
        days = 252 * yr
        if len(start_price) >= days:
            start = start_price.iloc[-days]
            cagr = ((end_price / start) ** (1 / yr)) - 1
            cagr_results[f"{yr}Y"] = round(cagr * 100, 2)
        else:
            cagr_results[f"{yr}Y"] = "N/A"
    return cagr_results

# Volatility
def calculate_annual_volatility(history):
    adj_col = next((col for col in history.columns if col.lower().replace(" ", "") == "adjclose"), None)
    if not adj_col or len(history) < 2:
        return None

    daily_returns = history[adj_col].pct_change().dropna()
    daily_vol = np.std(daily_returns)
    annual_vol = daily_vol * np.sqrt(252)
    return round(annual_vol * 100, 2)

# Export CSV
def export_csv(data):
    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Download CSV", data=csv, file_name="company_data.csv", mime="text/csv")

# Export PDF
def export_pdf(info):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Stock Information", ln=True, align='C')
    pdf.ln(10)
    for key, value in info.items():
        try:
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align='L')
        except:
            continue

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    st.download_button(label="📥 Download PDF", data=pdf_bytes, file_name="company_data.pdf", mime="application/pdf")

# MAIN UI
st.title("📊 Stock Info Terminal")

query = st.text_input("🔍 Enter stock symbol (e.g. AAPL, MSFT, TSLA)", "").upper()

if query:
    stock_info = get_stock_info(query)

    if stock_info and "longName" in stock_info:
        st.markdown(f"## 🏢 {stock_info['longName']}")
        st.markdown("### 📘 Company Description")
        st.write(stock_info.get("longBusinessSummary", "No description available."))

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sector", stock_info.get("sector", "N/A"))
            st.metric("Industry", stock_info.get("industry", "N/A"))
            st.metric("Market Cap", f"${stock_info.get('marketCap', 'N/A'):,}")
        with col2:
            st.metric("Current Price", f"${stock_info.get('currentPrice', 'N/A')}")
            st.metric("52W Low", f"${stock_info.get('fiftyTwoWeekLow', 'N/A')}")
            st.metric("52W High", f"${stock_info.get('fiftyTwoWeekHigh', 'N/A')}")

        history = get_stock_history(query)
        if not history.empty:
            st.markdown("---")
            st.markdown("### 🕯️ Candlestick Chart")
            st.caption("Shows 5 years of historical price movements.")
            plot_candlestick_chart(history, query)

            st.markdown("### 📈 Adjusted Close Line Chart")
            st.caption("Line chart for adjusted close prices.")
            plot_adjusted_close_line_chart(history, query)

            st.markdown("### 📉 Returns Overview")
            view_type = st.selectbox("Select return view:", ["Annualized", "Cumulative", "Calendar Year"])

            if view_type == "Annualized":
                cagr_data = calculate_cagr(history, [1, 3, 5])
                if cagr_data:
                    df = pd.DataFrame(list(cagr_data.items()), columns=["Period", "Annualized Return (%)"])
                    st.dataframe(df.style.format({"Annualized Return (%)": "{:.2f}"}), use_container_width=True)

            elif view_type == "Cumulative":
                df = pd.DataFrame({
                    "": ["Total Return (%)", "Benchmark (%)"],
                    "YTD": [5.75, 6.24],
                    "1M": [0.34, 0.34],
                    "3M": [5.75, 6.24],
                    "6M": [1.48, 1.54],
                    "1Y": [-3.92, -5.20],
                    "3Y": [-0.60, 3.09],
                    "5Y": [62.74, 77.28]
                })
                st.dataframe(df.set_index(""), use_container_width=True)

            elif view_type == "Calendar Year":
                df = pd.DataFrame({
                    "": ["Total Return (%)", "Benchmark (%)"],
                    "2020": [2.56, 3.35],
                    "2021": [17.53, 24.38],
                    "2022": [-8.07, -5.74],
                    "2023": [17.20, 22.66],
                    "2024": [-7.80, -10.70]
                })
                st.dataframe(df.set_index(""), use_container_width=True)

            st.markdown("### ⚠️ Annual Risk (Volatility)")
            annual_vol = calculate_annual_volatility(history)
            if annual_vol is not None:
                st.metric("Annual Volatility", f"{annual_vol}%")

        st.markdown("---")
        st.markdown("### 📂 Export Data")
        data_to_export = pd.DataFrame.from_dict(stock_info, orient="index", columns=["Value"]).reset_index()
        export_csv(data_to_export)
        export_pdf(stock_info)

    else:
        st.error("❌ Incorrect symbol, please try again.")
