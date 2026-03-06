import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.express as px

from services.stock_service import get_stock_data, get_fundamentals
from services.news_service import get_news
from services.sentiment_service import analyze_sentiment
from utils.indicators import add_indicators
from database.db import create_table, add_stock, get_watchlist, remove_stock
from fpdf import FPDF

st.caption("AI-powered financial research platform for technical, fundamental and sentiment analysis of stocks.")

# -----------------------------
# INITIALIZE DATABASE
# -----------------------------
create_table()

st.title("📈 Financial Research AI Agent")

# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
if "data" not in st.session_state:
    st.session_state.data = None

if "fundamentals" not in st.session_state:
    st.session_state.fundamentals = None

if "sentiment" not in st.session_state:
    st.session_state.sentiment = None

if "analyzed" not in st.session_state:
    st.session_state.analyzed = False


# -----------------------------
# STOCK INPUT
# -----------------------------
symbol = st.text_input("Enter Stock Symbol (Example: TCS.NS)")
compare_symbol = st.text_input("Compare With Another Stock (Optional)")


# -----------------------------
# ANALYZE BUTTON
# -----------------------------
if st.button("Analyze Stock"):
    st.session_state.analyzed = True


# -----------------------------
# MAIN ANALYSIS
# -----------------------------
if st.session_state.analyzed:

    data = get_stock_data(symbol)

    if data.empty:
        st.error("Invalid stock symbol. Try symbols like TCS.NS or INFY.NS")
        st.stop()

    data = add_indicators(data)
    data = data.reset_index()

    rsi = data["RSI"].iloc[-1]

    # -----------------------------
    # PRICE CHART
    # -----------------------------
    st.subheader("📊 Stock Price Chart")

    fig = px.line(
        data,
        x="Date",
        y=["Close", "MA20", "MA50"],
        title=f"{symbol} Price Analysis"
    )

    st.plotly_chart(fig)

    # -----------------------------
    # RSI CHART
    # -----------------------------
    st.subheader("📉 RSI Indicator")

    rsi_fig = px.line(
        data,
        x="Date",
        y="RSI",
        title="Relative Strength Index"
    )

    st.plotly_chart(rsi_fig)

    # -----------------------------
    # FUNDAMENTALS
    # -----------------------------
    st.subheader("📑 Fundamental Analysis")

    fundamentals = get_fundamentals(symbol)

    st.write("Market Cap:", fundamentals["Market Cap"])
    st.write("PE Ratio:", fundamentals["PE Ratio"])
    st.write("EPS:", fundamentals["EPS"])
    st.write("Revenue:", fundamentals["Revenue"])

    # -----------------------------
    # SIMPLE EXPLANATION
    # -----------------------------
    rsi = data["RSI"].iloc[-1]
    st.subheader("📘 Simple Explanation")
    if fundamentals["PE Ratio"] and fundamentals["PE Ratio"] > 25:
        st.write("This stock looks slightly expensive compared to typical companies.")

    elif fundamentals["PE Ratio"] and fundamentals["PE Ratio"] < 15:
        st.write("This stock may be undervalued based on its earnings.")

    else:
        st.write("This stock is fairly priced based on its earnings.")

    if rsi < 30:
        st.write("The stock is oversold. Sometimes this means the price may rise soon.")

    elif rsi > 70:
        st.write("The stock is overbought. Sometimes this means the price may fall soon.")

    else:
        st.write("The stock price is moving normally without extreme buying or selling.")   

    # -----------------------------
    # NEWS + SENTIMENT
    # -----------------------------
    st.subheader("📰 News Sentiment")

    news = get_news(symbol)
    sentiment = analyze_sentiment(news)

    st.write("Positive:", sentiment["positive"])
    st.write("Negative:", sentiment["negative"])
    st.write("Neutral:", sentiment["neutral"])

    st.subheader("Latest News")

    for article in news:
        st.write(article["title"])
        st.write(article["url"])

    # -----------------------------
    # SAVE DATA IN SESSION STATE
    # -----------------------------
    st.session_state.data = data
    st.session_state.fundamentals = fundamentals
    st.session_state.sentiment = sentiment

    # -----------------------------
    # STOCK COMPARISON
    # -----------------------------
    if compare_symbol:

        st.subheader("📊 Stock Comparison")

        data1 = get_stock_data(symbol)
        data2 = get_stock_data(compare_symbol)

        data1 = data1.reset_index()
        data2 = data2.reset_index()

        data1["Stock"] = symbol
        data2["Stock"] = compare_symbol

        combined = data1[["Date", "Close", "Stock"]]
        combined2 = data2[["Date", "Close", "Stock"]]

        final = pd.concat([combined, combined2])

        fig = px.line(
            final,
            x="Date",
            y="Close",
            color="Stock",
            title=f"{symbol} vs {compare_symbol}"
        )

        st.plotly_chart(fig)

    # -----------------------------
    # PORTFOLIO ESTIMATION
    # -----------------------------
    st.subheader("💰 Portfolio Estimation")

    investment = st.number_input("Investment Amount (₹)", min_value=0)

    if investment > 0:

        current_price = data["Close"].iloc[-1]
        shares = int(investment / current_price)

        st.write("Current Price:", round(current_price, 2))
        st.write("Estimated Shares:", shares)

    # -----------------------------
    # AI INVESTMENT RECOMMENDATION
    # -----------------------------
    st.subheader("🤖 AI Investment Recommendation")

    rsi = data["RSI"].iloc[-1]

    if rsi < 30 and sentiment["positive"] > sentiment["negative"]:
        recommendation = "BUY"
        reason = "The stock is oversold and news sentiment is positive."

    elif rsi > 70 and sentiment["negative"] > sentiment["positive"]:
        recommendation = "SELL"
        reason = "The stock is overbought and news sentiment is negative."

    else:
        recommendation = "HOLD"
        reason = "The stock is in a neutral range."

    st.success(f"Recommendation: {recommendation}")
    st.write(reason)


    # -----------------------------
    # WATCHLIST ADD
    # -----------------------------
    if st.button("Add to Watchlist"):
        add_stock(symbol)
        st.success("Stock added to watchlist")


# -----------------------------
# WATCHLIST DISPLAY
# -----------------------------
st.subheader("⭐ Watchlist")

stocks = get_watchlist()

for s in stocks:

    col1, col2 = st.columns([3, 1])

    col1.write(s[0])

    if col2.button("Remove", key=s[0]):
        remove_stock(s[0])
        st.rerun()


# -----------------------------
# REPORT EXPORT
# -----------------------------
st.subheader("📄 Export Report")


def generate_report(symbol, data, fundamentals, sentiment):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial","B",16)
    pdf.cell(200,10,f"Financial Research Report: {symbol}",ln=True)

    pdf.set_font("Arial",size=12)
    pdf.cell(200,10,"Generated by Financial Research AI Agent",ln=True)

    pdf.ln(10)

    price = round(data["Close"].iloc[-1],2)
    rsi = round(data["RSI"].iloc[-1],2)

    pdf.cell(200,10,f"Current Stock Price: {price}",ln=True)
    pdf.cell(200,10,f"RSI Indicator: {rsi}",ln=True)

    pdf.ln(5)

    pdf.cell(200,10,"Fundamental Analysis",ln=True)

    pdf.cell(200,10,f"Market Cap: {fundamentals['Market Cap']}",ln=True)
    pdf.cell(200,10,f"PE Ratio: {fundamentals['PE Ratio']}",ln=True)
    pdf.cell(200,10,f"EPS: {fundamentals['EPS']}",ln=True)
    pdf.cell(200,10,f"Revenue: {fundamentals['Revenue']}",ln=True)

    pdf.ln(5)

    pdf.cell(200,10,"News Sentiment",ln=True)

    pdf.cell(200,10,f"Positive News: {sentiment['positive']}",ln=True)
    pdf.cell(200,10,f"Negative News: {sentiment['negative']}",ln=True)
    pdf.cell(200,10,f"Neutral News: {sentiment['neutral']}",ln=True)

    pdf.ln(10)

    if rsi < 30:
        advice = "The stock appears oversold. It might be a good buying opportunity."
    elif rsi > 70:
        advice = "The stock appears overbought. Investors should be cautious."
    else:
        advice = "The stock is trading in a normal range."

    pdf.multi_cell(0,10,f"AI Recommendation: {advice}")

    pdf.output("report.pdf")


if st.button("Generate PDF Report"):

    if st.session_state.data is None:
        st.error("Please analyze a stock first.")
        st.stop()

    generate_report(
        symbol,
        st.session_state.data,
        st.session_state.fundamentals,
        st.session_state.sentiment
    )

    with open("report.pdf", "rb") as file:

        st.download_button(
            label="Download Report",
            data=file,
            file_name="financial_report.pdf",
            mime="application/pdf"
        )