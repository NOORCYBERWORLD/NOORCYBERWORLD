import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

# Page Config
st.set_page_config(page_title="NOOR CYBER WORLD", page_icon="🖥️", layout="wide")

# Google Apps Script Web App URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxfb9UlZt5QXCTC_a4U95VopEgYmKunhwKGRpBwnjxNQ-ahdS_ivYTORRxjeams_CQ/exec"

# IST Offset
IST_OFFSET = timezone(timedelta(hours=5, minutes=30))

def get_today_ist():
    return datetime.now(IST_OFFSET).date()

# Custom UI Styling
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0a0a0c 0%, #16181f 50%, #0d1117 100%); color: #ffffff; }
    .header-title { margin: 0; color: #ff2a2a; font-size: 32px; font-weight: 800; letter-spacing: 1.5px; }
    .header-subtitle { margin: 0; color: #3b82f6; font-size: 14px; font-weight: 600; }
    div[data-testid="stMetric"] { background: rgba(255, 255, 255, 0.04); border-radius: 12px; padding: 15px; border: 1px solid rgba(59, 130, 246, 0.2); }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='padding-top: 10px; margin-bottom: 20px;'>
        <h1 class="header-title">NOOR CYBER WORLD</h1>
        <p class="header-subtitle">Center Management & Secure Cloud Entry System</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

@st.cache_data(ttl=2)
def get_records():
    try:
        res = requests.get(WEB_APP_URL, timeout=12)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
                if not df.empty and "created_at" in df.columns:
                    df["created_at"] = df["created_at"].astype(str)
                    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
                    return df
        return pd.DataFrame(columns=["created_at", "name", "mobile", "service", "amount", "payment", "expiry"])
    except Exception:
        return pd.DataFrame(columns=["created_at", "name", "mobile", "service", "amount", "payment", "expiry"])

def add_record(created_at, name, mobile, service, amount, payment, expiry):
    payload = {
        "created_at": str(created_at),
        "name": str(name),
        "mobile": str(mobile),
        "service": str(service),
        "amount": str(amount),
        "payment": str(payment),
        "expiry": str(expiry)
    }
    try:
        res = requests.post(WEB_APP_URL, data=payload, timeout=15, allow_redirects=True)
        return res.status_code in [200, 302]
    except Exception:
        return False

if "selected_view_date" not in st.session_state:
    st.session_state.selected_view_date = get_today_ist()

services_list = [
    "Aadhaar Card Download / Update", "PAN Card New / Correction", "Voter ID Card Apply / Correction",
    "Ration Card Services", "Ayushman Bharat Card", "E-Shram Card", "Income Certificate",
    "Caste Certificate", "Domicile Certificate", "Non-Creamy Layer Certificate",
    "Gazette Notification / Name Change", "Passport Application", "Driving License (LL/DL) & RC Services",
    "PM Kisan Samman Nidhi / KYC", "PF / EPF Withdrawal & Claim", "Government Job Online Forms",
    "Admission & Scholarship Forms", "Railway / Bus / Air Ticket Booking", "Electricity / Gas / Water Bill Payment",
    "Money Transfer (DMT) / AEPS Cash Withdrawal", "Mobile / DTH Recharge", "Xerox / Color Printout / Lamination / Scanning",
    "Resume / Bio-Data Making", "Udyam Aadhaar / MSME Registration", "Shop Act License / FSSAI Food License",
    "GST Registration & Return Filing", "Income Tax Return (ITR) Filing", "Police Verification Application",
    "Digital Signature (DSC)", "PVC Card Printing", "Other"
]

df_all = get_records()
curr_date_str = st.session_state.selected_view_date.strftime("%Y-%m-%d")

if not df_all.empty and "created_at" in df_all.columns:
    day_df = df_all[df_all["created_at"] == curr_date_str]
    day_total = int(day_df["amount"].sum()) if not day_df.empty else 0
else:
    day_df = pd.DataFrame()
    day_total = 0

col_prev, col_date, col_next = st.columns([1, 4, 1])

with col_prev:
    st.write("")
    if st.button("❮ Previous", use_container_width=True):
        st.session_state.selected_view_date -= timedelta(days=1)
        st.rerun()

with col_date:
    selected_from_cal = st.date_input(
        f"📅 Date: {st.session_state.selected_view_date.strftime('%B %d, %Y (%A)')}  |  Balance: ₹ {day_total:,}",
        value=st.session_state.selected_view_date,
        key="date_picker_main"
    )
    if selected_from_cal != st.session_state.selected_view_date:
        st.session_state.selected_view_date = selected_from_cal
        st.rerun()

with col_next:
    st.write("")
    if st.button("Next ❯", use_container_width=True):
        st.session_state.selected_view_date += timedelta(days=1)
        st.rerun()

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Daily View & Add Entry", "🔔 Renewal Alerts", "📂 Full Google Sheet Data"])

with tab1:
    st.subheader(f"📋 Entries for {st.session_state.selected_view_date.strftime('%d-%m-%Y (%A)')}")
    
    if not day_df.empty:
        total_cash = int(day_df[day_df["payment"] == "Cash"]["amount"].sum())
        total_online = int(day_df[day_df["payment"] == "Online"]["amount"].sum())
    else:
        total_cash = 0
        total_online = 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Day Total", f"₹ {total_cash + total_online}")
    c2.metric("Day Cash", f"₹ {total_cash}")
    c3.metric("Day Online / UPI", f"₹ {total_online}")
    
    st.markdown("---")
    if not day_df.empty:
        st.dataframe(day_df, use_container_width=True)
    else:
        st.info("ℹ️ No entries recorded for this date yet.")

    st.markdown("---")
    st.subheader(f"➕ Add Entry for {st.session_state.selected_view_date.strftime('%d-%m-%Y')}")
    
    # Direct Form Inputs without Nesting Errors
    col_a, col_b = st.columns(2)
    with col_a:
        name = st.text_input("Customer Name*", key="cust_name_input")
        mobile = st.text_input("Mobile Number*", key="cust_mob_input")
        selected_service = st.selectbox("Search / Select Service*", services_list, key="srv_select_input")
        custom_srv = st.text_input("Type Custom Service Name (If 'Other' Selected)", key="custom_srv_input")

    with col_b:
        amount = st.number_input("Amount (₹)", min_value=0, step=10, key="amt_input")
        pay_mode = st.radio("Payment Mode", ["Cash", "Online"], horizontal=True, key="pay_mode_input")
        has_expiry = st.checkbox("Requires Renewal / Validity?", key="has_exp_input")
        dur_unit = st.selectbox("Validity Unit", ["Days", "Months", "Years"], index=1, key="dur_unit_input")
        dur_val = st.number_input("Validity Duration Value", min_value=1, value=1, key="dur_val_input")

    st.write("")
    if st.button("💾 Save Entry to Cloud Sheet", type="primary", use_container_width=True):
        if not name.strip() or not mobile.strip():
            st.error("⚠️ Please enter Customer Name and Mobile Number!")
        else:
            final_service = selected_service
            if selected_service == "Other":
                if custom_srv.strip():
                    final_service = custom_srv.strip()
                else:
                    st.error("⚠️ Please type the custom service name!")
                    st.stop()
            
            exp_str = "N/A"
            if has_expiry:
                entry_d = st.session_state.selected_view_date
                if dur_unit == "Days":
                    calc_exp = entry_d + timedelta(days=int(dur_val))
                elif dur_unit == "Months":
                    calc_exp = entry_d + relativedelta(months=int(dur_val))
                elif dur_unit == "Years":
                    calc_exp = entry_d + relativedelta(years=int(dur_val))
                exp_str = calc_exp.strftime("%Y-%m-%d")

            date_str = st.session_state.selected_view_date.strftime("%Y-%m-%d")
            
            with st.spinner("Saving entry to Google Sheet..."):
                success = add_record(date_str, name, mobile, final_service, amount, pay_mode, exp_str)
            
            if success:
                st.cache_data.clear()
                st.success(f"✅ Entry for '{name}' saved successfully!")
                st.balloons()
            else:
                st.error("❌ Google Sheet server error. Please check Apps Script connection.")

with tab2:
    st.subheader("⚠️ Renewal Alerts (Next 15 Days)")
    today = get_today_ist()
    alerts_found = False
    
    if not df_all.empty and "expiry" in df_all.columns:
        for idx, row in df_all.iterrows():
            exp_val = row["expiry"]
            if exp_val != "N/A" and exp_val != "" and exp_val is not None:
                try:
                    exp_d = datetime.strptime(str(exp_val), "%Y-%m-%d").date()
                    days_left = (exp_d - today).days
                    if 0 <= days_left <= 15:
                        alerts_found = True
                        formatted_exp = exp_d.strftime('%d-%m-%Y')
                        msg = f"Hello {row['name']}, your {row['service']} is expiring on {formatted_exp}. Please visit NOOR CYBER WORLD for renewal."
                        wa_link = f"https://wa.me/91{row['mobile']}?text={msg.replace(' ', '%20')}"
                        st.warning(f"🔴 **{row['name']}** - {row['service']} (Expires: {formatted_exp} | {days_left} Days Left)")
                        st.markdown(f"[💬 Send WhatsApp Message]({wa_link})")
                except Exception:
                    pass
                    
    if not alerts_found:
        st.info("🎉 No renewals due in the next 15 days.")

with tab3:
    st.subheader("📂 All Cloud Records")
    if df_all.empty:
        st.info("No records available in Google Sheet.")
    else:
        st.dataframe(df_all, use_container_width=True)
