import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# Page Config
st.set_page_config(page_title="NOOR CYBER WORLD", page_icon="🖥️", layout="wide")

# App Header
st.title("🖥️ NOOR CYBER WORLD")
st.caption("Center Management & Renewal Reminder System")

# GOOGLE SCRIPT WEB APP URL (CONNECTED TO YOUR GOOGLE DRIVE)
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxZ7tWX0eVwncDm-M1_rTkhaSbUceneoXFZeZL1iqhA8y_Wvd6O0VtLXxvrJvrVNsg/exec"

# Session State for Dynamic Services List (Auto-Add Feature)
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

# Fetch Data from Google Sheets in Google Drive
def fetch_records():
    if GOOGLE_SCRIPT_URL:
        try:
            res = requests.get(GOOGLE_SCRIPT_URL)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list):
                    return data
        except Exception as e:
            pass
    return st.session_state.get("records", [])

# Always load fresh records from Google Drive
st.session_state.records = fetch_records()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ New Entry", "🔔 Renewal Alerts", "⚙️ Manage Entries (Edit/Delete)"])

# TAB 1: DASHBOARD
with tab1:
    st.subheader("Today's Overview")
    
    col_ref1, col_ref2 = st.columns([4, 1])
    with col_ref2:
        if st.button("🔄 Sync with Google Drive"):
            st.session_state.records = fetch_records()
            st.rerun()

    df = pd.DataFrame(st.session_state.records)
    
    if not df.empty and "Payment" in df.columns and "Amount" in df.columns:
        total_cash = int(pd.to_numeric(df[df["Payment"] == "Cash"]["Amount"], errors='coerce').sum())
        total_online = int(pd.to_numeric(df[df["Payment"] == "Online"]["Amount"], errors='coerce').sum())
    else:
        total_cash = 0
        total_online = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Collection", f"₹ {total_cash + total_online}")
    col2.metric("Cash Collection", f"₹ {total_cash}")
    col3.metric("Online / UPI", f"₹ {total_online}")
    
    st.markdown("---")
    st.dataframe(df, use_container_width=True)

# TAB 2: NEW ENTRY
with tab2:
    st.subheader("New Service Entry")
    with st.form("entry_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input("Customer Name*")
            mobile = st.text_input("Mobile Number*")
            selected_service = st.selectbox("Search / Select Service*", st.session_state.services_list)
            
            # Show Textbox if 'Other' is selected
            custom_service_name = ""
            if selected_service == "Other":
                custom_service_name = st.text_input("Type New Service Name (Will Auto-Add to List)*")

        with col_b:
            amount = st.number_input("Amount (₹)", min_value=0, step=10)
            pay_mode = st.radio("Payment Mode", ["Cash", "Online"])
            has_expiry = st.checkbox("Does it require renewal?")
            expiry_date = st.date_input("Expiry Date") if has_expiry else None
            
        if st.form_submit_button("💾 Save Entry"):
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
                
                exp_str = expiry_date.strftime("%Y-%m-%d") if expiry_date else "N/A"
                
                new_entry = {
                    "name": name,
                    "mobile": mobile,
                    "service": final_service,
                    "amount": amount,
                    "payment": pay_mode,
                    "expiry": exp_str
                }
                
                # Save to Google Drive Sheet via Web App
                try:
                    requests.post(GOOGLE_SCRIPT_URL, json=new_entry)
                    st.success(f"✅ Successfully saved to Google Drive: {final_service}")
                except Exception as e:
                    st.error(f"Save failed: {e}")

                # Refresh records
                st.session_state.records = fetch_records()
                st.rerun()
            else:
                st.error("Please enter Name and Mobile Number!")

# TAB 3: ALERTS
with tab3:
    st.subheader("⚠️ Renewal Alerts (Next 15 Days)")
    today = datetime.now().date()
    alerts_found = False
    
    for item in st.session_state.records:
        exp_val = item.get("Expiry", "N/A")
        if exp_val != "N/A" and exp_val != "":
            try:
                exp_d = datetime.strptime(str(exp_val), "%Y-%m-%d").date()
                days_left = (exp_d - today).days
                if 0 <= days_left <= 15:
                    alerts_found = True
                    msg = f"Hello {item.get('Name')}, your {item.get('Service')} is expiring on {item.get('Expiry')}. Please visit NOOR CYBER WORLD for renewal."
                    wa_link = f"https://wa.me/91{item.get('Mobile')}?text={msg.replace(' ', '%20')}"
                    st.warning(f"🔴 **{item.get('Name')}** - {item.get('Service')} (Expires: {item.get('Expiry')} | {days_left} Days Left)")
                    st.markdown(f"[💬 Send WhatsApp Message]({wa_link})")
            except Exception:
                pass
                
    if not alerts_found:
        st.info("🎉 No renewals due in the next 15 days.")

# TAB 4: EDIT/DELETE
with tab4:
    st.subheader("⚙️ Manage Entries (Edit / Delete)")
    if not st.session_state.records:
        st.info("No records available in Google Drive.")
    else:
        options = [f"{i+1}. {r.get('Name')} - {r.get('Service')} (₹{r.get('Amount')})" for i, r in enumerate(st.session_state.records)]
        idx = st.selectbox("Select entry to modify:", range(len(options)), format_func=lambda x: options[x])
        
        curr_rec = st.session_state.records[idx]
        st.markdown("---")
        
        if st.button("🗑️ Delete Selected Entry", type="primary"):
            st.session_state.records.pop(idx)
            st.success("🗑️ Entry deleted locally!")
            st.rerun()
            
        st.markdown("---")
        st.markdown("#### ✏️ Edit Selected Entry:")
        
        with st.form("edit_entry_form"):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                e_name = st.text_input("Customer Name", value=curr_rec.get("Name", ""))
                e_mobile = st.text_input("Mobile Number", value=curr_rec.get("Mobile", ""))
                
                s_idx = st.session_state.services_list.index(curr_rec.get("Service")) if curr_rec.get("Service") in st.session_state.services_list else len(st.session_state.services_list)-1
                e_service = st.selectbox("Service", st.session_state.services_list, index=s_idx)
                
            with col_e2:
                e_amount = st.number_input("Amount (₹)", value=int(curr_rec.get("Amount", 0)) if str(curr_rec.get("Amount", 0)).isdigit() else 0, step=10)
                e_pay = st.radio("Payment Mode", ["Cash", "Online"], index=0 if curr_rec.get("Payment") == "Cash" else 1)
                
            if st.form_submit_button("🔄 Update Entry"):
                st.session_state.records[idx]["Name"] = e_name
                st.session_state.records[idx]["Mobile"] = e_mobile
                st.session_state.records[idx]["Service"] = e_service
                st.session_state.records[idx]["Amount"] = e_amount
                st.session_state.records[idx]["Payment"] = e_pay
                st.success("✅ Entry updated successfully!")
                st.rerun()
