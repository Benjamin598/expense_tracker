import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# === File to store expenses ===
DATA_FILE = 'expenses.csv'

# === Load Data ===
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
        return df
    else:
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])

# === Save Data ===
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# === Streamlit App ===
st.set_page_config(page_title="Expense Tracker", layout="centered")
st.title("💰 Personal Expense Tracker Dashboard")

# === Add New Expense ===
with st.expander("➕ Add New Expense", expanded=False):
    with st.form("expense_form"):
        date = st.date_input("Date", value=datetime.today())
        category = st.text_input("Category", placeholder="e.g. Food, Rent")
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        description = st.text_input("Description", placeholder="e.g. Lunch, Taxi, Internet")

        submitted = st.form_submit_button("Add Expense")
        if submitted:
            new_entry = pd.DataFrame([{
                "Date": pd.to_datetime(date),
                "Category": category,
                "Amount": amount,
                "Description": description
            }])
            df_existing = load_data()
            df_updated = pd.concat([df_existing, new_entry], ignore_index=True)
            save_data(df_updated)
            st.success("✅ Expense added successfully!")
            st.rerun()  # ✅ FIXED: Updated method for refreshing the app

# === Load and Filter Data ===
df = load_data()

st.sidebar.header("🔎 Filter Expenses")
category_filter = st.sidebar.selectbox("Filter by Category", options=["All"] + sorted(df["Category"].dropna().unique().tolist()))

if category_filter != "All":
    df = df[df["Category"] == category_filter]

# === Display Expense Table ===
st.subheader("📋 Expense Table")
if df.empty:
    st.info("No expenses found. Add some using the form above.")
else:
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

    # === Total Spend ===
    total = df["Amount"].sum()
    st.metric("💸 Total Spent", f"${total:,.2f}")

    # === Monthly Spending Chart ===
    df["Month"] = df["Date"].dt.to_period("M")
    monthly = df.groupby("Month")["Amount"].sum().reset_index()
    monthly["Month"] = monthly["Month"].astype(str)
    st.subheader("📆 Monthly Spending")
    st.bar_chart(monthly.set_index("Month"))

    # === Spending by Category Pie Chart ===
    category_summary = df.groupby("Category")["Amount"].sum().reset_index()
    fig = px.pie(category_summary, values="Amount", names="Category", title="📊 Spending by Category")
    st.plotly_chart(fig)
