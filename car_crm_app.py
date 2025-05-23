# Streamlit Car Flipping CRM App
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Car Flipping CRM", layout="centered")

# Initialize session state if not already present
if "crm_data" not in st.session_state:
    st.session_state.crm_data = pd.DataFrame(columns=[
        "VIN", "Make", "Model", "Year", "Purchase Date", "Purchase Price ($)",
        "Sold Date", "Sold Price ($)", "Profit ($)", "Status"
    ])

st.title("🚗 Car Flipping CRM")

# Form to add new car
with st.form("add_car_form"):
    st.subheader("Add a Car to Watchlist")
    vin = st.text_input("VIN")
    make = st.text_input("Make")
    model = st.text_input("Model")
    year = st.number_input("Year", min_value=1980, max_value=2030, step=1)
    submitted = st.form_submit_button("Add to Watchlist")
    if submitted and vin:
        new_row = pd.DataFrame([[vin, make, model, year, None, None, None, None, None, "Watch"]], columns=st.session_state.crm_data.columns)
        st.session_state.crm_data = pd.concat([st.session_state.crm_data, new_row], ignore_index=True)
        st.success("Car added to watchlist!")

# Section to mark as purchased
st.subheader("💵 Mark a Car as Purchased")
purchase_vin = st.selectbox("Select VIN to mark as purchased", st.session_state.crm_data[st.session_state.crm_data["Status"] == "Watch"]["VIN"])
purchase_date = st.date_input("Purchase Date")
purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, step=100.0)
if st.button("Update Purchase Info"):
    idx = st.session_state.crm_data[st.session_state.crm_data["VIN"] == purchase_vin].index
    if not idx.empty:
        st.session_state.crm_data.loc[idx, "Purchase Date"] = pd.to_datetime(purchase_date)
        st.session_state.crm_data.loc[idx, "Purchase Price ($)"] = purchase_price
        st.session_state.crm_data.loc[idx, "Status"] = "Purchased"
        st.success("Car marked as purchased!")

# Section to mark as sold
st.subheader("💰 Mark a Car as Sold")
sold_vin = st.selectbox("Select VIN to mark as sold", st.session_state.crm_data[st.session_state.crm_data["Status"] == "Purchased"]["VIN"])
sold_date = st.date_input("Sold Date")
sold_price = st.number_input("Sold Price ($)", min_value=0.0, step=100.0)
if st.button("Update Sold Info"):
    idx = st.session_state.crm_data[st.session_state.crm_data["VIN"] == sold_vin].index
    if not idx.empty:
        st.session_state.crm_data.loc[idx, "Sold Date"] = pd.to_datetime(sold_date)
        st.session_state.crm_data.loc[idx, "Sold Price ($)"] = sold_price
        purchase_price = st.session_state.crm_data.loc[idx, "Purchase Price ($)"].values[0]
        if pd.notna(purchase_price):
            profit = sold_price - float(purchase_price)
            st.session_state.crm_data.loc[idx, "Profit ($)"] = profit
            st.session_state.crm_data.loc[idx, "Status"] = "Sold"
            st.success("Car marked as sold!")

# Display CRM table
st.subheader("📋 Current CRM Table")
st.dataframe(st.session_state.crm_data)

# Monthly profit summary
st.subheader("📈 Monthly Profit Summary")
if not st.session_state.crm_data["Sold Date"].dropna().empty:
    df = st.session_state.crm_data.copy()
    df["Sold Date"] = pd.to_datetime(df["Sold Date"], errors='coerce')
    df["Month"] = df["Sold Date"].dt.to_period("M")
    summary = df.dropna(subset=["Profit ($)"]).groupby("Month")["Profit ($)"].sum()
    st.bar_chart(summary)

# Export to Excel
st.subheader("📤 Export CRM to Excel")
if st.download_button("Download Excel Report", data=st.session_state.crm_data.to_csv(index=False).encode("utf-8"), file_name="CarFlipCRM_Report.csv", mime="text/csv"):
    st.success("Excel report downloaded!")
