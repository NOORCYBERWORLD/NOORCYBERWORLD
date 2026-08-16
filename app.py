import streamlit as st
import pandas as pd
import requests, json, io, os
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import quote
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ============================================================
# NOOR CYBER WORLD - COMPLETE APP WITH CYBER OFFICE BACKGROUND & 2X2 LOGO
# ============================================================

st.set_page_config(
    page_title="NOOR CYBER WORLD",
    page_icon="🖥️",
    layout="wide"
)

WEB_APP_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwSipN_etRHmOKXczikdg1gwzBvksliKCLQ0NYIJX9BbCGcyalc8H14aMTo_mNAbytK"
    "/exec"
)

IST = timezone(timedelta(hours=5, minutes=30))

COLUMNS = [
    "created_at", "name", "mobile", "service",
    "amount", "net_amount", "cash", "credit",
    "expiry", "_row_number"
]

# Comprehensive Digital & Maha e-Seva / Aaple Sarkar Services List
BASE_SERVICES = sorted([
    "7/12 Extract & 8A Utara (Land Record)",
    "Aadhaar Card Download / Update",
    "Age, Nationality & Domicile Certificate",
    "Ayushman Bharat Card (PM-JAY)",
    "Birth Certificate Application / Correction",
    "Caste Certificate & Validity",
    "Character Certificate (Police Verification)",
    "Death Certificate Application",
    "Digital Signature Certificate (DSC)",
    "Disability Certificate (UDID Card)",
    "Driving License (LL/DL) & RC Services",
    "E-Gazette Notification (Name/DOB Change)",
    "E-Panchayat & Gram Panchayat Services",
    "E-Shram Card",
    "Electricity / Gas / Water Bill Payment",
    "Encumbrance Certificate (Search Report)",
    "FSSAI Food License / Registration",
    "GST Registration & Return Filing",
    "Income Certificate",
    "Income Tax Return (ITR) Filing",
    "Kisan Credit Card (KCC) & Agri Schemes",
    "Labor Card / Worker Registration",
    "LPG Gas Booking & Transfer",
    "Mobile / DTH Recharge",
    "Money Transfer (DMT) / AEPS Cash Withdrawal",
    "Non-Creamy Layer Certificate",
    "PAN Card New / Correction",
    "Passport Application / Renewal",
    "PF / EPF Withdrawal & Claim",
    "PM Kisan Samman Nidhi / KYC Update",
    "Police Verification / NOC Application",
    "Property Tax & Water Tax Payment",
    "PVC Card Printing (Aadhaar/PAN/Voter)",
    "Railway / Bus / Air Ticket Booking",
    "Ration Card New / Transfer / Update",
    "Resume / Bio-Data & Online Form Filling",
    "Senior Citizen ID Card",
    "Shop Act License (Gumasta)",
    "Student Scholarship Form (MahaDBT)",
    "Udyam Aadhaar / MSME Registration",
    "Voter ID Card Apply / Correction",
    "Voter Registration & PVC Card",
    "Widow / Old Age / Pension Scheme Form",
    "Xerox / Color Printout / Lamination / Scanning"
], key=str.lower)

if "custom_services" not in st.session_state:
    st.session_state.custom_services = []
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now(IST).date()
if "editing_row" not in st.session_state:
    st.session_state.editing_row = None
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None
if "success_message" not in st.session_state:
    st.session_state.success_message = None
if "last_saved_wa" not in st.session_state:
    st.session_state.last_saved_wa = None
if "service_rows" not in st.session_state:
    st.session_state.service_rows = [{"service": BASE_SERVICES[0], "amount": 0}]
if "customer_type" not in st.session_state:
    st.session_state.customer_type = "KNOWN CUSTOMER"


def today_ist():
    return datetime.now(IST).date()

def services():
    return sorted(
        set(BASE_SERVICES + st.session_state.custom_services),
        key=str.lower
    ) + ["Other"]

def empty_df():
    return pd.DataFrame(columns=COLUMNS)

def clean_df(df):
    if df is None or df.empty:
        return empty_df()

    df = df.copy()

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = 0 if col in ["amount", "net_amount", "cash", "credit"] else ""

    for col in ["name", "mobile", "service", "expiry"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    raw = df["created_at"].fillna("").astype(str).str.strip()
    df["created_at"] = raw.str[:10]

    for col in ["amount", "net_amount", "cash", "credit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["_row_number"] = pd.to_numeric(
        df["_row_number"], errors="coerce"
    ).fillna(0).astype(int)

    return df[COLUMNS]

@st.cache_data(ttl=5)
def get_records():
    try:
        r = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_records",
                "t": int(datetime.now().timestamp())
            },
            timeout=20
        )
        if r.status_code != 200:
            return empty_df()
        data = r.json()
        return clean_df(pd.DataFrame(data))
    except Exception:
        return empty_df()

def get_expenses():
    try:
        r = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_expenses",
                "t": int(datetime.now().timestamp())
            },
            timeout=20
        )
        if r.status_code != 200:
            return []
        data = r.json()
        return data if isinstance(data, list) else []
    except Exception:
        return []

def auto_fill_customer_name():
    mobile = str(st.session_state.get("mobile_field_new", "")).strip()
    if not mobile:
        st.session_state["name_field_new"] = ""
        return
    try:
        found = get_records()
        if not found.empty:
            matches = found[found["mobile"].astype(str).str.strip() == mobile]
            if not matches.empty:
                st.session_state["name_field_new"] = str(matches.iloc[-1]["name"]).strip()
                return
    except Exception:
        pass
    st.session_state["name_field_new"] = ""

def post_api(payload):
    try:
        r = requests.post(
            WEB_APP_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        try:
            data = r.json()
            return bool(data.get("success")), str(
                data.get("message", data.get("error", "Request failed"))
            )
        except Exception:
            return r.status_code < 400, "Success"
    except Exception as e:
        return False, str(e)

# ============================================================
# STYLING: CYBER OFFICE BACKGROUND & 2X2 INCH LOGO
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&display=swap');

/* Premium Dynamic Cyber Office Background */
.stApp {
    background: 
        radial-gradient(circle at 15% 15%, rgba(34, 211, 238, 0.12), transparent 35%),
        radial-gradient(circle at 85% 20%, rgba(59, 130, 246, 0.12), transparent 40%),
        radial-gradient(circle at 50% 85%, rgba(16, 185, 129, 0.08), transparent 45%),
        linear-gradient(135deg, #030712 0%, #0b1329 50%, #060d19 100%);
    background-attachment: fixed;
    color: #f8fafc;
    font-family: Inter, sans-serif;
}

/* Container Spacing for Header Clarity */
.block-container {
    max-width: 1450px;
    padding-top: 5.5rem !important;
    padding-bottom: 3rem;
}

/* Header & Logo Container */
.nc-header-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 25px;
    margin-bottom: 20px;
}

/* 2x2 Inch Logo Styling (144px x 144px at standard 96 DPI) */
.nc-logo-img {
    width: 144px;
    height: 144px;
    object-fit: contain;
    filter: drop-shadow(0px 0px 12px rgba(34, 211, 238, 0.6));
    border-radius: 12px;
}

.nc-header-text {
    text-align: left;
}

.nc-title {
    font-family: Orbitron, Arial, sans-serif;
    font-size: 38px;
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: 3px;
    color: #22d3ee;
    text-shadow: 0 0 20px rgba(34, 211, 238, 0.5);
}

.nc-main-title {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 2.5px;
    color: #ffffff;
    margin-top: 5px;
}

.nc-sub {
    font-size: 12px;
    letter-spacing: 2px;
    color: #94a3b8;
    margin-top: 5px;
}

/* Glassmorphism Summary Card */
.nc-top {
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(34, 211, 238, 0.3);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    border-radius: 14px;
    padding: 12px 18px;
    text-align: center;
    font-size: 14px;
    line-height: 1.8;
}

.profit { color: #22c55e; font-weight: 800; }
.cash { color: #22c55e; font-weight: 800; }
.credit { color: #ef4444; font-weight: 800; }

.nc-section {
    font-family: Orbitron, sans-serif;
    font-size: 19px;
    font-weight: 700;
    color: #e2e8f0;
    margin: 10px 0 14px;
}

.nc-green { color: #22c55e; font-weight: 700; }
.nc-red { color: #ef4444; font-weight: 700; }

/* Metric Cards with Glowing Border Effect */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.7));
    border: 1px solid rgba(34, 211, 238, 0.25);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    border-radius: 15px;
    padding: 15px;
}

.stButton > button {
    border-radius: 9px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# Base64 logo conversion for seamless display
logo_html = ""
if os.path.exists("logo.png"):
    import base64
    with open("logo.png", "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" class="nc-logo-img" alt="Logo">'
else:
    logo_html = '<img src="logo.png" class="nc-logo-img" alt="Logo">'

st.markdown(f"""
<div class="nc-header-container">
  {logo_html}
  <div class="nc-header-text">
    <div class="nc-title">NOOR CYBER WORLD</div>
    <div class="nc-main-title">CUSTOMER MANAGEMENT SYSTEM</div>
    <div class="nc-sub">DIGITAL SERVICE • MAHA E-SEVA KENDRA • SMART RECORD</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================

df = get_records()
expenses = get_expenses()

if df.empty:
    df = empty_df()

selected_date = st.session_state.selected_date
selected_date_str = selected_date.strftime("%Y-%m-%d")

if not df.empty:
    day_df = df[df["created_at"].str[:10] == selected_date_str].copy()
else:
    day_df = empty_df()

# ============================================================
# TOP NET-INCOME SUMMARY
# ============================================================

if not df.empty:
    today_s = today_ist().strftime("%Y-%m-%d")
    month_s = today_ist().strftime("%Y-%m")
    year_s = today_ist().strftime("%Y")

    today_net = df.loc[df["created_at"].str[:10] == today_s, "net_amount"].sum()
    month_net = df.loc[df["created_at"].str[:7] == month_s, "net_amount"].sum()
    year_net = df.loc[df["created_at"].str[:4] == year_s, "net_amount"].sum()
else:
    today_net = month_net = year_net = 0

st.markdown(f"""
<div class="nc-top">
<b>📅 TODAY NET INCOME:</b> <span class="profit">₹ {today_net:,.0f}</span>
&nbsp;&nbsp; | &nbsp;&nbsp;
<b>🗓️ MONTH NET INCOME:</b> <span class="profit">₹ {month_net:,.0f}</span>
&nbsp;&nbsp; | &nbsp;&nbsp;
<b>📊 YEAR NET INCOME:</b> <span class="profit">₹ {year_net:,.0f}</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# DATE NAVIGATION
# ============================================================

p, d, n = st.columns([1,4,1])

with p:
    if st.button("❮ PREVIOUS DAY", use_container_width=True):
        st.session_state.selected_date -= timedelta(days=1)
        st.rerun()

with d:
    picked = st.date_input(
        "Working Date",
        value=selected_date,
        label_visibility="collapsed"
    )
    if picked != selected_date:
        st.session_state.selected_date = picked
        st.rerun()

with n:
    if st.button("NEXT DAY ❯", use_container_width=True):
        st.session_state.selected_date += timedelta(days=1)
        st.rerun()

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 TODAY'S ENTRIES & ADD ENTRY",
    "🔴 CREDIT COLLECTION",
    "🔔 RENEWAL ALERTS",
    "💸 SHOP EXPENSES & PROFIT",
    "📂 RECORDS & SEARCH"
])

# ============================================================
# TAB 1 - TODAY'S ENTRIES & ADD ENTRY
# ============================================================

with tab1:
    st.markdown(
        f"<div class='nc-section'>📋 Entries for {selected_date.strftime('%d-%m-%Y')}</div>",
        unsafe_allow_html=True
    )

    total_gross = int(day_df["amount"].sum()) if not day_df.empty else 0
    total_net = int(day_df["net_amount"].sum()) if not day_df.empty else 0
    cash_sum = int(day_df["cash"].sum()) if not day_df.empty else 0
    credit_sum = int(day_df["credit"].sum()) if not day_df.empty else 0

    a,b,c,e = st.columns(4)
    a.metric("TOTAL COLLECTION", f"₹ {total_gross:,}")
    b.metric("CASH RECEIVED", f"₹ {cash_sum:,}")
    c.metric("PENDING CREDIT", f"₹ {credit_sum:,}")
    e.metric("NET PROFIT", f"₹ {total_net:,}")

    st.markdown("---")

    if day_df.empty:
        st.info("ℹ️ No entries recorded for this date yet.")
    else:
        h_act, h_date, h_name, h_mob, h_serv, h_amt, h_net, h_cash, h_cred, h_exp = st.columns([0.8, 1, 1.8, 1.2, 2.5, 1, 1, 1, 1, 1])
        h_act.markdown("**Actions**")
        h_date.markdown("**Date**")
        h_name.markdown("**Name**")
        h_mob.markdown("**Mobile**")
        h_serv.markdown("**Service**")
        h_amt.markdown("**Amount**")
        h_net.markdown("**Net Profit**")
        h_cash.markdown("**Cash**")
        h_cred.markdown("**Credit**")
        h_exp.markdown("**Expiry**")
        st.markdown("<div style='height:2px; background:rgba(34,211,238,0.3); margin:4px 0 10px;'></div>", unsafe_allow_html=True)

        for index, row in day_df.iterrows():
            rn = int(row["_row_number"])
            c_act, c_date, c_name, c_mob, c_serv, c_amt, c_net, c_cash, c_cred, c_exp = st.columns([0.8, 1, 1.8, 1.2, 2.5, 1, 1, 1, 1, 1])
            
            with c_act:
                e_col, d_col = st.columns(2)
                with e_col:
                    if st.button("✏️", key=f"edit_t1_{rn}"):
                        st.session_state.editing_row = row.to_dict()
                        st.session_state.editing_services_loaded = False
                        st.rerun()
                with d_col:
                    if st.button("🗑️", key=f"del_t1_{rn}"):
                        st.session_state.confirm_delete = rn
                        st.rerun()
            
            with c_date: st.write(row['created_at'])
            
            cred_float = float(row['credit'])
            with c_name:
                text_cls = "nc-red" if cred_float > 0 else "nc-green"
                st.markdown(f"<span class='{text_cls}'>{row['name']}</span>", unsafe_allow_html=True)
                
            with c_mob: st.write(row['mobile'])
            with c_serv: st.write(row['service'])
            with c_amt: st.write(f"₹ {float(row['amount']):,.0f}")
            with c_net: st.write(f"₹ {float(row['net_amount']):,.0f}")
            with c_cash: st.write(f"₹ {float(row['cash']):,.0f}")
            with c_cred:
                st.markdown(f"<span class='{text_cls}'>₹ {cred_float:,.0f}</span>", unsafe_allow_html=True)
            with c_exp: st.write(row['expiry'])
            
            st.markdown("<div style='height:1px; background:rgba(255,255,255,0.05); margin:2px 0 6px;'></div>", unsafe_allow_html=True)

    if st.session_state.confirm_delete:
        rn = st.session_state.confirm_delete
        st.warning("⚠️ Confirm deletion of this customer entry.")
        y, no = st.columns(2)
        with y:
            if st.button("YES, DELETE", type="primary", use_container_width=True):
                ok, msg = post_api({"action":"delete","row_number":rn})
                if ok:
                    st.session_state.confirm_delete = None
                    get_records.clear()
                    st.session_state.success_message = "Entry deleted successfully."
                    st.rerun()
                else:
                    st.error(msg)
        with no:
            if st.button("NO, CANCEL", use_container_width=True):
                st.session_state.confirm_delete = None
                st.rerun()

    st.markdown("---")

    # ========================================================
    # ENTRY FORM (BALANCED 2 COLUMNS)
    # ========================================================

    editing = st.session_state.editing_row is not None
    old = st.session_state.editing_row or {}

    if editing and not st.session_state.get("editing_services_loaded", False):
        old_services = [x.strip() for x in str(old.get("service", "")).split(",") if x.strip()]
        if not old_services:
            old_services = [BASE_SERVICES[0]]
        for svc in old_services:
            if svc not in BASE_SERVICES and svc not in st.session_state.custom_services:
                st.session_state.custom_services.append(svc)
        st.session_state.service_rows = [
            {"service": old_services[0], "amount": int(float(old.get("amount", 0)))}
        ]
        for svc in old_services[1:]:
            st.session_state.service_rows.append({"service": svc, "amount": 0})
        st.session_state.editing_services_loaded = True

    if not editing and st.session_state.get("editing_services_loaded", False):
        st.session_state.editing_services_loaded = False
        st.session_state.service_rows = [{"service": BASE_SERVICES[0], "amount": 0}]

    st.markdown(
        "<div class='nc-section'>{}</div>".format(
            "✏️ EDIT CUSTOMER ENTRY" if editing else "➕ ADD NEW CUSTOMER ENTRY"
        ),
        unsafe_allow_html=True
    )

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Customer Details**")
        if editing:
            mobile = st.text_input(
                "Mobile Number *",
                value=str(old.get("mobile", "")),
                key=f"mobile_field_edit_{int(old.get('_row_number', 0))}"
            ).strip()
            name = st.text_input(
                "Customer Name *",
                value=str(old.get("name", "")),
                key=f"name_field_edit_{int(old.get('_row_number', 0))}"
            ).strip()
        else:
            customer_type = st.radio(
                "Customer Type",
                ["KNOWN CUSTOMER", "UNKNOWN CUSTOMER"],
                horizontal=True,
                key="customer_type"
            )
            unknown_customer = customer_type == "UNKNOWN CUSTOMER"

            mobile = st.text_input(
                "Mobile Number *",
                key="mobile_field_new",
                disabled=unknown_customer,
                on_change=auto_fill_customer_name
            ).strip()

            if unknown_customer:
                st.session_state["name_field_new"] = "UNKNOWN"

            name = st.text_input(
                "Customer Name *",
                key="name_field_new",
                disabled=unknown_customer
            ).strip()

        st.markdown("**Services Selection**")
        svcs = services()
        service_values = []
        total_service_amount = 0

        for i, item in enumerate(st.session_state.service_rows):
            service_col, amount_col = st.columns([3.5, 1.5])

            current_service = str(item.get("service", svcs[0]))
            if current_service not in svcs:
                st.session_state.custom_services.append(current_service)
                svcs = services()

            service_index = svcs.index(current_service) if current_service in svcs else 0

            with service_col:
                selected = st.selectbox(
                    f"Service {i + 1}",
                    svcs,
                    index=service_index,
                    key=f"service_field_{i}"
                )

                custom_value = ""
                if selected == "Other":
                    custom_value = st.text_input(
                        f"Enter Custom Service {i + 1}",
                        key=f"custom_service_field_{i}"
                    ).strip()
                    if custom_value and custom_value not in st.session_state.custom_services:
                        st.session_state.custom_services.append(custom_value)
                        selected = custom_value

            with amount_col:
                svc_amount = st.number_input(
                    f"Amount {i + 1} (₹)",
                    min_value=0,
                    step=10,
                    value=int(item.get("amount", 0)),
                    key=f"service_amount_{i}"
                )

            service_values.append(selected)
            total_service_amount += int(svc_amount)

        if st.button("＋ ADD MORE SERVICE", key="add_service_button"):
            st.session_state.service_rows.append({"service": svcs[0], "amount": 0})
            st.rerun()

    with col_right:
        st.markdown("**Billing & Payment Details**")
        amount = total_service_amount
        st.markdown(
            f"<div style=\"font-weight:800;font-size:16px;margin:5px 0 12px;color:#f8fafc\">TOTAL FEE / GROSS AMOUNT: <span style=\"color:#22d3ee\">₹ {int(amount):,}</span></div>",
            unsafe_allow_html=True
        )

        net_amount = st.number_input(
            "Net Income / Profit (₹) *",
            min_value=0,
            step=10,
            value=int(float(old.get("net_amount", 0))) if editing else 0,
            key="net_field"
        )

        old_credit = float(old.get("credit", 0)) if editing else 0
        pay_index = 1 if old_credit > 0 else 0
        payment = st.radio(
            "Payment Type *",
            ["💵 CASH", "🔴 CREDIT (UDHARI)"],
            index=pay_index,
            horizontal=True,
            key="payment_field"
        )

        if "CREDIT" in payment:
            cash_value = 0
            credit_value = int(amount)
        else:
            cash_value = int(amount)
            credit_value = 0

        st.info(f"💵 Cash: ₹ {cash_value:,}   |   🔴 Credit: ₹ {credit_value:,}")

        expiry_exists = str(old.get("expiry", "N/A")).strip() not in ["", "N/A"]
        has_expiry = st.checkbox(
            "Requires Renewal / Validity?",
            value=expiry_exists,
            key="has_expiry"
        )

        if has_expiry:
            v_unit_col, v_dur_col = st.columns(2)
            with v_unit_col:
                unit = st.selectbox(
                    "Validity Unit",
                    ["Days", "Months", "Years"],
                    index=1,
                    key="validity_unit"
                )
            with v_dur_col:
                duration = st.number_input(
                    "Validity Duration",
                    min_value=1,
                    value=1,
                    step=1,
                    key="validity_duration"
                )
        else:
            unit = "Months"
            duration = 1

    st.markdown("<br>", unsafe_allow_html=True)
    save, cancel = st.columns(2)

    with save:
        label = "💾 UPDATE ENTRY" if editing else "⚡ SAVE ENTRY"

        if st.button(label, type="primary", use_container_width=True):
            unknown_customer = (not editing and st.session_state.get("customer_type") == "UNKNOWN CUSTOMER")

            if unknown_customer:
                name = "UNKNOWN"
                mobile = "UNKNOWN"
            elif not name or not mobile:
                st.error("Please enter Customer Name and Mobile Number.")
                st.stop()

            final_services = [str(x).strip() for x in service_values if str(x).strip() and str(x).strip() != "Other"]
            if not final_services:
                st.error("Please select at least one service.")
                st.stop()

            final_service = ", ".join(final_services)

            for svc in final_services:
                if svc not in BASE_SERVICES and svc not in st.session_state.custom_services:
                    st.session_state.custom_services.append(svc)

            if int(net_amount) > int(amount):
                st.error("Net Income / Profit cannot be greater than Total Fee.")
                st.stop()

            expiry = "N/A"
            if has_expiry:
                base = selected_date
                if unit == "Days":
                    exp = base + timedelta(days=int(duration))
                elif unit == "Months":
                    exp = base + relativedelta(months=int(duration))
                else:
                    exp = base + relativedelta(years=int(duration))
                expiry = exp.strftime("%Y-%m-%d")

            payload = {
                "action": "edit" if editing else "add",
                "created_at": selected_date_str,
                "name": name,
                "mobile": mobile,
                "service": final_service,
                "amount": str(int(amount)),
                "net_amount": str(int(net_amount)),
                "cash": str(cash_value),
                "credit": str(credit_value),
                "expiry": expiry
            }

            if editing:
                payload["row_number"] = int(old["_row_number"])

            ok, msg = post_api(payload)

            if ok:
                get_records.clear()
                st.session_state.editing_row = None
                st.session_state.editing_services_loaded = False
                st.session_state.service_rows = [{"service": BASE_SERVICES[0], "amount": 0}]
                st.session_state.customer_type = "KNOWN CUSTOMER"
                for key in ["mobile_field_new", "name_field_new", "net_field"]:
                    st.session_state.pop(key, None)
                st.session_state.last_saved_wa = (
                    "https://wa.me/91" + mobile +
                    "?text=" + quote(
                        f"Dear {name}, Thank you for choosing NOOR CYBER WORLD "
                        f"for {final_service}! Total Amount: Rs.{int(amount)}."
                    )
                ) if mobile else None
                st.session_state.success_message = "Entry saved successfully."
                st.rerun()
            else:
                st.error(f"Failed to save: {msg}")

    with cancel:
        if editing and st.button("❌ CANCEL EDIT", use_container_width=True):
            st.session_state.editing_row = None
            st.session_state.editing_services_loaded = False
            st.session_state.service_rows = [{"service": BASE_SERVICES[0], "amount": 0}]
            st.rerun()

    if st.session_state.last_saved_wa:
        st.link_button(
            "💬 SEND THANK YOU WHATSAPP",
            st.session_state.last_saved_wa,
            use_container_width=True
        )

# ============================================================
# TAB 2 - CREDIT
# ============================================================

with tab2:
    st.markdown(
        "<div class='nc-section'>🔴 PENDING CREDIT / UDHARI COLLECTION</div>",
        unsafe_allow_html=True
    )

    credit_df = df[df["credit"] > 0].copy() if not df.empty else empty_df()

    if credit_df.empty:
        st.success("🎉 No pending credit! All payments are clear.")
    else:
        pending = int(credit_df["credit"].sum())
        st.error(f"⚠️ Total Pending Credit: ₹ {pending:,} ({len(credit_df)} Entries)")

        for _, row in credit_df.iterrows():
            rn = int(row["_row_number"])
            c_info, c_wa, c_cash = st.columns([6,2,2])

            with c_info:
                st.markdown(
                    f"""<div style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <b class="nc-red">🔴 {row['name']}</b> ({row['mobile']})<br>
                    Service: {row['service']}<br>
                    Pending: <b class="nc-red">₹ {float(row['credit']):,.0f}</b> | Date: {row['created_at']}
                    </div>""",
                    unsafe_allow_html=True
                )

            with c_wa:
                msg = quote(
                    f"Hello {row['name']}, this is a gentle reminder from "
                    f"NOOR CYBER WORLD. Your payment of Rs.{int(row['credit'])} "
                    f"for {row['service']} is pending. Please clear your balance. Thank you!"
                )
                st.link_button(
                    "💬 SEND REMINDER",
                    f"https://wa.me/91{str(row['mobile']).strip()}?text={msg}",
                    use_container_width=True
                )

            with c_cash:
                if st.button(
                    "💵 CASH RECEIVED",
                    key=f"credit_cash_{rn}",
                    use_container_width=True
                ):
                    ok, msg = post_api({
                        "action":"credit_to_cash",
                        "row_number":rn
                    })
                    if ok:
                        get_records.clear()
                        st.session_state.success_message = (
                            f"₹ {int(row['credit'])} received from {row['name']}."
                        )
                        st.rerun()
                    else:
                        st.error(msg)

# ============================================================
# TAB 3 - RENEWALS
# ============================================================

with tab3:
    st.markdown(
        "<div class='nc-section'>🔔 RENEWAL ALERTS — NEXT 15 DAYS</div>",
        unsafe_allow_html=True
    )

    alerts = []
    today = today_ist()

    for _, row in df.iterrows():
        exp = str(row["expiry"]).strip()
        if exp and exp != "N/A":
            try:
                ed = datetime.strptime(exp[:10], "%Y-%m-%d").date()
                left = (ed - today).days
                if 0 <= left <= 15:
                    alerts.append((row,ed,left))
            except Exception:
                pass

    if not alerts:
        st.success("🎉 No renewals due in the next 15 days.")
    else:
        st.warning(f"⚠️ {len(alerts)} renewal(s) pending.")
        for row,ed,left in alerts:
            date_text = ed.strftime("%d-%m-%Y")
            c_info, c_wa = st.columns([8,2])
            with c_info:
                st.markdown(
                    f"""<div style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <b class="nc-red">🔴 {row['name']}</b> ({row['mobile']})<br>
                    Service: {row['service']}<br>
                    Expiry: <b class="nc-red">{date_text}</b> — {left} days remaining
                    </div>""",
                    unsafe_allow_html=True
                )
            with c_wa:
                msg = quote(
                    f"Hello {row['name']}, your service {row['service']} "
                    f"is expiring on {date_text}. Please visit NOOR CYBER WORLD to renew it."
                )
                st.link_button(
                    f"💬 SEND WHATSAPP",
                    f"https://wa.me/91{str(row['mobile']).strip()}?text={msg}",
                    use_container_width=True
                )

# ============================================================
# TAB 4 - EXPENSES
# ============================================================

with tab4:
    st.markdown(
        "<div class='nc-section'>💸 SHOP EXPENSES & REAL PROFIT</div>",
        unsafe_allow_html=True
    )

    left,right = st.columns([1,2])

    with left:
        exp_title = st.text_input(
            "Expense Title",
            key="exp_title"
        )
        exp_amount = st.number_input(
            "Expense Amount (₹)",
            min_value=0,
            step=10,
            key="exp_amount"
        )

        if st.button(
            "💾 ADD EXPENSE",
            type="primary",
            use_container_width=True
        ):
            if not exp_title.strip() or exp_amount <= 0:
                st.error("Enter valid expense title and amount.")
            else:
                ok,msg = post_api({
                    "action":"add_expense",
                    "created_at":selected_date_str,
                    "title":exp_title.strip(),
                    "amount":str(int(exp_amount))
                })
                if ok:
                    st.session_state.success_message = "Expense added."
                    st.rerun()
                else:
                    st.error(msg)

    with right:
        selected_expenses = [
            x for x in expenses
            if str(x.get("created_at",""))[:10] == selected_date_str
        ]

        total_exp = sum(float(x.get("amount",0)) for x in selected_expenses)
        actual_saving = total_net - total_exp

        x1,x2,x3 = st.columns(3)
        x1.metric("NET PROFIT", f"₹ {total_net:,}")
        x2.metric("EXPENSES", f"₹ {total_exp:,.0f}")
        x3.metric("ACTUAL SAVINGS", f"₹ {actual_saving:,.0f}")

        if selected_expenses:
            st.markdown("#### 🔴 Today's Expenses")
            for exp in selected_expenses:
                rn = int(exp.get("_row_number",0))
                aa,bb = st.columns([8,1])
                with aa:
                    st.markdown(
                        f"""<div style="padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); color:#ef4444;">
                        <b>💸 {exp.get('title','')}</b>
                        &nbsp; — &nbsp; ₹ {float(exp.get('amount',0)):,.0f}
                        </div>""",
                        unsafe_allow_html=True
                    )
                with bb:
                    if rn and st.button("🗑️", key=f"expdel_{rn}"):
                        ok,msg = post_api({
                            "action":"delete_expense",
                            "row_number":rn
                        })
                        if ok:
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("No expenses recorded for this date.")

# ============================================================
# TAB 5 - ALL RECORDS & SEARCH
# ============================================================

with tab5:
    st.markdown(
        "<div class='nc-section'>📂 ALL CUSTOMER RECORDS & SEARCH</div>",
        unsafe_allow_html=True
    )

    if df.empty:
        st.info("No records available.")
    else:
        q = st.text_input(
            "🔍 Search Name / Mobile / Service / Date",
            key="search_records"
        ).strip().lower()

        filtered = df.copy()
        filtered = filtered.sort_values(by="created_at", ascending=False)

        if q:
            filtered = filtered[
                filtered["name"].str.lower().str.contains(q, na=False)
                | filtered["mobile"].str.lower().str.contains(q, na=False)
                | filtered["service"].str.lower().str.contains(q, na=False)
                | filtered["created_at"].str.lower().str.contains(q, na=False)
            ]

        export = filtered.drop(columns=["_row_number"], errors="ignore")

        b1, b2 = st.columns(2)
        with b1:
            st.download_button(
                "📥 DOWNLOAD CSV",
                export.to_csv(index=False).encode("utf-8-sig"),
                "NOOR_CYBER_WORLD_ALL_RECORDS.csv",
                "text/csv",
                use_container_width=True
            )

        with b2:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=20, leftMargin=20,
                topMargin=20, bottomMargin=20
            )
            styles = getSampleStyleSheet()
            elements = [
                Paragraph(
                    "NOOR CYBER WORLD - ALL CUSTOMER RECORDS",
                    ParagraphStyle(
                        "title",
                        parent=styles["Heading1"],
                        alignment=1,
                        fontSize=16
                    )
                ),
                Spacer(1, 10)
            ]

            rows = [[
                "Date", "Name", "Mobile", "Service",
                "Gross", "Net", "Cash", "Credit", "Expiry"
            ]]

            for _, r in export.iterrows():
                rows.append([
                    str(r["created_at"]),
                    str(r["name"]),
                    str(r["mobile"]),
                    str(r["service"]),
                    f"Rs. {float(r['amount']):.0f}",
                    f"Rs. {float(r['net_amount']):.0f}",
                    f"Rs. {float(r['cash']):.0f}",
                    f"Rs. {float(r['credit']):.0f}",
                    str(r["expiry"])
                ])

            tbl = Table(rows, repeatRows=1)
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("ALIGN", (0, 0), (-1, -1), "CENTER")
            ]))
            elements.append(tbl)
            doc.build(elements)
            buffer.seek(0)

            st.download_button(
                "📄 DOWNLOAD PDF",
                buffer.getvalue(),
                "NOOR_CYBER_WORLD_ALL_RECORDS.pdf",
                "application/pdf",
                use_container_width=True
            )

        st.caption(f"Showing {len(filtered)} total records (latest first)")

        rh_act, rh_date, rh_name, rh_mob, rh_serv, rh_amt, rh_net, rh_cash, rh_cred, rh_exp = st.columns([0.8, 1, 1.8, 1.2, 2.5, 1, 1, 1, 1, 1])
        rh_act.markdown("**Actions**")
        rh_date.markdown("**Date**")
        rh_name.markdown("**Name**")
        rh_mob.markdown("**Mobile**")
        rh_serv.markdown("**Service**")
        rh_amt.markdown("**Amount**")
        rh_net.markdown("**Net Profit**")
        rh_cash.markdown("**Cash**")
        rh_cred.markdown("**Credit**")
        rh_exp.markdown("**Expiry**")
        st.markdown("<div style='height:2px; background:rgba(34,211,238,0.3); margin:4px 0 10px;'></div>", unsafe_allow_html=True)

        for _, row in filtered.iterrows():
            rn = int(row["_row_number"])
            c_act, c_date, c_name, c_mob, c_serv, c_amt, c_net, c_cash, c_cred, c_exp = st.columns([0.8, 1, 1.8, 1.2, 2.5, 1, 1, 1, 1, 1])
            
            with c_act:
                e_col, d_col = st.columns(2)
                with e_col:
                    if st.button("✏️", key=f"rec_edit_{rn}"):
                        st.session_state.editing_row = row.to_dict()
                        try:
                            st.session_state.selected_date = datetime.strptime(
                                str(row["created_at"])[:10],
                                "%Y-%m-%d"
                            ).date()
                        except Exception:
                            pass
                        st.session_state.last_saved_wa = None
                        st.rerun()
                with d_col:
                    if st.button("🗑️", key=f"rec_del_{rn}"):
                        st.session_state.confirm_delete = rn
                        st.rerun()

            with c_date: st.write(row['created_at'])
            
            cred_float = float(row['credit'])
            with c_name:
                text_cls = "nc-red" if cred_float > 0 else "nc-green"
                st.markdown(f"<span class='{text_cls}'>{row['name']}</span>", unsafe_allow_html=True)

            with c_mob: st.write(row['mobile'])
            with c_serv: st.write(row['service'])
            with c_amt: st.write(f"₹ {float(row['amount']):,.0f}")
            with c_net: st.write(f"₹ {float(row['net_amount']):,.0f}")
            with c_cash: st.write(f"₹ {float(row['cash']):,.0f}")
            with c_cred:
                st.markdown(f"<span class='{text_cls}'>₹ {cred_float:,.0f}</span>", unsafe_allow_html=True)
            with c_exp: st.write(row['expiry'])
            
            st.markdown("<div style='height:1px; background:rgba(255,255,255,0.05); margin:2px 0 6px;'></div>", unsafe_allow_html=True)

# ============================================================
# GLOBAL DELETE CONFIRMATION
# ============================================================

if st.session_state.confirm_delete:
    rn = st.session_state.confirm_delete
    st.warning(f"⚠️ Confirm delete for Google Sheet row {rn}.")
    y,n = st.columns(2)

    with y:
        if st.button(
            "YES, DELETE ENTRY",
            key="global_yes_delete",
            type="primary",
            use_container_width=True
        ):
            ok,msg = post_api({
                "action":"delete",
                "row_number":rn
            })
            if ok:
                st.session_state.confirm_delete = None
                get_records.clear()
                st.session_state.success_message = "Entry deleted successfully."
                st.rerun()
            else:
                st.error(msg)

    with n:
        if st.button(
            "NO, KEEP ENTRY",
            key="global_no_delete",
            use_container_width=True
        ):
            st.session_state.confirm_delete = None
            st.rerun()

# ============================================================
# TOAST
# ============================================================

if st.session_state.success_message:
    st.toast(st.session_state.success_message, icon="✅")
    st.session_state.success_message = None
