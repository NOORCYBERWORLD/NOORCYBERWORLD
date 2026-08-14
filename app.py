import streamlit as st
import pandas as pd
import requests
import json
import io
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import quote

# Reportlab for PDF Generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Page Configuration
st.set_page_config(page_title="NOOR CYBER WORLD", layout="wide")

# ============================================================
# TIMEZONE & COLUMNS
# ============================================================
IST = timezone(timedelta(hours=5, minutes=30))

COLUMNS = [
    "created_at",
    "name",
    "mobile",
    "service",
    "amount",
    "net_amount",
    "payment",
    "expiry",
    "_row_number"
]

DEFAULT_SERVICES = [
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
    "Xerox / Color Printout / Lamination / Scanning"
]

DEFAULT_SERVICES = sorted(DEFAULT_SERVICES, key=lambda x: x.lower()) + ["Other"]

if "custom_services" not in st.session_state:
    st.session_state.custom_services = []

if "expenses" not in st.session_state:
    st.session_state.expenses = []

def get_all_services():
    services = DEFAULT_SERVICES[:-1] + st.session_state.custom_services
    services = sorted(set(s.strip() for s in services if s and s.strip()), key=lambda x: x.lower())
    services.append("Other")
    return services

SERVICES = get_all_services()

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now(IST).date()

if "editing_row" not in st.session_state:
    st.session_state.editing_row = None

# ============================================================
# HEADER & CUSTOM CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&display=swap');

:root {
    --red:#ef4444;
    --green:#22c55e;
    --cyan:#22d3ee;
    --border:rgba(96,165,250,.22);
}

.stApp {
    background: linear-gradient(115deg, rgba(5,8,15,.96), rgba(7,18,32,.84)),
        url("https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=2400&q=80")
        center/cover fixed no-repeat;
    color:#f8fafc;
    font-family:'Inter',sans-serif;
}

.block-container {
    max-width:1450px;
    padding-top:1.2rem;
    padding-bottom:3rem;
}

.nc-header {
    text-align: center;
    padding: 10px 10px 15px;
    margin-bottom: 10px;
}
.nc-title {
    font-family: Arial, sans-serif;
    font-size: 32px;
    font-weight: 800;
    letter-spacing: 3px;
    color: white;
    margin-bottom: 2px;
}
.nc-main-title {
    font-family: Arial, sans-serif;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #22d3ee;
    margin-bottom: 5px;
}
.nc-sub {
    font-size: 11px;
    letter-spacing: 1.5px;
    color: #cbd5e1;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(15,23,42,.92), rgba(30,41,59,.72));
    border:1px solid var(--border);
    border-radius:18px;
    padding:18px;
    box-shadow: 0 12px 35px rgba(0,0,0,.22);
}

div[data-testid="stMetricLabel"] { color:#cbd5e1; }
div[data-testid="stMetricValue"] { font-weight:800; }

.nc-card-green {
    background: linear-gradient(145deg, rgba(22, 101, 52, 0.35), rgba(15, 23, 42, 0.85));
    border: 1px solid rgba(34, 197, 94, 0.5);
    border-left: 6px solid #22c55e;
    border-radius: 14px;
    padding: 14px;
    margin: 8px 0;
}

.nc-card-red {
    background: linear-gradient(145deg, rgba(153, 27, 27, 0.35), rgba(15, 23, 42, 0.85));
    border: 1px solid rgba(239, 68, 68, 0.5);
    border-left: 6px solid #ef4444;
    border-radius: 14px;
    padding: 14px;
    margin: 8px 0;
}

.nc-section {
    font-family: 'Orbitron',sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #e2e8f0;
    margin: 8px 0 14px;
}

.top-corner-stats {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(34, 211, 238, 0.3);
    border-radius: 12px;
    padding: 12px 18px;
    text-align: right;
    font-size: 13px;
    color: #cbd5e1;
    line-height: 1.6;
}

.top-corner-stats span.gross { color: #22d3ee; font-weight: 700; }
.top-corner-stats span.net { color: #22c55e; font-weight: 700; }

.alert-badge {
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid #ef4444;
    color: #fca5a5;
    padding: 10px 16px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 16px;
    margin-bottom: 15px;
    display: inline-block;
}
</style>

<div class="nc-header">
    <div class="nc-title">NOOR CYBER WORLD</div>
    <div class="nc-main-title">CUSTOMERS MANAGEMENT SYSTEM</div>
    <div class="nc-sub">DIGITAL SERVICE • CUSTOMER RECORD • SMART MANAGEMENT</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# GOOGLE APPS SCRIPT URL
# ============================================================
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbytGWMPZpnOWm6v2ibp7_nn0ZuvFb8VwWNpqBenI_gcuq_tH3w9RsYiF1zGLzfCDDgg/exec"

# ============================================================
# HELPER FUNCTIONS & API
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
            df[col] = ""

    for col in ["name", "mobile", "service", "payment", "expiry"]:
        df[col] = df[col].fillna("").astype(str)

    raw = df["created_at"].fillna("").astype(str)
    parsed = pd.to_datetime(raw, errors="coerce")
    df["created_at"] = parsed.dt.strftime("%Y-%m-%d")
    df.loc[parsed.isna(), "created_at"] = raw[parsed.isna()]

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["net_amount"] = pd.to_numeric(df["net_amount"], errors="coerce").fillna(0)
    return df[COLUMNS]

@st.cache_data(ttl=5)
def fetch_sheet_records():
    try:
        response = requests.get(
            WEB_APP_URL,
            params={"t": int(datetime.now().timestamp())},
            timeout=20
        )
        if response.status_code != 200:
            return empty_df()

        data = response.json()
        if not isinstance(data, list):
            return empty_df()

        df = pd.DataFrame(data)
        if df.empty:
            return empty_df()

        return clean_df(df)
    except Exception:
        return empty_df()

def api_post(payload):
    try:
        response = requests.post(
            WEB_APP_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        try:
            data = response.json()
            return (bool(data.get("success")), str(data.get("message", data.get("error", "Failed"))))
        except Exception:
            return (True, "Success")
    except Exception as e:
        return (False, str(e))

def generate_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=15
    )
    
    elements.append(Paragraph("NOOR CYBER WORLD - CUSTOMER RECORDS", title_style))
    elements.append(Spacer(1, 10))

    headers = ["Date", "Name", "Mobile", "Service", "Gross", "Net Income", "Payment", "Expiry"]
    table_data = [headers]

    for _, row in df.iterrows():
        table_data.append([
            str(row["created_at"]),
            str(row["name"]),
            str(row["mobile"]),
            str(row["service"]),
            f"Rs. {row['amount']}",
            f"Rs. {row['net_amount']}",
            str(row["payment"]),
            str(row["expiry"])
        ])

    t = Table(table_data, colWidths=[55, 90, 75, 120, 50, 55, 50, 55])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
    ]))
    
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Fetch Data Live
df_all = fetch_sheet_records()

# Unique Customer Names & Mobile mapping
existing_names = sorted(list(set(df_all["name"].dropna().str.strip()))) if not df_all.empty else []
name_to_mobile_map = {}
if not df_all.empty:
    for _, r in df_all.iterrows():
        nm = str(r["name"]).strip()
        mb = str(r["mobile"]).strip()
        if nm and mb:
            name_to_mobile_map[nm] = mb

# Top Header Stats Display
now_ist = datetime.now(IST)
current_date_str = now_ist.strftime("%Y-%m-%d")
current_month_str = now_ist.strftime("%Y-%m")
current_year_str = now_ist.strftime("%Y")

if not df_all.empty:
    created_dates = pd.to_datetime(df_all["created_at"], errors="coerce")
    
    day_mask = created_dates.dt.strftime("%Y-%m-%d") == current_date_str
    month_mask = created_dates.dt.strftime("%Y-%m") == current_month_str
    year_mask = created_dates.dt.strftime("%Y") == current_year_str

    day_gross = df_all[day_mask]["amount"].sum()
    day_net = df_all[day_mask]["net_amount"].sum()

    month_gross = df_all[month_mask]["amount"].sum()
    month_net = df_all[month_mask]["net_amount"].sum()

    year_gross = df_all[year_mask]["amount"].sum()
    year_net = df_all[year_mask]["net_amount"].sum()
else:
    day_gross = day_net = month_gross = month_net = year_gross = year_net = 0

st.markdown(
    f"""
    <div class="top-corner-stats">
        📅 <b>Today:</b> Total <span class="gross">₹ {day_gross:,.0f}</span> | Net Profit <span class="net">₹ {day_net:,.0f}</span><br>
        🗓️ <b>Month:</b> Total <span class="gross">₹ {month_gross:,.0f}</span> | Net Profit <span class="net">₹ {month_net:,.0f}</span><br>
        📊 <b>Year:</b> Total <span class="gross">₹ {year_gross:,.0f}</span> | Net Profit <span class="net">₹ {year_net:,.0f}</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Date Selector
selected_date_str = st.session_state.selected_date.strftime("%Y-%m-%d")

if not df_all.empty:
    date_mask = pd.to_datetime(df_all["created_at"], errors="coerce").dt.strftime("%Y-%m-%d") == selected_date_str
    day_df = df_all[date_mask].copy()
else:
    day_df = empty_df()

p_col, d_col, n_col = st.columns([1, 4, 1])

with p_col:
    if st.button("❮ PREVIOUS DAY", use_container_width=True):
        st.session_state.selected_date -= timedelta(days=1)
        st.rerun()

with d_col:
    picked = st.date_input("📅 Working Date", value=st.session_state.selected_date, label_visibility="collapsed")
    if picked != st.session_state.selected_date:
        st.session_state.selected_date = picked
        st.rerun()

with n_col:
    if st.button("NEXT DAY ❯", use_container_width=True):
        st.session_state.selected_date += timedelta(days=1)
        st.rerun()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 TODAY'S ENTRIES & ADD ENTRY",
    "🔴 UDHARI COLLECTION",
    "🔔 RENEWAL ALERTS",
    "💸 SHOP EXPENSES & PROFIT",
    "📂 RECORDS & SEARCH"
])

# ============================================================
# TAB 1: TODAY'S ENTRIES & ADD / EDIT ENTRY
# ============================================================
with tab1:
    st.markdown(
        f"<div class='nc-section'>📋 Entries for {st.session_state.selected_date.strftime('%d-%m-%Y')}</div>",
        unsafe_allow_html=True
    )

    if not day_df.empty:
        total_gross = int(day_df["amount"].sum())
        total_net = int(day_df["net_amount"].sum())
        cash_sum = int(day_df.loc[day_df["payment"].str.strip().str.lower() == "cash", "amount"].sum())
        udhari_sum = int(day_df.loc[day_df["payment"].str.strip().str.lower() == "credit (udhari)", "amount"].sum())
    else:
        total_gross = total_net = cash_sum = udhari_sum = 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TOTAL COLLECTION", f"₹ {total_gross:,}")
    m2.metric("TOTAL NET PROFIT", f"₹ {total_net:,}")
    m3.metric("CASH RECEIVED", f"₹ {cash_sum:,}")
    m4.metric("PENDING UDHARI", f"₹ {udhari_sum:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    if day_df.empty:
        st.info("ℹ️ No entries recorded for this date yet.")
    else:
        for idx, row in day_df.iterrows():
            is_udhari = "udhari" in str(row['payment']).lower() or "credit" in str(row['payment']).lower()
            card_class = "nc-card-red" if is_udhari else "nc-card-green"
            badge = "🔴 UDHARI / CREDIT" if is_udhari else "🟢 CASH"

            c_info, c_btn1, c_btn2 = st.columns([6, 1, 1])
            with c_info:
                st.markdown(
                    f"""
                    <div class='{card_class}'>
                    <b>👤 {row['name']}</b> ({row['mobile']}) &nbsp;&nbsp;|&nbsp;&nbsp; <b>{badge}</b><br>
                    Service: <b>{row['service']}</b> | Total Fee: <b>₹ {float(row['amount']):,.0f}</b> | Net Profit: <b>₹ {float(row['net_amount']):,.0f}</b><br>
                    Expiry: {row['expiry']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c_btn1:
                if st.button("✏️ Edit", key=f"edit_{idx}", use_container_width=True):
                    st.session_state.editing_row = row.to_dict()
                    st.rerun()
            with c_btn2:
                if st.button("🗑️ Delete", key=f"del_{idx}", use_container_width=True):
                    with st.spinner("Deleting..."):
                        payload = {
                            "action": "delete",
                            "row_number": int(row["_row_number"])
                        }
                        ok, msg = api_post(payload)
                        if ok:
                            fetch_sheet_records.clear()
                            st.session_state.success_message = "Deleted successfully!"
                            st.rerun()
                        else:
                            st.error(f"Error: {msg}")

    st.markdown("---")
    
    # FORM: ADD OR EDIT
    is_editing = st.session_state.editing_row is not None
    form_title = "✏️ Edit Customer Entry" if is_editing else "➕ Add New Customer Entry"
    st.markdown(f"<div class='nc-section'>{form_title}</div>", unsafe_allow_html=True)

    edit_data = st.session_state.editing_row or {}

    left, right = st.columns(2)

    with left:
        if is_editing:
            name_input = st.text_input("Customer Name*", value=edit_data.get("name", ""), key="input_name_edit")
        else:
            name_input = st.selectbox(
                "Customer Name*",
                options=existing_names,
                index=None,
                placeholder="Type name (e.g. Nawaj) or select existing...",
                accept_new_options=True,
                key="input_name_select"
            )
            if name_input is None:
                name_input = ""

        auto_mobile = ""
        if name_input and name_input.strip() in name_to_mobile_map and not is_editing:
            auto_mobile = name_to_mobile_map[name_input.strip()]
            
        default_mobile = edit_data.get("mobile", "") if is_editing else auto_mobile
        mobile_input = st.text_input("Mobile Number*", value=default_mobile, key=f"input_mobile_{name_input}")
        
        curr_serv = edit_data.get("service", SERVICES[0])
        default_index = SERVICES.index(curr_serv) if curr_serv in SERVICES else SERVICES.index("Other")
        
        service_selected = st.selectbox("Search / Select Service*", SERVICES, index=default_index, key="input_service")

        if service_selected == "Other":
            custom_val = curr_serv if curr_serv not in SERVICES else ""
            custom_service_input = st.text_input("Custom Service Name*", value=custom_val, key="input_custom_service")
        else:
            custom_service_input = ""

    with right:
        amount = st.number_input("Total Fee / Gross Amount (₹)*", min_value=0, step=10, value=int(edit_data.get("amount", 0)), key="input_amount")
        net_amount = st.number_input("Net Income / Profit (₹)*", min_value=0, step=10, value=int(edit_data.get("net_amount", 0)), key="input_net_amount")
        
        pay_opts = ["Cash", "Credit (Udhari)"]
        curr_pay = edit_data.get("payment", "Cash")
        pay_idx = 1 if "udhari" in curr_pay.lower() or "credit" in curr_pay.lower() else 0
        payment = st.radio("Payment Status*", pay_opts, index=pay_idx, horizontal=True, key="input_payment")
        
        has_exp = str(edit_data.get("expiry", "N/A")).strip() not in ["N/A", ""]
        has_expiry = st.checkbox("Requires Renewal / Validity?", value=has_exp, key="input_expiry_check")
        validity_unit = st.selectbox("Validity Unit", ["Days", "Months", "Years"], index=1, key="input_validity_unit")
        validity_value = st.number_input("Validity Duration", min_value=1, value=1, key="input_validity_value")

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        submit_btn_label = "💾 UPDATE ENTRY" if is_editing else "⚡ SAVE ENTRY"
        if st.button(submit_btn_label, type="primary", use_container_width=True):
            if not str(name_input).strip() or not str(mobile_input).strip():
                st.error("Please enter Customer Name and Mobile Number.")
            else:
                final_service = service_selected
                if service_selected == "Other":
                    if not custom_service_input.strip():
                        st.error("Please enter the Custom Service Name.")
                        st.stop()
                    final_service = custom_service_input.strip()
                    if final_service not in st.session_state.custom_services:
                        st.session_state.custom_services.append(final_service)

                expiry = "N/A"
                if has_expiry:
                    base = st.session_state.selected_date
                    if validity_unit == "Days":
                        expiry_date = base + timedelta(days=int(validity_value))
                    elif validity_unit == "Months":
                        expiry_date = base + relativedelta(months=int(validity_value))
                    else:
               
