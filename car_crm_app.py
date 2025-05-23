# Streamlit Car Flipping CRM App with MMR Calculator
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Car Flipping CRM", layout="wide")

# Set background styling
st.markdown("""
    <style>
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1592194996308-7b43878e84a6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .css-18e3th9 {
        background-color: rgba(255, 255, 255, 0.85) !important;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize contact list if not already present
if "contact_data" not in st.session_state:
    st.session_state.contact_data = pd.DataFrame(columns=["Name", "Phone", "Type", "Associated VIN"])


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
        # Prompt for contact info associated with this watchlist entry
        contact_name = st.text_input("Seller Name")
        contact_phone = st.text_input("Seller Phone Number")
        if contact_name and contact_phone:
            new_contact = pd.DataFrame([[contact_name, contact_phone, "Seller", vin]], columns=st.session_state.contact_data.columns)
            st.session_state.contact_data = pd.concat([st.session_state.contact_data, new_contact], ignore_index=True)
        st.session_state.crm_data = pd.concat([st.session_state.crm_data, new_row], ignore_index=True)
        st.success("Car added to watchlist!")

        # Simulated API call for similar market listings
        st.subheader("📊 Market Data for Similar Listings")
        if make and model:
            # NOTE: Replace with actual API call if available (e.g., Edmunds, CarGurus)
            st.markdown(f"Showing recent listings for **{year} {make} {model}**:")
            sample_market_data = pd.DataFrame({
                'Year': [year]*6,
                'Make': [make]*6,
                'Model': [model]*6,
                'Mileage': [85000, 102000, 96000, 88000, 92000, 110000],
                'Price ($)': [6200, 5800, 6000, 6350, 6100, 5700],
                'Location': [
                    'California - Los Angeles',
                    'California - San Diego',
                    'California - Riverside',
                    'USA - National Average',
                    'Midwest - Phoenix',
                    'Midwest - Las Vegas'
                ]
            })
            st.dataframe(sample_market_data)
        else:
            st.info("Enter Make and Model to fetch market data.")

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

# Dealer Offer Builder
st.subheader("📦 Create Dealer Offer Sheet")
with st.form("create_offer"):
    st.write("Enter Car Details to Generate an Offer")
    offer_vin = st.text_input("VIN")
    stock_number = st.text_input("Stock Number")
    offer_mileage = st.number_input("Mileage", min_value=0)
    offer_make = st.text_input("Make")
    offer_model = st.text_input("Model")
    offer_trim = st.text_input("Trim")
    offer_price = st.number_input("Offer Price ($)", min_value=0.0, step=100.0)
    notes = st.text_area("Notes")
    offer_submit = st.form_submit_button("Generate Offer")
    if offer_submit and offer_vin and offer_make and offer_model:
        offer_output = f"""
        ### 🔖 Dealer Offer Sheet
        - **VIN**: {offer_vin}  
        - **Stock #:** {stock_number}  
        - **Make / Model / Trim:** {offer_make} {offer_model} {offer_trim}  
        - **Mileage:** {offer_mileage:,} miles  
        - **Offer Price:** 💵 ${offer_price:,.2f}  
        - **Notes:** {notes}
        """
        st.markdown(offer_output)
        st.download_button(
            label="📄 Download Offer Sheet",
            data=offer_output,
            file_name=f"OfferSheet_{offer_vin}.txt",
            mime="text/plain"
        )

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

# Contact management section
st.subheader("📞 Contacts")
with st.form("add_contact"):
    st.write("Add a Contact (Buyer or Seller)")
    contact_name = st.text_input("Contact Name")
    contact_phone = st.text_input("Phone Number")
    contact_type = st.selectbox("Type", ["Seller", "Buyer"])
    associated_vin = st.text_input("Associated VIN (optional)")
    contact_submitted = st.form_submit_button("Add Contact")
    if contact_submitted and contact_name and contact_phone:
        new_contact = pd.DataFrame([[contact_name, contact_phone, contact_type, associated_vin]], columns=st.session_state.contact_data.columns)
        st.session_state.contact_data = pd.concat([st.session_state.contact_data, new_contact], ignore_index=True)
        st.success("Contact added!")

st.dataframe(st.session_state.contact_data)

# Export to Excel
st.subheader("📤 Export CRM to Excel")
if st.download_button("Download Excel Report", data=st.session_state.crm_data.to_csv(index=False).encode("utf-8"), file_name="CarFlipCRM_Report.csv", mime="text/csv"):
    st.success("Excel report downloaded!")

# AI Assistant for Pitch Generation
st.subheader("🤖 AI Assistant: Generate a Pitch to Find a Car")
car_description = st.text_area("Describe the car you're trying to source (year, make, model, trim, budget, etc.):")
if st.button("Generate Pitch"):
    if car_description:
        pitch = f"Hi, I'm looking for a vehicle with the following specs: {car_description}. If you have something that fits or close, let me know. Cash buyer, ready to move fast."
        st.markdown(f"**Generated Pitch:**

{pitch}")
        st.download_button("📄 Download Pitch", data=pitch, file_name="Pitch.txt", mime="text/plain")
    else:
        st.warning("Please describe the car you're looking for.")

# MMR Calculator
st.subheader("📊 MMR-Based Price Calculator")
mmr_input = st.number_input("Enter MMR Value ($)", min_value=0.0, step=100.0)
if mmr_input:
    low_offer = mmr_input * 0.85
    high_offer = mmr_input * 0.92
    st.markdown(f"**Target Buy Price Range (8–15% below MMR):** 💰 **${low_offer:,.2f} – ${high_offer:,.2f}**")
