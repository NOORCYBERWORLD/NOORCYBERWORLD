import streamlit as st
import pandas as pd
import requests, json, io
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import quote
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ============================================================
# NOOR CYBER WORLD - FINAL APP.PY
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
    "created_at",
    "name",
    "mobile",
    "service",
    "amount",
    "net_amount",
    "cash",
    "credit",
    "expiry",
    "_row_number"
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
    "Xerox / Color Printout / Lamination / Scanning"
], key=str.lower)

# ============================================================
# SESSION STATE
# ============================================================

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


# ============================================================
# HELPERS
# ============================================================

def today_ist():
    return datetime.now(IST).date()


def empty_df():
    return pd.DataFrame(columns=COLUMNS)


def get_services():

    return sorted(
        set(
            BASE_SERVICES
            + st.session_state.custom_services
        ),
        key=str.lower
    ) + ["Other"]


def clean_df(df):

    if df is None or df.empty:
        return empty_df()

    df = df.copy()

    for col in COLUMNS:

        if col not in df.columns:

            if col in [
                "amount",
                "net_amount",
                "cash",
                "credit"
            ]:
                df[col] = 0

            else:
                df[col] = ""

    # ----------------------------
    # TEXT
    # ----------------------------

    for col in [
        "name",
        "mobile",
        "service",
        "expiry"
    ]:

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # ----------------------------
    # DATE
    # ----------------------------

    # IMPORTANT:
    # Do NOT use pd.to_datetime here.
    # It can shift Google Sheet dates by one day.
    raw_date = (
        df["created_at"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["created_at"] = raw_date.str[:10]

    # ----------------------------
    # NUMBERS
    # ----------------------------

    for col in [
        "amount",
        "net_amount",
        "cash",
        "credit"
    ]:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    # ----------------------------
    # ROW NUMBER
    # ----------------------------

    df["_row_number"] = pd.to_numeric(
        df["_row_number"],
        errors="coerce"
    ).fillna(0).astype(int)

    return df[COLUMNS]


# ============================================================
# GET CUSTOMER RECORDS
# ============================================================

@st.cache_data(ttl=5)
def get_records():

    try:

        response = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_records",
                "t": int(
                    datetime.now().timestamp()
                )
            },
            timeout=20
        )

        if response.status_code != 200:
            return empty_df()

        data = response.json()

        if not isinstance(data, list):
            return empty_df()

        return clean_df(
            pd.DataFrame(data)
        )

    except Exception:

        return empty_df()


# ============================================================
# GET EXPENSES
# ============================================================

def get_expenses():

    try:

        response = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_expenses",
                "t": int(
                    datetime.now().timestamp()
                )
            },
            timeout=20
        )

        if response.status_code != 200:
            return []

        data = response.json()

        if isinstance(data, list):
            return data

        return []

    except Exception:

        return []


# ============================================================
# POST API
# ============================================================

def post_api(payload):

    try:

        response = requests.post(
            WEB_APP_URL,
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json"
            },
            timeout=20
        )

        try:

            data = response.json()

            return (
                bool(
                    data.get("success")
                ),
                str(
                    data.get(
                        "message",
                        data.get(
                            "error",
                            "Request failed"
                        )
                    )
                )
            )

        except Exception:

            return (
                response.status_code < 400,
                "Success"
            )

    except Exception as e:

        return False, str(e)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&display=swap'
);

.stApp {

    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(34,211,238,.08),
            transparent 28%
        ),
        radial-gradient(
            circle at 90% 15%,
            rgba(59,130,246,.08),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #05080f,
            #0b1220 52%,
            #07111b
        );

    color:#f8fafc;
    font-family:'Inter',sans-serif;
}

.block-container {

    max-width:1450px;
    padding-top:1rem;
    padding-bottom:3rem;

}


/* HEADER */

.nc-header {

    text-align:center;
    padding:12px 10px 14px;

}

.nc-title {

    font-family:'Orbitron',Arial,sans-serif;

    font-size:40px;

    line-height:1.25;

    font-weight:800;

    letter-spacing:3px;

    color:#22d3ee;

    text-shadow:
        0 0 18px rgba(34,211,238,.35);

}

.nc-main-title {

    font-family:'Inter',sans-serif;

    font-size:21px;

    font-weight:800;

    letter-spacing:2px;

    color:#ffffff;

    margin-top:5px;

}

.nc-sub {

    font-size:11px;

    letter-spacing:2px;

    color:#94a3b8;

    margin-top:4px;

}


/* TOP SUMMARY */

.nc-top {

    background:
        rgba(15,23,42,.88);

    border:
        1px solid
        rgba(34,211,238,.25);

    border-radius:12px;

    padding:7px 13px;

    text-align:right;

    font-size:12px;

    line-height:1.8;

}

.profit {

    color:#22c55e;

    font-weight:800;

}

.cash {

    color:#22c55e;

    font-weight:800;

}

.credit {

    color:#ef4444;

    font-weight:800;

}


/* SECTION */

.nc-section {

    font-family:'Orbitron',sans-serif;

    font-size:18px;

    font-weight:700;

    color:#e2e8f0;

    margin:8px 0 14px;

}


/* GREEN CARD */

.nc-green {

    background:
        linear-gradient(
            145deg,
            rgba(22,101,52,.30),
            rgba(15,23,42,.88)
        );

    border:
        1px solid
        rgba(34,197,94,.42);

    border-left:
        5px solid #22c55e;

    border-radius:12px;

    padding:10px 13px;

    margin:5px 0;

}


/* RED CARD */

.nc-red {

    background:
        linear-gradient(
            145deg,
            rgba(127,29,29,.30),
            rgba(15,23,42,.88)
        );

    border:
        1px solid
        rgba(239,68,68,.42);

    border-left:
        5px solid #ef4444;

    border-radius:12px;

    padding:10px 13px;

    margin:5px 0;

}


/* METRICS */

div[data-testid="stMetric"] {

    background:
        linear-gradient(
            145deg,
            rgba(15,23,42,.95),
            rgba(30,41,59,.75)
        );

    border:
        1px solid
        rgba(96,165,250,.20);

    border-radius:15px;

    padding:15px;

}


/* BUTTON */

.stButton > button {

    border-radius:9px;

    font-weight:700;

}

</style>

<div class="nc-header">

    <div class="nc-title">
        NOOR CYBER WORLD
    </div>

    <div class="nc-main-title">
        CUSTOMER MANAGEMENT SYSTEM
    </div>

    <div class="nc-sub">
        DIGITAL SERVICE • CUSTOMER RECORD • SMART MANAGEMENT
    </div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

df = get_records()

expenses = get_expenses()

if df.empty:
    df = empty_df()


# ============================================================
# SELECTED DATE
# ============================================================

selected_date = (
    st.session_state.selected_date
)

selected_date_str = (
    selected_date.strftime(
        "%Y-%m-%d"
    )
)


# ============================================================
# SELECTED DAY DATA
# ============================================================

if not df.empty:

    day_df = df[
        df["created_at"]
        .astype(str)
        .str[:10]
        == selected_date_str
    ].copy()

else:

    day_df = empty_df()


# ============================================================
# TOP NET INCOME
# ============================================================

today_string = (
    today_ist().strftime(
        "%Y-%m-%d"
    )
)

month_string = (
    today_ist().strftime(
        "%Y-%m"
    )
)

year_string = (
    today_ist().strftime(
        "%Y"
    )
)


if not df.empty:

    today_net = df.loc[
        df["created_at"]
        .astype(str)
        .str[:10]
        == today_string,
        "net_amount"
    ].sum()

    month_net = df.loc[
        df["created_at"]
        .astype(str)
        .str[:7]
        == month_string,
        "net_amount"
    ].sum()

    year_net = df.loc[
        df["created_at"]
        .astype(str)
        .str[:4]
        == year_string,
        "net_amount"
    ].sum()

else:

    today_net = 0
    month_net = 0
    year_net = 0


# ============================================================
# TOP SUMMARY DISPLAY
# ============================================================

st.markdown(
    f"""
<div class="nc-top">

<b>📅 TODAY NET INCOME:</b>
<span class="profit">
₹ {today_net:,.0f}
</span>

&nbsp;&nbsp; | &nbsp;&nbsp;

<b>🗓️ MONTH NET INCOME:</b>
<span class="profit">
₹ {month_net:,.0f}
</span>

&nbsp;&nbsp; | &nbsp;&nbsp;

<b>📊 YEAR NET INCOME:</b>
<span class="profit">
₹ {year_net:,.0f}
</span>

</div>
""",
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# DATE NAVIGATION
# ============================================================

previous_col, date_col, next_col = (
    st.columns([1,4,1])
)


with previous_col:

    if st.button(
        "❮ PREVIOUS DAY",
        use_container_width=True
    ):

        st.session_state.selected_date -= (
            timedelta(days=1)
        )

        st.rerun()


with date_col:

    picked_date = st.date_input(
        "Working Date",
        value=selected_date,
        label_visibility="collapsed"
    )

    if (
        picked_date
        != selected_date
    ):

        st.session_state.selected_date = (
            picked_date
        )

        st.rerun()


with next_col:

    if st.button(
        "NEXT DAY ❯",
        use_container_width=True
    ):

        st.session_state.selected_date += (
            timedelta(days=1)
        )

        st.rerun()


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 TODAY'S ENTRIES & ADD ENTRY",
        "🔴 CREDIT COLLECTION",
        "🔔 RENEWAL ALERTS",
        "💸 SHOP EXPENSES & PROFIT",
        "📂 RECORDS & SEARCH"
    ]
)
