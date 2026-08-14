import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Page Config
st.set_page_config(page_title="NOOR CYBER WORLD", page_icon="🖥️", layout="wide")

# 👇 यहाँ अपनी Base64 कोड स्ट्रिंग रहने दें
LOGO_BASE64 = "PASTE_YOUR_BASE64_STRING_HERE"

# CUSTOM CSS FOR STYLING
st.markdown("""
    <style>
    /* Main Background Gradient matching logo theme */
    .stApp {
        background: linear-gradient(135deg, #0a0a0c 0%, #16181f 50%, #0d1117 100%);
        color: #ffffff;
    }
    
    /* Header Title Style */
    .header-title {
        margin: 0;
        color: #ff2a2a;
        font-size: 32px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-shadow: 0 0 12px rgba(255, 42, 42, 0.4);
    }
    
    .header-subtitle {
        margin: 0;
        color: #3b82f6;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 1px;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        color: #ffffff;
        padding: 8px 16px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ff2a2a !important;
        color: #ffffff !important;
        font-weight: bold;
    }

    /* Form & Input Styling */
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        border-radius: 8px !important;
    }

    /* Primary Button */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# App Header Layout
col_logo, col_title = st.columns([1, 4])

with col_logo:
    if LOGO_BASE64 and "PASTE_YOUR_BASE64" not in LOGO_BASE64:
        st.image(LOGO_BASE64, width=130)
    else:
        st.write("🖥️")

with col_title:
    st.markdown("""
        <div style='padding-top: 10px;'>
            <h1 class="header-title">NOOR CYBER WORLD</h1>
            <p class="header-subtitle">Center Management & Renewal Reminder System</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("noor_cyber_data.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            service TEXT NOT NULL,
            amount REAL NOT NULL,
            payment TEXT NOT NULL,
            expiry TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Database Functions
def add_record(created_at, name, mobile, service, amount, payment, expiry):
    conn = sqlite3.connect("noor_cyber_data.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO records (created_at, name, mobile, service, amount, payment, expiry)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (created_at, name, mobile, service, amount, payment, expiry))
    conn.commit()
    conn.close()

def get_records():
    conn = sqlite3.connect("noor_cyber_data.db")
    df = pd.read_sql_query("SELECT id, created_at as Date, name as Name, mobile as Mobile, service as Service, amount as Amount, payment as Payment, expiry as Expiry FROM records", conn)
    conn.close()
    return df

def delete_record(record_id):
    conn = sqlite3.connect("noor_cyber_data.db")
    c = conn.cursor()
    c.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

def update_record(record_id, created_at, name, mobile, service, amount, payment, expiry):
    conn = sqlite3.connect("noor_cyber_data.db")
    c = conn.cursor()
    c.execute('''
        UPDATE records 
        SET created_at = ?, name = ?, mobile = ?, service = ?, amount = ?, payment = ?, expiry = ?
        WHERE id = ?
    ''', (created_at, name, mobile, service, amount, payment, expiry, record_id))
    conn.commit()
    conn.close()

# Run DB Setup
init_db()

# Session State for Dynamic Services List
if "services_list" not in st.session_state:
    st.session_state.services_list = [
        "Aadhaar Card Download / Update",
        "PAN Card New / Correction",
        "Voter ID Card Apply / Correction",
        "Ration Card Services",
        "Ayushman Bharat Card",
        "E-Shram Card",
        "Income Certificate",
        "Caste Certificate",
        "Domicile Certificate",
        "Non-Creamy Layer Certificate",
        "Gazette Notification / Name Change",
        "Passport Application",
        "Driving License (LL/DL) & RC Services",
        "PM Kisan Samman Nidhi / KYC",
        "PF / EPF Withdrawal & Claim",
        "Government Job Online Forms",
        "Admission & Scholarship Forms",
        "Railway / Bus / Air Ticket Booking",
        "Electricity / Gas / Water Bill Payment",
        "Money Transfer (DMT) / AEPS Cash Withdrawal",
        "Mobile / DTH Recharge",
        "Xerox / Color Printout / Lamination / Scanning",
        "Resume / Bio-Data Making",
        "Udyam Aadhaar / MSME Registration",
        "Shop Act License / FSSAI Food License",
        "GST Registration & Return Filing",
        "Income Tax Return (ITR) Filing",
        "Police Verification Application",
        "Digital Signature (DSC)",
        "PVC Card Printing",
        "Other"
    ]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ New Entry", "🔔 Renewal Alerts", "📂 History & Edit/Delete"])

# TAB 1: DASHBOARD (Today's Data)
with tab1:
    st.subheader("Today's Overview")
    df = get_records()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if not df.empty and "Date" in df.columns:
        today_df = df[df["Date"] == today_str]
    else:
        today_df = pd.DataFrame()
        
    if not today_df.empty:
        total_cash = int(today_df[today_df["Payment"] == "Cash"]["Amount"].sum())
        total_online = int(today_df[today_df["Payment"] == "Online"]["Amount"].sum())
    else:
        total_cash = 0
        total_online = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Today Total", f"₹ {total_cash + total_online}")
    col2.metric("Today Cash", f"₹ {total_cash}")
    col3.metric("Today Online / UPI", f"₹ {total_online}")
    
    st.markdown("---")
    st.write("📋 **Today's Entries:**")
    st.dataframe(today_df.drop(columns=["id"], errors="ignore"), use_container_width=True)

# TAB 2: NEW ENTRY
with tab2:
    st.subheader("New Service Entry")
    
    col_a, col_b = st.columns(2)
    with col_a:
        entry_date = st.date_input("Entry Date*", datetime.now().date(), key="new_entry_date")
        name = st.text_input("Customer Name*", key="new_name")
        mobile = st.text_input("Mobile Number*", key="new_mobile")
        selected_service = st.selectbox("Search / Select Service*", st.session_state.services_list, key="new_service")
        
        custom_service_name = ""
        if selected_service == "Other":
            custom_service_name = st.text_input("Type New Service Name*", key="custom_srv")

    with col_b:
        amount = st.number_input("Amount (₹)", min_value=0, step=10, key="new_amount")
        pay_mode = st.radio("Payment Mode", ["Cash", "Online"], key="new_pay")
        
        st.markdown("---")
        has_expiry = st.checkbox("Does it require renewal / validity?", key="has_exp")
        
        calculated_expiry = None
        if has_expiry:
            st.write("⏱️ **Set Validity / Expiry Duration:**")
            col_dur1, col_dur2 = st.columns(2)
            with col_dur1:
                duration_unit = st.selectbox("Validity Unit", ["Days", "Months", "Years"], index=1)
            with col_dur2:
                duration_val = st.number_input(f"Number of {duration_unit}", min_value=1, value=1 if duration_unit != "Days" else 7, step=1)
            
            if duration_unit == "Days":
                calculated_expiry = entry_date + timedelta(days=int(duration_val))
            elif duration_unit == "Months":
                calculated_expiry = entry_date + relativedelta(months=int(duration_val))
            elif duration_unit == "Years":
                calculated_expiry = entry_date + relativedelta(years=int(duration_val))
                
            st.info(f"📅 **Calculated Expiry Date:** {calculated_expiry.strftime('%d-%m-%Y')}")

    st.markdown("---")
    if st.button("💾 Save Entry", type="primary"):
        if name and mobile:
            final_service = selected_service
            if selected_service == "Other":
                if custom_service_name.strip():
                    final_service = custom_service_name.strip()
                    if final_service not in st.session_state.services_list:
                        st.session_state.services_list.insert(-1, final_service)
                else:
                    st.error("Please enter the custom service name!")
                    st.stop()
            
            exp_str = calculated_expiry.strftime("%Y-%m-%d") if calculated_expiry else "N/A"
            date_str = entry_date.strftime("%Y-%m-%d")
            
            add_record(date_str, name, mobile, final_service, amount, pay_mode, exp_str)
            st.success(f"✅ Entry saved successfully for Date: {entry_date.strftime('%d-%m-%Y')}")
            st.rerun()
        else:
            st.error("Please enter Name and Mobile Number!")

# TAB 3: ALERTS
with tab3:
    st.subheader("⚠️ Renewal Alerts (Next 15 Days)")
    today = datetime.now().date()
    alerts_found = False
    df = get_records()
    
    if not df.empty:
        for idx, row in df.iterrows():
            exp_val = row["Expiry"]
            if exp_val != "N/A" and exp_val != "" and exp_val is not None:
                try:
                    exp_d = datetime.strptime(str(exp_val), "%Y-%m-%d").date()
                    days_left = (exp_d - today).days
                    if 0 <= days_left <= 15:
                        alerts_found = True
                        formatted_exp = exp_d.strftime('%d-%m-%Y')
                        msg = f"Hello {row['Name']}, your {row['Service']} is expiring on {formatted_exp}. Please visit NOOR CYBER WORLD for renewal."
                        wa_link = f"https://wa.me/91{row['Mobile']}?text={msg.replace(' ', '%20')}"
                        st.warning(f"🔴 **{row['Name']}** - {row['Service']} (Expires: {formatted_exp} | {days_left} Days Left)")
                        st.markdown(f"[💬 Send WhatsApp Message]({wa_link})")
                except Exception:
                    pass
                    
    if not alerts_found:
        st.info("🎉 No renewals due in the next 15 days.")

# TAB 4: HISTORY & EDIT/DELETE (Date Filter Added)
with tab4:
    st.subheader("📂 History & Manage Entries (Search / Edit / Delete)")
    df = get_records()
    
    if df.empty:
        st.info("No records available in database.")
    else:
        # Date Filter Controls
        col_f1, col_f2 = st.columns([1, 2])
        with col_f1:
            filter_type = st.radio("Filter By Date:", ["Single Date", "Date Range", "All Records"])
        
        filtered_df = df.copy()
        
        with col_f2:
            if filter_type == "Single Date":
                selected_date = st.date_input("Select Date", datetime.now().date())
                sel_date_str = selected_date.strftime("%Y-%m-%d")
                filtered_df = df[df["Date"] == sel_date_str]
            elif filter_type == "Date Range":
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    start_d = st.date_input("From Date", datetime.now().date() - timedelta(days=7))
                with col_r2:
                    end_d = st.date_input("To Date", datetime.now().date())
                
                filtered_df = df[(df["Date"] >= start_d.strftime("%Y-%m-%d")) & (df["Date"] <= end_d.strftime("%Y-%m-%d"))]

        # Collection Summary for Selected Date / Filter
        st.markdown("---")
        if not filtered_df.empty:
            f_cash = int(filtered_df[filtered_df["Payment"] == "Cash"]["Amount"].sum())
            f_online = int(filtered_df[filtered_df["Payment"] == "Online"]["Amount"].sum())
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Selected Period Total", f"₹ {f_cash + f_online}")
            c2.metric("Selected Period Cash", f"₹ {f_cash}")
            c3.metric("Selected Period Online", f"₹ {f_online}")
            
            st.markdown("### 📋 Filtered Records Table")
            st.dataframe(filtered_df.drop(columns=["id"], errors="ignore"), use_container_width=True)
            
            st.markdown("---")
            st.markdown("### ✏️ Select Entry to Edit or Delete")
            
            options = {f"ID:{row['id']} | Date:{row['Date']} | {row['Name']} - {row['Service']} (₹{row['Amount']})": row['id'] for idx, row in filtered_df.iterrows()}
            selected_option = st.selectbox("Choose Entry:", list(options.keys()))
            selected_id = options[selected_option]
            
            curr_rec = df[df["id"] == selected_id].iloc[0]
            
            col_act1, col_act2 = st.columns([1, 3])
            with col_act1:
                if st.button("🗑️ Delete Selected Entry", type="primary"):
                    delete_record(selected_id)
                    st.success("🗑️ Entry deleted permanently!")
                    st.rerun()
            
            st.markdown("#### 📝 Edit Record Details:")
            with st.form("edit_entry_form"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    try:
                        curr_date_obj = datetime.strptime(str(curr_rec["Date"]), "%Y-%m-%d").date()
                    except:
                        curr_date_obj = datetime.now().date()
                        
                    e_date = st.date_input("Entry Date", value=curr_date_obj)
                    e_name = st.text_input("Customer Name", value=curr_rec["Name"])
                    e_mobile = st.text_input("Mobile Number", value=curr_rec["Mobile"])
                    
                    s_idx = st.session_state.services_list.index(curr_rec["Service"]) if curr_rec["Service"] in st.session_state.services_list else len(st.session_state.services_list)-1
                    e_service = st.selectbox("Service", st.session_state.services_list, index=s_idx)
                    
                with col_e2:
                    e_amount = st.number_input("Amount (₹)", value=int(curr_rec["Amount"]), step=10)
                    e_pay = st.radio("Payment Mode", ["Cash", "Online"], index=0 if curr_rec["Payment"] == "Cash" else 1)
                    e_expiry = st.text_input("Expiry Date (YYYY-MM-DD or N/A)", value=str(curr_rec["Expiry"]))
                    
                if st.form_submit_button("🔄 Update Entry"):
                    update_record(selected_id, e_date.strftime("%Y-%m-%d"), e_name, e_mobile, e_service, e_amount, e_pay, e_expiry)
                    st.success("✅ Entry updated successfully!")
                    st.rerun()
        else:
            st.warning("⚠️ No records found for the selected date filter.")
