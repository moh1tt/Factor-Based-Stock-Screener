# app.py

import streamlit as st
import pandas as pd
from screener import screen_stocks
from matplotlib import pyplot as plt

st.set_page_config(page_title="Stock Screener", layout="wide")

st.title("📈 Stock Screener")
st.markdown(
    "Filter and rank S&P 500 stocks based on valuation and quality factors.")
st.markdown("""
Welcome to the **Stock Screener** — an intelligent tool to help you discover stocks based on *fundamental financial factors*.

### 🧠 Why Use This Screener?
This app helps you:
- Filter stocks using real financial data (P/E, ROE, EPS Growth, etc.)
- Rank them with a custom scoring model based on your preferences
- Quickly find value, growth, or quality stocks without digging through raw numbers

### 💼 Ideal For:
- Finance & data science students building a portfolio
- Retail investors looking for smart entry points
- Professionals exploring systematic investment strategies
""")

st.info("📌 This is a dynamic, no-code stock research tool powered by Python + Streamlit. Adjust sliders and discover your top stocks instantly!")


# Load and process
df_raw = pd.read_csv("data/fundamentals_snapshot.csv")
df = screen_stocks(df_raw)

# Sidebar: Filter Criteria
with st.sidebar.expander("🔍 Filter Criteria"):
    pe_max = st.slider("Maximum P/E", 0.0, 100.0, 25.0)
    roe_min = st.slider("Minimum ROE", 0.0, 1.0, 0.10)
    de_max = st.slider("Maximum D/E", 0.0, 100.0, 10.0)

# Sidebar: Custom Weights
with st.sidebar.expander("⚖️ Factor Weights"):
    w_pe = st.slider("Weight: P/E (lower better)", 0.0, 1.0, 0.25)
    w_pb = st.slider("Weight: P/B (lower better)", 0.0, 1.0, 0.25)
    w_roe = st.slider("Weight: ROE", 0.0, 1.0, 0.25)
    w_eps = st.slider("Weight: EPS Growth", 0.0, 1.0, 0.25)


# Normalize and score
for col in ['P/E', 'P/B', 'ROE', 'EPS Growth']:
    if col in df.columns:
        df[col + '_score'] = (df[col] - df[col].min()) / \
            (df[col].max() - df[col].min())

df['Factor Score'] = (
    (1 - df['P/E_score']) * w_pe +
    (1 - df['P/B_score']) * w_pb +
    df['ROE_score'] * w_roe +
    df['EPS Growth_score'] * w_eps
)

# Apply filters
filtered = df[
    (df['P/E'] <= pe_max) &
    (df['ROE'] >= roe_min) &
    (df['D/E'] <= de_max)
]

with st.expander("📘 Financial Metrics Explained"):
    st.markdown("""
### 📊 Key Financial Ratios Used in This Screener

#### **1. Price-to-Earnings (P/E) Ratio**
- **Formula**: Market Price per Share / Earnings per Share (EPS)
- **What it means**: Tells you how much investors are paying for each dollar of earnings.
- **Interpretation**:
  - Low P/E → undervalued (or low growth expectations)
  - High P/E → expensive or high growth potential

#### **2. Price-to-Book (P/B) Ratio**
- **Formula**: Market Price / Book Value of Assets
- **What it means**: Compares the market value of a company to its accounting value.
- **Interpretation**:
  - P/B < 1 → possibly undervalued
  - P/B > 3 → market expects strong growth or intangible assets dominate

#### **3. Return on Equity (ROE)**
- **Formula**: Net Income / Shareholder’s Equity
- **What it means**: Measures how effectively a company turns equity into profits.
- **Interpretation**:
  - ROE > 15% → strong profitability
  - ROE < 5% → inefficient use of capital

#### **4. Debt-to-Equity (D/E) Ratio**
- **Formula**: Total Liabilities / Shareholder’s Equity
- **What it means**: Indicates a company’s leverage and financial risk.
- **Interpretation**:
  - D/E < 1 → conservative leverage
  - D/E > 2 → heavily reliant on debt

#### **5. EPS Growth**
- **Formula**: (Current EPS - Last Year EPS) / Last Year EPS
- **What it means**: Shows how fast earnings are growing year over year.
- **Interpretation**:
  - Positive & rising EPS growth = strong earnings momentum

#### **6. Market Capitalization (Market Cap)**
- **Formula**: Share Price × Total Shares Outstanding
- **What it means**: Represents the total market value of the company.
- **Categories**:
  - Small Cap (< $2B)
  - Mid Cap ($2B–$10B)
  - Large Cap (> $10B)

---
These metrics are commonly used by institutional investors, analysts, and quant funds to evaluate stocks across **value, quality, and growth factors**.
    """)


# 📊 KPIs with Top Stock Highlight
st.subheader("📊 Key Metrics Summary")

if not filtered.empty:
    top_stock = filtered.sort_values('Factor Score', ascending=False).iloc[0]
    st.markdown(
        f"**🏅 Top Stock Based on Your Criteria:** `{top_stock['Company Name']} ({top_stock['Ticker']})`")

    col1, col2, col3 = st.columns(3)
    col1.metric("📈 Avg P/E", f"{filtered['P/E'].mean():.2f}")
    col2.metric("💰 Avg ROE", f"{filtered['ROE'].mean():.2%}")
    col3.metric("🏢 Avg Market Cap",
                f"${filtered['Market Cap'].mean() / 1e9:.2f}B")

    col4, col5, col6 = st.columns(3)
    col4.metric("📉 Avg D/E", f"{filtered['D/E'].mean():.2f}")
    col5.metric("🚀 Avg EPS Growth", f"{filtered['EPS Growth'].mean():.2%}")
    col6.metric("📊 Avg Factor Score", f"{filtered['Factor Score'].mean():.2f}")
else:
    st.warning(
        "No stocks match your filters. Adjust the sliders to explore more options.")


# --- Top 10 Highlight ---
st.subheader("🏆 Top 10 Stocks by Factor Score")
if not filtered.empty:
    top10 = filtered.sort_values('Factor Score', ascending=False).head(10)

    st.dataframe(
        top10[['Ticker', 'Company Name', 'P/E', 'P/B', 'ROE',
               'D/E', 'EPS Growth', 'Market Cap', 'Factor Score']]
        .style
        .format({
            "P/E": "{:.2f}",
            "P/B": "{:.2f}",
            "ROE": "{:.2%}",
            "D/E": "{:.2f}",
            "EPS Growth": "{:.2%}",
            "Market Cap": "${:,.0f}",
            "Factor Score": "{:.2f}"
        })
        .background_gradient(subset=['Factor Score'], cmap='Blues')
    )


# 📋 Full Table
st.subheader("📋 All Filtered Stocks")
if not filtered.empty:
    st.dataframe(
        filtered[['Ticker', 'Company Name', 'P/E', 'P/B', 'ROE',
                  'D/E', 'EPS Growth', 'Market Cap', 'Factor Score']]
        .sort_values('Factor Score', ascending=False)
        .style
        .format({
            "P/E": "{:.2f}",
            "P/B": "{:.2f}",
            "ROE": "{:.2%}",
            "D/E": "{:.2f}",
            "EPS Growth": "{:.2%}",
            "Market Cap": "${:,.0f}",
            "Factor Score": "{:.2f}"
        })
    )

# 📥 Download
st.download_button("📥 Download CSV", filtered.to_csv(
    index=False), file_name="filtered_stocks.csv")


# 💸 Investment Recommendation Planner
st.subheader("💸 Investment Recommendation Planner")

with st.expander("📊 Personalized Allocation Plan"):
    savings = st.number_input(
        "Enter your total investable savings (USD)", min_value=0.0, step=100.0, format="%.2f")

    if savings > 0:
        # Fixed strategy allocation
        value_pct = 40
        quality_pct = 35
        growth_pct = 25

        value_amt = savings * value_pct / 100
        quality_amt = savings * quality_pct / 100
        growth_amt = savings * growth_pct / 100

        st.markdown(f"""
        ### 🧾 Recommended Plan Based on Factor Strategy
        - 💰 **Total to Invest**: `${savings:,.2f}`

        **Allocation Strategy:**
        - 🟦 **Value Stocks (40%)**: `${value_amt:,.2f}`
        - 🟩 **Quality Stocks (35%)**: `${quality_amt:,.2f}`
        - 🟥 **Growth Stocks (25%)**: `${growth_amt:,.2f}`
        """)
