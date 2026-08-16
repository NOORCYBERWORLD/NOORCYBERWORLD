import io
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st
from dateutil.relativedelta import relativedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ============================================================
# NOOR CYBER WORLD - PROFESSIONAL / LIGHTWEIGHT APP
# ============================================================

WEB_APP_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwSipN_etRHmOKXczikdg1gwzBvksliKCLQ0NYIJX9BbCGcyalc8H14aMTo_mNAbytK"
    "/exec"
)

IST = timezone(timedelta(hours=5, minutes=30))
LOGO_PATH = "logo.png"  # Put your logo.png beside app.py when available.

st.set_page_config(
    page_title="NOOR CYBER WORLD",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🖥️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

COLUMNS = [
    "created_at", "name", "mobile", "service", "amount", "net_amount",
    "cash", "credit", "expiry", "_row_number"
]

BASE_SERVICES = sorted([
    "Aadhaar Card Download / Update",
    "Ayushman Bharat Card",
    "Caste Certificate",
    "Digital Signature (DSC)",
    "Domicile Certificate",
    "Driving License (LL/DL) & RC Services",
    "E-Shram Card",
    "Electricity / Gas / Water Bill Payment",
    "FSSAI Food License",
    "Gazette Notification / Name Change",
    "GST Registration & Return Filing",
    "Income Certificate",
    "Income Tax Return (ITR) Filing",
    "Money Transfer (DMT) / AEPS Cash Withdrawal",
    "Mobile / DTH Recharge",
    "Non-Creamy Layer Certificate",
    "PAN Card New / Correction",
    "Passport Application",
    "PF / EPF Withdrawal & Claim",
    "Police Verification Application",
    "PM Kisan Samman Nidhi / KYC",
    "PVC Card Printing",
    "Railway / Bus / Air Ticket Booking",
    "Ration Card Services",
    "Resume / Bio-Data Making",
    "Shop Act License",
    "Udyam Aadhaar / MSME Registration",
    "Voter ID Card Apply / Correction",
    "Xerox / Color Printout / Lamination / Scanning",
], key=str.lower)

# ============================================================
# SESSION STATE
# ============================================================

def init_state():
    defaults = {
        "selected_date": datetime.now(IST).date(),
        "editing_row": None,
        "confirm_delete": None,
        "confirm_expense_delete": None,
        "success_message": None,
        "last_saved_wa": None,
        "custom_services": [],
        "service_count": 1,
        "service_values": [BASE_SERVICES[0]],
        "service_amounts": [0],
        "mobile_recall": "",
        "recalled_name": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# ============================================================
# HELPERS
# ============================================================

def today_ist():
    return datetime.now(IST).date()


def empty_df():
    return pd.DataFrame(columns=COLUMNS)


def clean_df(df):
    if df is None or df.empty:
        return empty_df()
    df = df.copy()
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = 0 if col in {"amount", "net_amount", "cash", "credit"} else ""
    for col in ["name", "mobile", "service", "expiry"]:
        df[col] = df[col].fillna("").astype(str).str.strip()
    # Keep ISO date as plain text. Never use pd.to_datetime here.
    df["created_at"] = df["created_at"].fillna("").astype(str).str[:10]
    for col in ["amount", "net_amount", "cash", "credit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["_row_number"] = pd.to_numeric(df["_row_number"], errors="coerce").fillna(0).astype(int)
    return df[COLUMNS]


def service_list():
    return sorted(set(BASE_SERVICES + st.session_state.custom_services), key=str.lower) + ["Other"]


def invalidate_data():
    get_records.clear()
    get_expenses.clear()
    get_services.clear()
    get_payments.clear()
    get_recurring.clear()


@st.cache_data(ttl=20, show_spinner=False)
def get_records():
    try:
        r = requests.get(WEB_APP_URL, params={"action": "get_records"}, timeout=12)
        data = r.json() if r.ok else []
        return clean_df(pd.DataFrame(data if isinstance(data, list) else []))
    except Exception:
        return empty_df()


@st.cache_data(ttl=20, show_spinner=False)
def get_expenses():
    try:
        r = requests.get(WEB_APP_URL, params={"action": "get_expenses"}, timeout=12)
        data = r.json() if r.ok else []
        return data if isinstance(data, list) else []
    except Exception:
        return []


@st.cache_data(ttl=60, show_spinner=False)
def get_services():
    try:
        r = requests.get(WEB_APP_URL, params={"action": "get_services"}, timeout=12)
        data = r.json() if r.ok else []
        return [str(x).strip() for x in data if str(x).strip()]
    except Exception:
        return []


@st.cache_data(ttl=20, show_spinner=False)
def get_payments():
    try:
        r = requests.get(WEB_APP_URL, params={"action": "get_payments"}, timeout=12)
        data = r.json() if r.ok else []
        return data if isinstance(data, list) else []
    except Exception:
        return []


@st.cache_data(ttl=20, show_spinner=False)
def get_recurring():
    try:
        r = requests.get(WEB_APP_URL, params={"action": "get_recurring"}, timeout=12)
        data = r.json() if r.ok else []
        return data if isinstance(data, list) else []
    except Exception:
        return []


def post_api(payload):
    try:
        r = requests.post(
            WEB_APP_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        data = r.json()
        return bool(data.get("success")), str(data.get("message", data.get("error", "Request failed")))
    except Exception as exc:
        return False, str(exc)

# ============================================================
# CSS / HEADER
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&display=swap');
.stApp{background:linear-gradient(135deg,#05080f,#0b1220 52%,#07111b);color:#f8fafc;font-family:Inter,sans-serif}
.block-container{max-width:1450px;padding-top:.55rem;padding-bottom:2.5rem}
.nc-header{position:relative;text-align:center;padding:7px 10px 8px;min-height:76px}
.nc-logo{height:48px;width:48px;object-fit:contain;vertical-align:middle;margin-right:9px;border-radius:8px}
.nc-title{font-family:Orbitron,Arial,sans-serif;font-size:32px;line-height:1.15;font-weight:800;letter-spacing:2.2px;color:#22d3ee;text-shadow:0 0 14px rgba(34,211,238,.28);white-space:nowrap}
.nc-main-title{font-size:18px;font-weight:800;letter-spacing:1.5px;color:#fff;margin-top:4px}
.nc-sub{font-size:9px;letter-spacing:1.8px;color:#94a3b8;margin-top:3px}
.income-box{margin:2px auto 10px;max-width:900px;background:rgba(15,23,42,.72);border:1px solid rgba(34,211,238,.22);border-radius:9px;padding:5px 10px;text-align:center;font-size:11px;line-height:1.5}
.profit{color:#22c55e;font-weight:800}.cash{color:#22c55e;font-weight:800}.credit{color:#ef4444;font-weight:800}
.nc-section{font-family:Orbitron,sans-serif;font-size:17px;font-weight:700;color:#e2e8f0;margin:7px 0 10px}
.nc-table-wrap{border:1px solid rgba(96,165,250,.16);border-radius:8px;overflow:hidden}
.nc-table-head{background:#111827;border-bottom:1px solid rgba(34,211,238,.28);color:#94a3b8;font-size:9px;font-weight:800;letter-spacing:.3px;padding:5px 4px;min-height:28px;display:flex;align-items:center;white-space:nowrap;overflow:hidden}
.nc-table-row{background:rgba(15,23,42,.70);border-bottom:1px solid rgba(148,163,184,.10);color:#e2e8f0;font-size:10px;font-weight:600;padding:5px 4px;min-height:30px;display:flex;align-items:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nc-table-row:hover{background:rgba(30,41,59,.88)}
.table-green{color:#22c55e!important;font-weight:800!important}.table-red{color:#ef4444!important;font-weight:800!important}
.nc-red-text{color:#ef4444!important;font-weight:700}.nc-green-text{color:#22c55e!important;font-weight:700}
.nc-mini{font-size:10px;color:#94a3b8}.stButton>button{border-radius:7px;font-weight:700}
div[data-testid="stMetric"]{background:transparent;border:0;padding:2px 4px}
div[data-testid="stMetricLabel"]{font-size:10px}div[data-testid="stMetricValue"]{font-size:22px}
</style>
""",
    unsafe_allow_html=True,
)

# Stable header: rendered exactly once.
if os.path.exists(LOGO_PATH):
    st.markdown(
        f"<div class='nc-header'><div class='nc-title'><img class='nc-logo' src='data:image/png;base64,{__import__('base64').b64encode(open(LOGO_PATH,'rb').read()).decode()}'/>NOOR CYBER WORLD</div><div class='nc-main-title'>CUSTOMER MANAGEMENT SYSTEM</div><div class='nc-sub'>DIGITAL SERVICE • CUSTOMER RECORD • SMART MANAGEMENT</div></div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<div class='nc-header'><div class='nc-title'>NOOR CYBER WORLD</div><div class='nc-main-title'>CUSTOMER MANAGEMENT SYSTEM</div><div class='nc-sub'>DIGITAL SERVICE • CUSTOMER RECORD • SMART MANAGEMENT</div></div>",
        unsafe_allow_html=True,
    )

# ============================================================
# LOAD DATA ONCE PER RERUN
# ============================================================

server_services = get_services()
for s in server_services:
    if s not in st.session_state.custom_services and s not in BASE_SERVICES:
        st.session_state.custom_services.append(s)

df = clean_df(get_records())
expenses = get_expenses()
payments = get_payments()
recurring = get_recurring()

# Latest first everywhere.
if not df.empty:
    df = df.sort_values(["created_at", "_row_number"], ascending=[False, False], kind="stable").reset_index(drop=True)

selected_date = st.session_state.selected_date
selected_date_str = selected_date.strftime("%Y-%m-%d")

day_df = df[df["created_at"].str[:10] == selected_date_str].copy() if not df.empty else empty_df()

# ============================================================
# TOP INCOME SUMMARY
# ============================================================

today_s = today_ist().strftime("%Y-%m-%d")
month_s = today_ist().strftime("%Y-%m")
year_s = today_ist().strftime("%Y")

today_net = float(df.loc[df["created_at"].str[:10] == today_s, "net_amount"].sum()) if not df.empty else 0
today_cash = float(df.loc[df["created_at"].str[:10] == today_s, "cash"].sum()) if not df.empty else 0
month_net = float(df.loc[df["created_at"].str[:7] == month_s, "net_amount"].sum()) if not df.empty else 0
year_net = float(df.loc[df["created_at"].str[:4] == year_s, "net_amount"].sum()) if not df.empty else 0

st.markdown(
    f"<div class='income-box'><b>📅 TODAY NET:</b> <span class='profit'>₹ {today_net:,.0f}</span> &nbsp;|&nbsp; <b>🗓️ MONTH NET:</b> <span class='profit'>₹ {month_net:,.0f}</span> &nbsp;|&nbsp; <b>📊 YEAR NET:</b> <span class='profit'>₹ {year_net:,.0f}</span></div>",
    unsafe_allow_html=True,
)

# ============================================================
# DATE NAVIGATION
# ============================================================

p, d, n = st.columns([1, 4, 1])
with p:
    if st.button("❮ PREVIOUS DAY", use_container_width=True):
        st.session_state.selected_date -= timedelta(days=1)
        st.rerun()
with d:
    picked = st.date_input("Working Date", value=selected_date, label_visibility="collapsed")
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
    "📊 TODAY'S ENTRIES",
    "🔴 CREDIT COLLECTION",
    "🔔 RENEWAL ALERTS",
    "💸 SHOP EXPENSES",
    "📂 RECORDS & SEARCH",
])

# ============================================================
# COMMON TABLE
# ============================================================

def render_table(data, key_prefix="tbl", credit_mode=False):
    if data.empty:
        st.info("No records found.")
        return
    headers = ["DATE", "CUSTOMER", "MOBILE", "SERVICE", "AMOUNT", "NET", "CASH", "CREDIT", "EXPIRY", "EDIT", "DELETE"]
    widths = [0.86,1.05,1.15,2.0,0.72,0.72,0.72,0.72,0.82,0.38,0.45]
    hcols = st.columns(widths)
    for i, h in enumerate(headers):
        with hcols[i]:
            st.markdown(f"<div class='nc-table-head'>{h}</div>", unsafe_allow_html=True)

    for _, row in data.iterrows():
        rn = int(row["_row_number"])
        cols = st.columns(widths)
        vals = [
            str(row["created_at"]), str(row["name"]), str(row["mobile"]), str(row["service"]),
            f"₹ {float(row['amount']):,.0f}", f"₹ {float(row['net_amount']):,.0f}",
            f"₹ {float(row['cash']):,.0f}", f"₹ {float(row['credit']):,.0f}", str(row["expiry"])
        ]
        for i, val in enumerate(vals):
            cls = "nc-table-row"
            if i in (5, 6): cls += " table-green"
            if i == 7: cls += " table-red"
            with cols[i]:
                st.markdown(f"<div class='{cls}' title='{val}'>{val}</div>", unsafe_allow_html=True)
        with cols[9]:
            if st.button("✏️", key=f"{key_prefix}_edit_{rn}", help="Edit"):
                st.session_state.editing_row = row.to_dict()
                st.rerun()
        with cols[10]:
            if st.button("🗑️", key=f"{key_prefix}_del_{rn}", help="Delete"):
                st.session_state.confirm_delete = rn
                st.rerun()

# ============================================================
# TAB 1 - TODAY + ADD ENTRY
# ============================================================

with tab1:
    st.markdown(f"<div class='nc-section'>📋 ENTRIES FOR {selected_date.strftime('%d-%m-%Y')}</div>", unsafe_allow_html=True)

    total_gross = int(day_df["amount"].sum()) if not day_df.empty else 0
    total_net = int(day_df["net_amount"].sum()) if not day_df.empty else 0
    cash_sum = int(sum(float(x.get("amount",0)) for x in payments if str(x.get("payment_date",""))[:10] == selected_date_str))
    credit_sum = int(day_df["credit"].sum()) if not day_df.empty else 0
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("TOTAL COLLECTION", f"₹ {total_gross:,}")
    m2.metric("CASH RECEIVED", f"₹ {cash_sum:,}")
    m3.metric("PENDING CREDIT", f"₹ {credit_sum:,}")
    m4.metric("NET PROFIT", f"₹ {total_net:,}")

    st.markdown("<div class='nc-table-wrap'>", unsafe_allow_html=True)
    render_table(day_df, "day")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='nc-section'>➕ ADD NEW CUSTOMER ENTRY</div>", unsafe_allow_html=True)

    # Recall happens only when the user presses RECALL, not on every mobile keystroke.
    r1, r2 = st.columns([4,1])
    with r1:
        recall_mobile = st.text_input("Mobile Number *", value=st.session_state.mobile_recall, key="mobile_recall_input")
    with r2:
        st.write("")
        if st.button("🔎 RECALL", use_container_width=True):
            mobile_clean = recall_mobile.strip()
            st.session_state.mobile_recall = mobile_clean
            found = df[df["mobile"].astype(str).str.strip() == mobile_clean] if mobile_clean and not df.empty else empty_df()
            st.session_state.recalled_name = str(found.iloc[0]["name"]) if not found.empty else ""
            st.rerun()

    if st.session_state.recalled_name:
        st.markdown(f"<div class='nc-green-text'>✓ Existing Customer: {st.session_state.recalled_name}</div>", unsafe_allow_html=True)

  

    with st.form("entry_form", clear_on_submit=False):
        name = st.text_input("Customer Name *", value=st.session_state.recalled_name, key="entry_name")
        service_names = []
        service_amounts = []
        svcs = service_list()
        for i in range(st.session_state.service_count):
            a,b = st.columns([3,1])
            with a:
                default = st.session_state.service_values[i] if i < len(st.session_state.service_values) else svcs[0]
                idx = svcs.index(default) if default in svcs else 0
                s = st.selectbox(f"Service {i+1}", svcs, index=idx, key=f"svc_{i}")
                custom = ""
                if s == "Other":
                    custom = st.text_input(f"Other Service {i+1}", key=f"other_{i}")
                    s = custom.strip()
                service_names.append(s)
            with b:
                service_amounts.append(st.number_input(f"Amount {i+1} (₹)", min_value=0, step=10, key=f"svc_amt_{i}"))
  # Add-service rows. The button changes row count; actual saving is one operation.
    c_add, c_hint = st.columns([1,4])
    with c_add:
        if st.button("➕ ADD SERVICE", use_container_width=True):
            st.session_state.service_count += 1
            st.session_state.service_values.append(BASE_SERVICES[0])
            st.session_state.service_amounts.append(0)
            st.rerun()
    with c_hint:
        st.caption("One customer can have multiple services. They will be stored together with commas and one total amount.")
        amount = int(sum(service_amounts))
        st.markdown(f"**TOTAL SERVICE AMOUNT: ₹ {amount:,}**")
        net_amount = st.number_input("Net Income / Profit (₹) *", min_value=0, step=10, key="entry_net")
        payment = st.radio("Payment Type *", ["💵 CASH", "🔴 CREDIT (UDHARI)"], horizontal=True, key="entry_payment")
        has_expiry = st.checkbox("Requires Renewal / Validity?", key="entry_expiry_check")
        unit = st.selectbox("Validity Unit", ["Days","Months","Years"], index=1, key="entry_validity_unit")
        duration = st.number_input("Validity Duration", min_value=1, value=1, step=1, key="entry_validity_duration")
        save_entry = st.form_submit_button("⚡ SAVE ENTRY", type="primary", use_container_width=True)

    if save_entry:
        mobile = recall_mobile.strip()
        name = name.strip()
        final_services = [x.strip() for x in service_names if x and x.strip()]
        if not mobile or not name or not final_services:
            st.error("Customer name, mobile and at least one service are required.")
        elif net_amount > amount:
            st.error("Net Profit cannot be greater than Total Fee.")
        elif any(x == "Other" for x in final_services):
            st.error("Please enter the custom service name.")
        elif amount <= 0:
            st.error("Total service amount must be greater than zero.")
        else:
            final_service = ", ".join(final_services)
            expiry = "N/A"
            if has_expiry:
                if unit == "Days": exp = selected_date + timedelta(days=int(duration))
                elif unit == "Months": exp = selected_date + relativedelta(months=int(duration))
                else: exp = selected_date + relativedelta(years=int(duration))
                expiry = exp.strftime("%Y-%m-%d")
            is_credit = "CREDIT" in payment
            ok, msg = post_api({
                "action":"add",
                "created_at":selected_date_str,
                "name":name,
                "mobile":mobile,
                "service":final_service,
                "amount":str(amount),
                "net_amount":str(int(net_amount)),
                "cash":str(0 if is_credit else amount),
                "credit":str(amount if is_credit else 0),
                "expiry":expiry,
            })
            if ok:
                for svc in final_services:
                    if svc not in BASE_SERVICES and svc not in st.session_state.custom_services:
                        post_api({"action":"add_service","service":svc})
                        st.session_state.custom_services.append(svc)
                invalidate_data()
                st.session_state.last_saved_wa = "https://wa.me/91" + mobile + "?text=" + quote(f"Dear {name}, Thank you for choosing NOOR CYBER WORLD for {final_service}! Total Amount: Rs.{amount}.")
                st.session_state.success_message = "Entry saved successfully."
                st.rerun()
            else:
                st.error(msg)

# ============================================================
# TAB 2 - CREDIT COLLECTION
# ============================================================

with tab2:
    st.markdown("<div class='nc-section'>🔴 CREDIT COLLECTION</div>", unsafe_allow_html=True)
    credit_df = df[df["credit"] > 0].copy() if not df.empty else empty_df()
    if credit_df.empty:
        st.success("🎉 No pending credit! All payments are clear.")
    else:
        st.markdown(f"<div class='nc-red-text'>TOTAL PENDING CREDIT: ₹ {int(credit_df['credit'].sum()):,}</div>", unsafe_allow_html=True)
        headers = ["DATE","CUSTOMER","MOBILE","SERVICE","AMOUNT","NET","CASH","CREDIT","EXPIRY","REMINDER","COLLECT"]
        widths = [0.86,1.05,1.15,2.0,0.72,0.72,0.72,0.72,0.82,0.9,0.9]
        hc = st.columns(widths)
        for i,h in enumerate(headers):
            with hc[i]: st.markdown(f"<div class='nc-table-head'>{h}</div>", unsafe_allow_html=True)
        for _,row in credit_df.iterrows():
            rn=int(row["_row_number"]); cols=st.columns(widths)
            vals=[str(row["created_at"]),str(row["name"]),str(row["mobile"]),str(row["service"]),f"₹ {float(row['amount']):,.0f}",f"₹ {float(row['net_amount']):,.0f}",f"₹ {float(row['cash']):,.0f}",f"₹ {float(row['credit']):,.0f}",str(row["expiry"])]
            for i,val in enumerate(vals):
                cls="nc-table-row" + (" table-green" if i==5 else " table-red" if i==7 else "")
                with cols[i]: st.markdown(f"<div class='{cls}' title='{val}'>{val}</div>", unsafe_allow_html=True)
            with cols[9]:
                msg=quote(f"Hello {row['name']}, your pending payment is Rs.{int(row['credit'])} for {row['service']}. Please clear your balance. Thank you! - NOOR CYBER WORLD")
                st.link_button("💬 REMIND", f"https://wa.me/91{str(row['mobile']).strip()}?text={msg}", use_container_width=True)
            with cols[10]:
                if st.button("💵 COLLECT", key=f"collect_{rn}", use_container_width=True):
                    ok,msg=post_api({"action":"credit_to_cash","row_number":rn})
                    if ok:
                        invalidate_data(); st.session_state.success_message="Credit collected and moved to Cash."; st.rerun()
                    else: st.error(msg)

# ============================================================
# TAB 3 - RENEWALS
# ============================================================

with tab3:
    alerts=[]; today=today_ist()
    for _,row in df.iterrows():
        exp=str(row["expiry"]).strip()
        if not exp or exp=="N/A": continue
        try:
            ed=datetime.strptime(exp[:10],"%Y-%m-%d").date(); left=(ed-today).days
            if 0 <= left <= 15: alerts.append((row,ed,left))
        except Exception: pass
    count=len(alerts)
    st.markdown(f"<div class='nc-section'>🔔 RENEWAL ALERTS <span class='nc-red-text'>({count})</span></div>", unsafe_allow_html=True)
    if not alerts:
        st.success("🎉 No renewals due in the next 15 days.")
    else:
        for row,ed,left in alerts:
            color="red" if left <= 3 else "green"
            cls="nc-red-text" if color=="red" else "nc-green-text"
            st.markdown(f"<div class='{cls}'>🔔 {row['name']} • {row['mobile']} • {row['service']} • Expiry: {ed.strftime('%d-%m-%Y')} • {left} day(s) left</div>", unsafe_allow_html=True)
            msg=quote(f"Hello {row['name']}, your service {row['service']} expires on {ed.strftime('%d-%m-%Y')}. Please visit NOOR CYBER WORLD to renew it.")
            st.link_button("💬 SEND WHATSAPP", f"https://wa.me/91{str(row['mobile']).strip()}?text={msg}")

# ============================================================
# TAB 4 - EXPENSES
# ============================================================

with tab4:
    st.markdown("<div class='nc-section'>💸 SHOP EXPENSES & REAL PROFIT</div>", unsafe_allow_html=True)
    exp1,exp2,exp3=st.columns([2,1,1])
    with exp1: exp_title=st.text_input("Expense Title", key="exp_title")
    with exp2: exp_amount=st.number_input("Expense Amount (₹)", min_value=0, step=10, key="exp_amount")
    with exp3:
        st.write("")
        add_exp=st.button("💾 ADD EXPENSE", type="primary", use_container_width=True)
    if add_exp:
        if not exp_title.strip() or exp_amount <= 0: st.error("Enter valid expense title and amount.")
        else:
            ok,msg=post_api({"action":"add_expense","created_at":selected_date_str,"title":exp_title.strip(),"amount":str(int(exp_amount))})
            if ok: invalidate_data(); st.session_state.success_message="Expense saved."; st.rerun()
            else: st.error(msg)
    selected_expenses=[x for x in expenses if str(x.get("created_at",""))[:10]==selected_date_str]
    total_exp=sum(float(x.get("amount",0)) for x in selected_expenses)
    actual_saving=total_net-total_exp
    st.markdown(f"<div class='nc-mini'>NET PROFIT: <span class='profit'>₹ {total_net:,}</span> &nbsp; | &nbsp; EXPENSES: <span class='nc-red-text'>₹ {total_exp:,.0f}</span> &nbsp; | &nbsp; ACTUAL SAVINGS: <span class='profit'>₹ {actual_saving:,.0f}</span></div>", unsafe_allow_html=True)
    if selected_expenses:
        headers=["DATE","EXPENSE TITLE","AMOUNT","DELETE"]; widths=[1,5,1.3,.6]; hc=st.columns(widths)
        for i,h in enumerate(headers):
            with hc[i]: st.markdown(f"<div class='nc-table-head'>{h}</div>",unsafe_allow_html=True)
        for exp in sorted(selected_expenses,key=lambda x:int(x.get("_row_number",0)),reverse=True):
            rn=int(exp.get("_row_number",0)); cols=st.columns(widths)
            with cols[0]: st.markdown(f"<div class='nc-table-row'>{exp.get('created_at','')}</div>",unsafe_allow_html=True)
            with cols[1]: st.markdown(f"<div class='nc-table-row nc-red-text'>{exp.get('title','')}</div>",unsafe_allow_html=True)
            with cols[2]: st.markdown(f"<div class='nc-table-row nc-red-text'>₹ {float(exp.get('amount',0)):,.0f}</div>",unsafe_allow_html=True)
            with cols[3]:
                if st.button("🗑️",key=f"expdel_{rn}"):
                    ok,msg=post_api({"action":"delete_expense","row_number":rn})
                    if ok: invalidate_data(); st.rerun()
                    else: st.error(msg)
    else: st.info("No expenses recorded for this date.")

# ============================================================
# TAB 5 - RECORDS
# ============================================================

with tab5:
    st.markdown("<div class='nc-section'>📂 CUSTOMER RECORDS & SEARCH</div>", unsafe_allow_html=True)
    q=st.text_input("🔍 Search Name / Mobile / Service",key="search_records").strip().lower()
    filtered=df.copy()
    if q:
        filtered=filtered[filtered["name"].str.lower().str.contains(q,na=False)|filtered["mobile"].str.lower().str.contains(q,na=False)|filtered["service"].str.lower().str.contains(q,na=False)]
    b1,b2=st.columns(2)
    with b1:
        export=filtered.drop(columns=["_row_number"],errors="ignore")
        st.download_button("📥 DOWNLOAD CSV",export.to_csv(index=False).encode("utf-8-sig"),"NOOR_CYBER_WORLD_RECORDS.csv","text/csv",use_container_width=True)
    with b2:
        buffer=io.BytesIO(); doc=SimpleDocTemplate(buffer,pagesize=letter,rightMargin=20,leftMargin=20,topMargin=20,bottomMargin=20)
        styles=getSampleStyleSheet(); elements=[Paragraph("NOOR CYBER WORLD - CUSTOMER RECORDS",ParagraphStyle("title",parent=styles["Heading1"],alignment=1,fontSize=16)),Spacer(1,10)]
        rows=[["Date","Name","Mobile","Service","Gross","Net","Cash","Credit","Expiry"]]
        for _,r in export.iterrows(): rows.append([str(r["created_at"]),str(r["name"]),str(r["mobile"]),str(r["service"]),f"Rs. {float(r['amount']):.0f}",f"Rs. {float(r['net_amount']):.0f}",f"Rs. {float(r['cash']):.0f}",f"Rs. {float(r['credit']):.0f}",str(r["expiry"])])
        tbl=Table(rows,repeatRows=1); tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0f172a")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.4,colors.grey),("FONTSIZE",(0,0),(-1,-1),7),("ALIGN",(0,0),(-1,-1),"CENTER")]))
        elements.append(tbl); doc.build(elements); buffer.seek(0)
        st.download_button("📄 DOWNLOAD PDF",buffer.getvalue(),"NOOR_CYBER_WORLD_RECORDS.pdf","application/pdf",use_container_width=True)
    st.caption(f"Showing {len(filtered)} records • Latest entry first")
    st.markdown("<div class='nc-table-wrap'>",unsafe_allow_html=True); render_table(filtered,"rec"); st.markdown("</div>",unsafe_allow_html=True)

# ============================================================
# AUTO DAILY ENTRY MANAGEMENT - SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🔁 AUTO DAILY ENTRY")
    st.caption("A configured entry is added automatically once per day until you stop it.")
    active_recurring=[x for x in recurring if str(x.get("active","TRUE")).upper()=="TRUE"]
    st.write(f"Active rules: **{len(active_recurring)}**")
    with st.expander("➕ Create Daily Rule"):
        r_name=st.text_input("Customer Name",key="r_name")
        r_mobile=st.text_input("Mobile",key="r_mobile")
        r_service=st.selectbox("Service",service_list(),key="r_service")
        r_amount=st.number_input("Daily Amount (₹)",min_value=0,step=10,key="r_amount")
        r_net=st.number_input("Daily Net Profit (₹)",min_value=0,step=10,key="r_net")
        r_payment=st.radio("Payment",["CASH","CREDIT"],horizontal=True,key="r_payment")
        if st.button("SAVE AUTO RULE",use_container_width=True):
            if not r_name.strip() or not r_mobile.strip() or r_amount<=0 or r_net>r_amount: st.error("Fill valid customer, amount and profit.")
            else:
                ok,msg=post_api({"action":"add_recurring","name":r_name.strip(),"mobile":r_mobile.strip(),"service":r_service,"amount":str(int(r_amount)),"net_amount":str(int(r_net)),"payment":r_payment,"active":"TRUE","start_date":today_s})
                if ok: invalidate_data(); st.success("Auto daily rule saved."); st.rerun()
                else: st.error(msg)
    if recurring:
        for rr in recurring:
            rid=int(rr.get("_row_number",0)); active=str(rr.get("active","TRUE")).upper()=="TRUE"
            label=f"{'🟢' if active else '⚪'} {rr.get('name','')} • ₹{float(rr.get('amount',0)):,.0f} • {rr.get('payment','CASH')}"
            st.write(label)
            if active:
                if st.button("STOP",key=f"stop_rec_{rid}",use_container_width=True):
                    ok,msg=post_api({"action":"toggle_recurring","row_number":rid,"active":"FALSE"})
                    if ok: invalidate_data(); st.rerun()
                    else: st.error(msg)
            else:
                if st.button("START",key=f"start_rec_{rid}",use_container_width=True):
                    ok,msg=post_api({"action":"toggle_recurring","row_number":rid,"active":"TRUE"})
                    if ok: invalidate_data(); st.rerun()
                    else: st.error(msg)

# ============================================================
# GLOBAL EDIT / DELETE CONFIRMATION
# ============================================================

@st.dialog("✏️ EDIT CUSTOMER ENTRY")
def edit_dialog(row):
    rn=int(row["_row_number"])
    mobile=st.text_input("Mobile Number *",value=str(row.get("mobile","")),key=f"ed_m_{rn}")
    name=st.text_input("Customer Name *",value=str(row.get("name","")),key=f"ed_n_{rn}")
    service=st.text_input("Services (comma separated) *",value=str(row.get("service","")),key=f"ed_s_{rn}")
    amount=st.number_input("Total Fee / Gross Amount (₹)",min_value=0,step=10,value=int(float(row.get("amount",0))),key=f"ed_a_{rn}")
    net=st.number_input("Net Profit (₹)",min_value=0,step=10,value=int(float(row.get("net_amount",0))),key=f"ed_net_{rn}")
    payment=st.radio("Payment Type",["CASH","CREDIT"],index=1 if float(row.get("credit",0))>0 else 0,horizontal=True,key=f"ed_p_{rn}")
    if net>amount: st.error("Net Profit cannot be greater than Total Fee."); return
    if st.button("✅ YES, SAVE CHANGES",type="primary",use_container_width=True,key=f"ed_save_{rn}"):
        ok,msg=post_api({"action":"edit","row_number":rn,"created_at":str(row.get("created_at",""))[:10],"name":name.strip(),"mobile":mobile.strip(),"service":service.strip(),"amount":str(int(amount)),"net_amount":str(int(net)),"cash":str(int(amount) if payment=="CASH" else 0),"credit":str(int(amount) if payment=="CREDIT" else 0),"expiry":str(row.get("expiry","N/A"))})
        if ok: invalidate_data(); st.session_state.editing_row=None; st.session_state.success_message="Entry updated successfully."; st.rerun()
        else: st.error(msg)
    if st.button("❌ NO, CANCEL",use_container_width=True,key=f"ed_cancel_{rn}"):
        st.session_state.editing_row=None; st.rerun()

if st.session_state.editing_row is not None:
    edit_dialog(st.session_state.editing_row)

if st.session_state.confirm_delete:
    rn=int(st.session_state.confirm_delete)
    st.warning(f"Delete customer entry #{rn}?")
    y,n=st.columns(2)
    with y:
        if st.button("✅ YES, DELETE",type="primary",use_container_width=True,key="confirm_del_yes"):
            ok,msg=post_api({"action":"delete","row_number":rn})
            if ok: st.session_state.confirm_delete=None; invalidate_data(); st.session_state.success_message="Entry deleted."; st.rerun()
            else: st.error(msg)
    with n:
        if st.button("❌ NO, KEEP",use_container_width=True,key="confirm_del_no"):
            st.session_state.confirm_delete=None; st.rerun()

if st.session_state.last_saved_wa:
    st.link_button("💬 SEND THANK YOU WHATSAPP",st.session_state.last_saved_wa,use_container_width=True)
    if st.button("Close WhatsApp button",key="close_wa"):
        st.session_state.last_saved_wa=None; st.rerun()

if st.session_state.success_message:
    st.toast(st.session_state.success_message,icon="✅")
    st.session_state.success_message=None
