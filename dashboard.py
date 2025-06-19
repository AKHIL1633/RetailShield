import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

def show_dashboard():
    st.title("🛡️ RetailShield Blockchain Log Dashboard")
    API_URL = "http://localhost:5000/view_blockchain"

    @st.cache_data(ttl=10)
    def get_blockchain():
        resp = requests.get(API_URL)
        return resp.json()

    PAYMENT_METHODS = {1: "Credit Card", 2: "UPI", 3: "Wallet"}
    TIME_OF_DAY = {1: "Day", 0: "Night"}

    data = get_blockchain()
    rows = []
    raw_blocks = []

    for block in data:
        if block["index"] == 0:
            continue
        tx = block["data"]["transaction"]
        tx["Risk Level"] = block["data"]["result"]
        tx["Block Index"] = block["index"]
        t = float(block["timestamp"])
        tx["Time"] = datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")
        # NEW: Pull the actual fraud reason (if present, else "-")
        tx["Fraud Reason"] = block["data"].get("reason", "-")
        tx_disp = {
            "Amount (₹)": tx["amount"],
            "Trusted Device": "Yes" if tx["device_known"] else "No",
            "Frequency": tx["frequency"],
            "Location Match": "Yes" if tx["location_match"] else "No",
            "Payment Method": PAYMENT_METHODS.get(tx["payment_method"], "Other"),
            "Time (Day/Night)": TIME_OF_DAY.get(tx["time_of_day"], "Unknown"),
            "Is Return?": "Yes" if tx["is_return"] else "No",
            "Risk Level": tx["Risk Level"],
            "Fraud Reason": tx["Fraud Reason"],   # <-- Will now show full detail
            "Block Index": tx["Block Index"],
            "Time": tx["Time"],
        }
        rows.append(tx_disp)
        raw_blocks.append(block)

    with st.expander("ℹ️ Column Legend", expanded=False):
        st.markdown("""
        - **Trusted Device:** Was this transaction from a recognized device?
        - **Location Match:** Does the transaction location match the user’s usual pattern?
        - **Frequency:** Number of transactions in short span (higher = riskier)
        - **Payment Method:** UPI/Credit Card/Wallet
        - **Time (Day/Night):** Was it done during the day or night?
        - **Is Return?:** Was this a return/refund transaction?
        - **Risk Level:** Fraud or Safe
        - **Fraud Reason:** Why it was flagged (detailed by AI/rule)
        """)

    st.subheader("🔎 Filter & Search Transactions")
    col1, col2 = st.columns([1,2])
    with col1:
        risk_filter = st.multiselect("Filter by Risk Level", ["Fraud", "Safe"], default=["Fraud", "Safe"])
    with col2:
        amount_search = st.text_input("Search by Amount (Exact or Blank for All)")

    if rows:
        df = pd.DataFrame(rows)
        df = df[df["Risk Level"].isin(risk_filter)]
        if amount_search.strip():
            try:
                amt = int(amount_search)
                df = df[df["Amount (₹)"] == amt]
            except:
                pass

        st.write("## 🧾 Transaction Log")
        st.dataframe(
            df.style.applymap(lambda v: 'background-color: #ff4b4b' if v == 'Fraud' else 'background-color: #57d985', subset=["Risk Level"]),
            use_container_width=True,
            height=360
        )

        chart_data = df["Risk Level"].value_counts().reset_index()
        chart_data.columns = ["Risk Level", "Count"]
        st.write("### Fraud vs Safe Transactions")
        fig_pie = px.pie(chart_data, names="Risk Level", values="Count", color="Risk Level",
                         color_discrete_map={"Fraud": "#ff4b4b", "Safe": "#57d985"},
                         hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

        st.write("### Transactions Over Time")
        fig_line = px.line(df.sort_values("Time"), x="Time", y="Amount (₹)", color="Risk Level",
                           markers=True, labels={"Amount (₹)": "Transaction Amount (₹)"})
        st.plotly_chart(fig_line, use_container_width=True)

        st.download_button("⬇️ Download CSV Log", df.to_csv(index=False), "retailshield_log.csv")

    else:
        st.info("No transactions yet. Make some POSTs to /check_transaction!")

    with st.expander("🧾 View Raw Blockchain Data (JSON)"):
        st.json(raw_blocks)

    st.button("🔄 Refresh")
