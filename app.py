import streamlit as st
import pandas as pd
import requests
import json
import io
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import quote

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NOOR CYBER WORLD",
    page_icon="🖥️",
    layout="wide"
)


# ============================================================
# CONSTANTS
# ============================================================

IST = timezone(timedelta(hours=5, minutes=30))

WEB_APP_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwSipN_etRHmOKXczikdg1gwzBvksliKCLQ0NYIJX9BbCGcyalc8H14aMTo_mNAbytK"
    "/exec"
)

CUSTOMER_COLUMNS = [
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

EXPENSE_COLUMNS = [
    "created_at",
    "title",
    "amount",
    "_row_number"
]


# ============================================================
# SERVICES
# ============================================================

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


if "custom_services" not in st.session_state:
    st.session_state.custom_services = []


def get_services():

    all_services = (
        DEFAULT_SERVICES
        + st.session_state.custom_services
    )

    all_services = sorted(
        set(
            x.strip()
            for x in all_services
            if x and x.strip()
        ),
        key=lambda x: x.lower()
    )

    all_services.append("Other")

    return all_services


SERVICES = get_services()


# ============================================================
# SESSION STATE
# ============================================================

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now(IST).date()

if "editing_row" not in st.session_state:
    st.session_state.editing_row = None

if "last_saved_wa" not in st.session_state:
    st.session_state.last_saved_wa = None

if "success_message" not in st.session_state:
    st.session_state.success_message = None

if "delete_confirm_row" not in st.session_state:
    st.session_state.delete_confirm_row = None


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&display=swap');

:root {
    --red: #ef4444;
    --green: #22c55e;
    --cyan: #22d3ee;
    --blue: #3b82f6;
    --dark: #0f172a;
    --border: rgba(96,165,250,.25);
}

.stApp {
    background:
        radial-gradient(
            circle at top,
            rgba(15,23,42,.96),
            rgba(2,6,23,.98)
        );
    color: #f8fafc;
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1450px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}


/* ========================================================
   MAIN HEADER
   ======================================================== */

.nc-header {
    text-align: center;
    padding: 8px 10px 12px;
    margin-bottom: 8px;
}

.nc-title {
    font-family: 'Orbitron', Arial, sans-serif;
    font-size: 36px;
    line-height: 1.15;
    font-weight: 800;
    letter-spacing: 3px;
    color: #22d3ee;
    margin: 0;
    text-shadow:
        0 0 8px rgba(34,211,238,.45),
        0 0 22px rgba(34,211,238,.20);
}

.nc-main-title {
    font-family: Arial, sans-serif;
    font-size: 21px;
    line-height: 1.2;
    font-weight: 700;
    letter-spacing: 2px;
    color: #ffffff;
    margin-top: 5px;
}

.nc-sub {
    font-size: 11px;
    letter-spacing: 1.5px;
    color: #94a3b8;
    margin-top: 4px;
}


/* ========================================================
   TOP INCOME BOX
   ======================================================== */

.income-box {
    width: fit-content;
    margin: 5px 0 12px auto;
    padding: 9px 15px;

    background:
        linear-gradient(
            145deg,
            rgba(15,23,42,.96),
            rgba(30,41,59,.90)
        );

    border: 1px solid rgba(34,211,238,.25);
    border-radius: 10px;

    font-size: 11px;
    line-height: 1.8;
    color: #cbd5e1;

    box-shadow:
        0 8px 25px rgba(0,0,0,.22);
}

.income-box .profit {
    color: #22c55e;
    font-weight: 800;
}


/* ========================================================
   SECTION
   ======================================================== */

.nc-section {
    font-family: 'Orbitron', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #e2e8f0;
    margin: 8px 0 14px;
}


/* ========================================================
   ENTRY CARDS
   ======================================================== */

.nc-card-green {
    background:
        linear-gradient(
            145deg,
            rgba(22,101,52,.28),
            rgba(15,23,42,.90)
        );

    border: 1px solid rgba(34,197,94,.45);
    border-left: 5px solid #22c55e;

    border-radius: 10px;
    padding: 11px 13px;
    margin: 5px 0;
}

.nc-card-red {
    background:
        linear-gradient(
            145deg,
            rgba(127,29,29,.28),
            rgba(15,23,42,.90)
        );

    border: 1px solid rgba(239,68,68,.45);
    border-left: 5px solid #ef4444;

    border-radius: 10px;
    padding: 11px 13px;
    margin: 5px 0;
}


/* ========================================================
   RECORD TABLE
   ======================================================== */

.record-header {
    background: #172033;
    border: 1px solid #334155;
    padding: 8px 10px;
    border-radius: 7px;
    font-weight: 700;
    font-size: 12px;
    color: #e2e8f0;
}

.record-row {
    background: rgba(15,23,42,.82);
    border: 1px solid rgba(71,85,105,.45);
    padding: 5px 7px;
    border-radius: 7px;
    margin-top: 3px;
    font-size: 12px;
}

.record-row:hover {
    border-color: rgba(34,211,238,.45);
}


/* ========================================================
   METRICS
   ======================================================== */

div[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            rgba(15,23,42,.94),
            rgba(30,41,59,.80)
        );

    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 14px;

    box-shadow: 0 10px 30px rgba(0,0,0,.20);
}

div[data-testid="stMetricLabel"] {
    color: #cbd5e1;
}

div[data-testid="stMetricValue"] {
    font-weight: 800;
}


/* ========================================================
   EXPENSE
   ======================================================== */

.expense-card {
    background:
        linear-gradient(
            145deg,
            rgba(127,29,29,.38),
            rgba(15,23,42,.92)
        );

    border: 1px solid rgba(239,68,68,.55);
    border-left: 5px solid #ef4444;

    border-radius: 10px;
    padding: 11px 13px;
    margin: 5px 0;
}


/* ========================================================
   SMALL INFO
   ======================================================== */

.top-info {
    background: rgba(15,23,42,.85);
    border: 1px solid rgba(34,211,238,.25);
    border-radius: 10px;
    padding: 9px 13px;
    text-align: center;
    color: #cbd5e1;
    font-size: 12px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HELPERS
# ============================================================

def today_ist():
    return datetime.now(IST).date()


def empty_customer_df():
    return pd.DataFrame(columns=CUSTOMER_COLUMNS)


def empty_expense_df():
    return pd.DataFrame(columns=EXPENSE_COLUMNS)


def money(value):
    try:
        return f"₹ {float(value):,.0f}"
    except Exception:
        return "₹ 0"


def number_value(value):

    if value is None:
        return 0

    try:
        text = str(value).strip()

        if not text:
            return 0

        text = (
            text
            .replace(",", "")
            .replace("₹", "")
            .replace("Rs.", "")
            .replace("Rs", "")
        )

        return float(text)

    except Exception:
        return 0


def clean_text(value):

    if value is None:
        return ""

    return str(value).strip()


def normalize_date(value):

    if value is None:
        return ""

    text = str(value).strip()

    if not text:
        return ""

    # Already correct
    if len(text) >= 10:
        first10 = text[:10]

        if (
            len(first10) == 10
            and first10[4] == "-"
            and first10[7] == "-"
        ):
            try:
                datetime.strptime(
                    first10,
                    "%Y-%m-%d"
                )
                return first10
            except Exception:
                pass

    try:

        dt = pd.to_datetime(
            value,
            errors="coerce"
        )

        if pd.isna(dt):
            return text

        return dt.strftime(
            "%Y-%m-%d"
        )

    except Exception:

        return text


def date_mask(df, selected_date):

    if df.empty:
        return pd.Series(
            dtype=bool,
            index=df.index
        )

    dates = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    return (
        dates.dt.date
        == selected_date
    )


# ============================================================
# CLEAN CUSTOMER DATA
# ============================================================

def clean_customer_df(df):

    if df is None or df.empty:
        return empty_customer_df()

    df = df.copy()

    for col in CUSTOMER_COLUMNS:

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

    df["created_at"] = (
        df["created_at"]
        .apply(normalize_date)
    )

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

    df["_row_number"] = pd.to_numeric(
        df["_row_number"],
        errors="coerce"
    ).fillna(0).astype(int)

    return df[CUSTOMER_COLUMNS]


# ============================================================
# CLEAN EXPENSE DATA
# ============================================================

def clean_expense_df(df):

    if df is None or df.empty:
        return empty_expense_df()

    df = df.copy()

    for col in EXPENSE_COLUMNS:

        if col not in df.columns:

            if col == "amount":
                df[col] = 0
            else:
                df[col] = ""

    df["created_at"] = (
        df["created_at"]
        .apply(normalize_date)
    )

    df["title"] = (
        df["title"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    ).fillna(0)

    df["_row_number"] = pd.to_numeric(
        df["_row_number"],
        errors="coerce"
    ).fillna(0).astype(int)

    return df[EXPENSE_COLUMNS]


# ============================================================
# API POST
# ============================================================

def api_post(payload):

    try:

        response = requests.post(
            WEB_APP_URL,
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json"
            },
            timeout=25
        )

        if response.status_code >= 400:
            return False, (
                f"HTTP {response.status_code}"
            )

        try:

            result = response.json()

            if isinstance(result, dict):

                if result.get("success") is True:
                    return True, str(
                        result.get(
                            "message",
                            "Success"
                        )
                    )

                return False, str(
                    result.get(
                        "error",
                        result.get(
                            "message",
                            "Request failed"
                        )
                    )
                )

        except Exception:

            return True, "Success"

        return True, "Success"

    except Exception as e:

        return False, str(e)


# ============================================================
# FETCH CUSTOMER RECORDS
# ============================================================

@st.cache_data(ttl=5)
def fetch_customer_records():

    try:

        response = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_records",
                "t": int(
                    datetime.now().timestamp()
                )
            },
            timeout=25
        )

        if response.status_code != 200:
            return empty_customer_df()

        data = response.json()

        if not isinstance(data, list):
            return empty_customer_df()

        return clean_customer_df(
            pd.DataFrame(data)
        )

    except Exception:

        return empty_customer_df()


# ============================================================
# FETCH EXPENSES
# ============================================================

@st.cache_data(ttl=5)
def fetch_expenses():

    try:

        response = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_expenses",
                "t": int(
                    datetime.now().timestamp()
                )
            },
            timeout=25
        )

        if response.status_code != 200:
            return empty_expense_df()

        data = response.json()

        if not isinstance(data, list):
            return empty_expense_df()

        return clean_expense_df(
            pd.DataFrame(data)
        )

    except Exception:

        return empty_expense_df()


# ============================================================
# PDF
# ============================================================

def generate_pdf(df):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=17,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,
        spaceAfter=15
    )

    elements = []

    elements.append(
        Paragraph(
            "NOOR CYBER WORLD - CUSTOMER RECORDS",
            title_style
        )
    )

    elements.append(
        Spacer(1, 8)
    )

    headers = [
        "Date",
        "Name",
        "Mobile",
        "Service",
        "Amount",
        "Net",
        "Cash",
        "Credit",
        "Expiry"
    ]

    data = [headers]

    for _, row in df.iterrows():

        data.append([
            str(row["created_at"]),
            str(row["name"]),
            str(row["mobile"]),
            str(row["service"]),
            f"Rs. {float(row['amount']):.0f}",
            f"Rs. {float(row['net_amount']):.0f}",
            f"Rs. {float(row['cash']):.0f}",
            f"Rs. {float(row['credit']):.0f}",
            str(row["expiry"])
        ])

    table = Table(
        data,
        colWidths=[
            50,
            70,
            70,
            105,
            45,
            45,
            45,
            45,
            55
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1e293b")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.HexColor("#f8fafc")
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#cbd5e1")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            )
        ])
    )

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return buffer


# ============================================================
# LOAD DATA
# ============================================================

df_all = fetch_customer_records()
expense_df = fetch_expenses()


# ============================================================
# MOBILE → NAME MAP
# ============================================================

mobile_to_name = {}

if not df_all.empty:

    for _, row in df_all.iterrows():

        mobile = clean_text(
            row["mobile"]
        )

        name = clean_text(
            row["name"]
        )

        if mobile and name:
            mobile_to_name[mobile] = name


# ============================================================
# DATE VARIABLES
# ============================================================

now = datetime.now(IST)

today_date = now.date()

today_str = today_date.strftime(
    "%Y-%m-%d"
)

current_month = now.strftime(
    "%Y-%m"
)

current_year = now.strftime(
    "%Y"
)


# ============================================================
# DASHBOARD CALCULATIONS
# ============================================================

if not df_all.empty:

    created = pd.to_datetime(
        df_all["created_at"],
        errors="coerce"
    )

    today_mask = (
        created.dt.strftime("%Y-%m-%d")
        == today_str
    )

    month_mask = (
        created.dt.strftime("%Y-%m")
        == current_month
    )

    year_mask = (
        created.dt.strftime("%Y")
        == current_year
    )

    today_net_income = float(
        df_all.loc[
            today_mask,
            "net_amount"
        ].sum()
    )

    month_net_income = float(
        df_all.loc[
            month_mask,
            "net_amount"
        ].sum()
    )

    year_net_income = float(
        df_all.loc[
            year_mask,
            "net_amount"
        ].sum()
    )

else:

    today_net_income = 0
    month_net_income = 0
    year_net_income = 0


# ============================================================
# HEADER — ONLY ONE
# ============================================================

st.markdown(
    """
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
# SMALL INCOME TABLE
# ============================================================

st.markdown(
    f"""
    <div class="income-box">

        <b>📅 TODAY NET INCOME:</b>
        <span class="profit">
            ₹ {today_net_income:,.0f}
        </span>

        &nbsp;&nbsp; | &nbsp;&nbsp;

        <b>🗓️ MONTH NET INCOME:</b>
        <span class="profit">
            ₹ {month_net_income:,.0f}
        </span>

        &nbsp;&nbsp; | &nbsp;&nbsp;

        <b>📊 YEAR NET INCOME:</b>
        <span class="profit">
            ₹ {year_net_income:,.0f}
        </span>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SELECTED DATE
# ============================================================

selected_date = st.session_state.selected_date

selected_date_str = selected_date.strftime(
    "%Y-%m-%d"
)

selected_day_df = df_all[
    date_mask(
        df_all,
        selected_date
    )
].copy()


# ============================================================
# DATE NAVIGATION
# ============================================================

p_col, d_col, n_col = st.columns(
    [1, 4, 1]
)

with p_col:

    if st.button(
        "❮ PREVIOUS DAY",
        use_container_width=True
    ):

        st.session_state.selected_date = (
            selected_date
            - timedelta(days=1)
        )

        st.rerun()


with d_col:

    picked = st.date_input(
        "Working Date",
        value=selected_date,
        label_visibility="collapsed"
    )

    if picked != selected_date:

        st.session_state.selected_date = picked

        st.rerun()


with n_col:

    if st.button(
        "NEXT DAY ❯",
        use_container_width=True
    ):

        st.session_state.selected_date = (
            selected_date
            + timedelta(days=1)
        )

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
# TAB 1
# ============================================================

with tab1:

    st.markdown(
        f"""
        <div class="nc-section">
            📋 Entries for
            {selected_date.strftime("%d-%m-%Y")}
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # DAY SUMMARY
    # --------------------------------------------------------

    total_gross = float(
        selected_day_df["amount"].sum()
    )

    total_net = float(
        selected_day_df["net_amount"].sum()
    )

    cash_sum = float(
        selected_day_df["cash"].sum()
    )

    credit_sum = float(
        selected_day_df["credit"].sum()
    )


    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "TOTAL COLLECTION",
        money(total_gross)
    )

    m2.metric(
        "CASH RECEIVED",
        money(cash_sum)
    )

    m3.metric(
        "PENDING CREDIT",
        money(credit_sum)
    )

    m4.metric(
        "NET INCOME",
        money(total_net)
    )


    st.markdown("---")


    # --------------------------------------------------------
    # TODAY / SELECTED DAY ENTRIES
    # --------------------------------------------------------

    if selected_day_df.empty:

        st.info(
            "ℹ️ No entries recorded for this date yet."
        )

    else:

        for _, row in selected_day_df.iterrows():

            row_id = int(
                row["_row_number"]
            )

            is_credit = (
                float(row["credit"]) > 0
            )

            border_color = (
                "#ef4444"
                if is_credit
                else "#22c55e"
            )

            payment_text = (
                "🔴 CREDIT"
                if is_credit
                else "🟢 CASH"
            )


            left, edit_col, delete_col = st.columns(
                [8, 1, 1]
            )


            with left:

                st.markdown(
                    f"""
                    <div style="
                        background:rgba(15,23,42,.88);
                        border:1px solid rgba(71,85,105,.45);
                        border-left:5px solid {border_color};
                        border-radius:8px;
                        padding:9px 12px;
                        margin-bottom:4px;
                        font-size:12px;
                    ">

                    <b>👤 {row['name']}</b>
                    &nbsp; ({row['mobile']})
                    &nbsp;&nbsp; | &nbsp;&nbsp;
                    <b>{payment_text}</b>

                    <br>

                    <b>Service:</b>
                    {row['service']}

                    &nbsp;&nbsp; | &nbsp;&nbsp;

                    <b>Amount:</b>
                    ₹ {float(row['amount']):,.0f}

                    &nbsp;&nbsp; | &nbsp;&nbsp;

                    <b>Net:</b>
                    ₹ {float(row['net_amount']):,.0f}

                    &nbsp;&nbsp; | &nbsp;&nbsp;

                    <b>Cash:</b>
                    ₹ {float(row['cash']):,.0f}

                    &nbsp;&nbsp; | &nbsp;&nbsp;

                    <b>Credit:</b>
                    ₹ {float(row['credit']):,.0f}

                    <br>

                    <b>Expiry:</b>
                    {row['expiry']}

                    &nbsp;&nbsp; | &nbsp;&nbsp;

                    <b>Date:</b>
                    {row['created_at']}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with edit_col:

                if st.button(
                    "✏️",
                    key=f"edit_day_{row_id}",
                    help="Edit entry"
                ):

                    st.session_state.editing_row = (
                        row.to_dict()
                    )

                    st.rerun()


            with delete_col:

                if st.button(
                    "🗑️",
                    key=f"delete_day_{row_id}",
                    help="Delete entry"
                ):

                    st.session_state.delete_confirm_row = (
                        row.to_dict()
                    )

                    st.rerun()


    # --------------------------------------------------------
    # DELETE CONFIRMATION
    # --------------------------------------------------------

    if st.session_state.delete_confirm_row:

        delete_data = (
            st.session_state.delete_confirm_row
        )

        st.warning(
            f"⚠️ Delete entry of "
            f"**{delete_data.get('name', '')}** "
            f"₹ {float(delete_data.get('amount', 0)):,.0f}?"
        )

        yes_col, no_col = st.columns(2)

        with yes_col:

            if st.button(
                "✅ YES, DELETE",
                type="primary",
                use_container_width=True
            ):

                payload = {
                    "action": "delete",
                    "row_number": int(
                        delete_data["_row_number"]
                    )
                }

                with st.spinner(
                    "Deleting..."
                ):

                    ok, msg = api_post(
                        payload
                    )

                if ok:

                    fetch_customer_records.clear()

                    st.session_state.delete_confirm_row = None

                    st.session_state.success_message = (
                        "Entry deleted successfully."
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Delete failed: {msg}"
                    )

        with no_col:

            if st.button(
                "❌ NO, CANCEL",
                use_container_width=True
            ):

                st.session_state.delete_confirm_row = None

                st.rerun()


    st.markdown("---")


    # ========================================================
    # ADD / EDIT ENTRY FORM
    # ========================================================

    is_editing = (
        st.session_state.editing_row
        is not None
    )

    if is_editing:

        form_title = "✏️ EDIT CUSTOMER ENTRY"

    else:

        form_title = "➕ ADD NEW CUSTOMER ENTRY"


    st.markdown(
        f"""
        <div class="nc-section">
            {form_title}
        </div>
        """,
        unsafe_allow_html=True
    )


    edit_data = (
        st.session_state.editing_row
        or {}
    )


    # --------------------------------------------------------
    # MOBILE
    # --------------------------------------------------------

    mobile_default = clean_text(
        edit_data.get(
            "mobile",
            ""
        )
    )


    mobile_input = st.text_input(
        "Mobile Number*",
        value=mobile_default,
        key="customer_mobile_input"
    )


    clean_mobile = (
        str(mobile_input)
        .strip()
    )


    # --------------------------------------------------------
    # AUTO NAME
    # --------------------------------------------------------

    if not is_editing:

        detected_name = mobile_to_name.get(
            clean_mobile,
            ""
        )

        if detected_name:

            if (
                st.session_state.get(
                    "customer_name_input",
                    ""
                )
                != detected_name
            ):

                st.session_state.customer_name_input = (
                    detected_name
                )


    # --------------------------------------------------------
    # TWO COLUMNS
    # --------------------------------------------------------

    left, right = st.columns(2)


    with left:

        name_default = clean_text(
            edit_data.get(
                "name",
                ""
            )
        )


        if is_editing:

            if (
                "customer_name_input"
                not in st.session_state
            ):

                st.session_state.customer_name_input = (
                    name_default
                )


        name_input = st.text_input(
            "Customer Name*",
            key="customer_name_input"
        )


        current_service = clean_text(
            edit_data.get(
                "service",
                SERVICES[0]
            )
        )


        if current_service in SERVICES:

            service_index = SERVICES.index(
                current_service
            )

        else:

            service_index = SERVICES.index(
                "Other"
            )


        service_selected = st.selectbox(
            "Search / Select Service*",
            SERVICES,
            index=service_index,
            key="customer_service_input"
        )


        if service_selected == "Other":

            custom_default = (
                current_service
                if current_service
                not in SERVICES
                else ""
            )

            custom_service = st.text_input(
                "Custom Service Name*",
                value=custom_default,
                key="custom_service_input"
            )

        else:

            custom_service = ""


    with right:

        amount_default = int(
            number_value(
                edit_data.get(
                    "amount",
                    0
                )
            )
        )


        net_default = int(
            number_value(
                edit_data.get(
                    "net_amount",
                    0
                )
            )
        )


        amount = st.number_input(
            "Total Amount / Gross (₹)*",
            min_value=0,
            step=10,
            value=amount_default,
            key="customer_amount_input"
        )


        net_amount = st.number_input(
            "Net Income / Profit (₹)*",
            min_value=0,
            step=10,
            value=net_default,
            key="customer_net_input"
        )


        # ----------------------------------------------------
        # PAYMENT TYPE
        # ----------------------------------------------------

        existing_credit = number_value(
            edit_data.get(
                "credit",
                0
            )
        )

        existing_cash = number_value(
            edit_data.get(
                "cash",
                0
            )
        )


        default_payment_index = (
            1
            if existing_credit > 0
            else 0
        )


        payment_choice = st.radio(
            "Payment Type*",
            [
                "💵 Cash",
                "🔴 Credit (Udhari)"
            ],
            index=default_payment_index,
            horizontal=True,
            key="customer_payment_input"
        )


        if "Credit" in payment_choice:

            calculated_cash = 0

            calculated_credit = int(
                amount
            )

        else:

            calculated_cash = int(
                amount
            )

            calculated_credit = 0


        st.markdown(
            f"""
            <div class="top-info">

                💵 <b>Cash:</b>
                ₹ {calculated_cash:,}

                &nbsp;&nbsp;&nbsp;

                🔴 <b>Credit:</b>
                ₹ {calculated_credit:,}

            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # EXPIRY
        # ----------------------------------------------------

        existing_expiry = clean_text(
            edit_data.get(
                "expiry",
                "N/A"
            )
        )


        has_expiry_default = (
            existing_expiry not in [
                "",
                "N/A"
            ]
        )


        has_expiry = st.checkbox(
            "Requires Renewal / Validity?",
            value=has_expiry_default,
            key="customer_expiry_check"
        )


        validity_unit = st.selectbox(
            "Validity Unit",
            [
                "Days",
                "Months",
                "Years"
            ],
            index=1,
            key="customer_validity_unit"
        )


        validity_value = st.number_input(
            "Validity Duration",
            min_value=1,
            value=1,
            step=1,
            key="customer_validity_value"
        )


    # ========================================================
    # SAVE / CANCEL
    # ========================================================

    save_col, cancel_col = st.columns(2)


    with save_col:

        save_label = (
            "💾 UPDATE ENTRY"
            if is_editing
            else "⚡ SAVE ENTRY"
        )


        if st.button(
            save_label,
            type="primary",
            use_container_width=True
        ):

            if not name_input.strip():

                st.error(
                    "Please enter Customer Name."
                )

                st.stop()


            if not mobile_input.strip():

                st.error(
                    "Please enter Mobile Number."
                )

                st.stop()


            if amount <= 0:

                st.error(
                    "Amount must be greater than zero."
                )

                st.stop()


            if net_amount < 0:

                st.error(
                    "Net Income cannot be negative."
                )

                st.stop()


            # ------------------------------------------------
            # SERVICE
            # ------------------------------------------------

            final_service = service_selected


            if service_selected == "Other":

                if not custom_service.strip():

                    st.error(
                        "Please enter Custom Service Name."
                    )

                    st.stop()


                final_service = (
                    custom_service.strip()
                )


                if (
                    final_service
                    not in st.session_state.custom_services
                ):

                    st.session_state.custom_services.append(
                        final_service
                    )


            # ------------------------------------------------
            # EXPIRY
            # ------------------------------------------------

            expiry = "N/A"


            if has_expiry:

                base_date = selected_date


                if validity_unit == "Days":

                    expiry_date = (
                        base_date
                        + timedelta(
                            days=int(
                                validity_value
                            )
                        )
                    )

                elif validity_unit == "Months":

                    expiry_date = (
                        base_date
                        + relativedelta(
                            months=int(
                                validity_value
                            )
                        )
                    )

                else:

                    expiry_date = (
                        base_date
                        + relativedelta(
                            years=int(
                                validity_value
                            )
                        )
                    )


                expiry = expiry_date.strftime(
                    "%Y-%m-%d"
                )


            # ------------------------------------------------
            # PAYMENT
            # ------------------------------------------------

            if "Credit" in payment_choice:

                final_cash = 0

                final_credit = int(
                    amount
                )

            else:

                final_cash = int(
                    amount
                )

                final_credit = 0


            # ------------------------------------------------
            # PAYLOAD
            # ------------------------------------------------

            action = (
                "edit"
                if is_editing
                else "add"
            )


            payload = {

                "action": action,

                "created_at": selected_date_str,

                "name": clean_text(
                    name_input
                ),

                "mobile": clean_text(
                    mobile_input
                ),

                "service": final_service,

                "amount": str(
                    int(amount)
                ),

                "net_amount": str(
                    int(net_amount)
                ),

                "cash": str(
                    final_cash
                ),

                "credit": str(
                    final_credit
                ),

                "expiry": expiry
            }


            if is_editing:

                payload["row_number"] = int(
                    edit_data["_row_number"]
                )


            with st.spinner(
                "Saving to Google Sheet..."
            ):

                ok, msg = api_post(
                    payload
                )


            if ok:

                fetch_customer_records.clear()

                st.session_state.editing_row = None

                thank_message = (
                    f"Dear {name_input.strip()}, "
                    f"Thank you for choosing "
                    f"NOOR CYBER WORLD for "
                    f"{final_service}! "
                    f"Total Amount: Rs.{int(amount)}. "
                    f"We are happy to serve you."
                )


                st.session_state.last_saved_wa = (
                    "https://wa.me/91"
                    + clean_text(
                        mobile_input
                    )
                    + "?text="
                    + quote(
                        thank_message
                    )
                )


                st.session_state.success_message = (
                    "Entry saved successfully."
                )

                st.rerun()


            else:

                st.error(
                    f"Failed to save: {msg}"
                )


    with cancel_col:

        if is_editing:

            if st.button(
                "❌ CANCEL EDIT",
                use_container_width=True
            ):

                st.session_state.editing_row = None

                st.rerun()


    # ========================================================
    # WHATSAPP
    # ========================================================

    if st.session_state.last_saved_wa:

        st.success(
            "🎉 Entry successfully saved!"
        )

        st.link_button(
            "💬 SEND THANK YOU WHATSAPP",
            st.session_state.last_saved_wa,
            use_container_width=True
        )

        if st.button(
            "✖️ CLOSE WHATSAPP BUTTON",
            use_container_width=True
        ):

            st.session_state.last_saved_wa = None

            st.rerun()


# ============================================================
# TAB 2 — CREDIT COLLECTION
# ============================================================

with tab2:

    st.markdown(
        """
        <div class="nc-section">
            🔴 Pending Credit / Udhari Collection
        </div>
        """,
        unsafe_allow_html=True
    )


    if df_all.empty:

        credit_df = empty_customer_df()

    else:

        credit_df = df_all[
            df_all["credit"] > 0
        ].copy()


    if credit_df.empty:

        st.success(
            "🎉 No pending credit! All payments are clear."
        )

    else:

        total_credit = float(
            credit_df["credit"].sum()
        )

        st.error(
            f"⚠️ Total Pending Credit: "
            f"₹ {total_credit:,.0f} "
            f"({len(credit_df)} Entries)"
        )


        st.markdown("---")


        for _, row in credit_df.iterrows():

            row_id = int(
                row["_row_number"]
            )


            info_col, wa_col, paid_col = st.columns(
                [5, 2, 2]
            )


            with info_col:

                st.markdown(
                    f"""
                    <div class="nc-card-red">

                    <b>🔴 {row['name']}</b>
                    ({row['mobile']})

                    <br>

                    Service:
                    <b>{row['service']}</b>

                    <br>

                    Pending Credit:
                    <b style="color:#ef4444;font-size:18px;">
                        ₹ {float(row['credit']):,.0f}
                    </b>

                    <br>

                    Date:
                    {row['created_at']}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with wa_col:

                message = (
                    f"Hello {row['name']}, "
                    f"this is a gentle reminder from "
                    f"NOOR CYBER WORLD. "
                    f"Your pending payment of Rs."
                    f"{int(row['credit'])} "
                    f"for {row['service']} "
                    f"is pending. "
                    f"Please clear your balance. "
                    f"Thank you!"
                )


                wa_url = (
                    "https://wa.me/91"
                    + clean_text(
                        row["mobile"]
                    )
                    + "?text="
                    + quote(message)
                )


                st.link_button(
                    "💬 SEND REMINDER",
                    wa_url,
                    use_container_width=True
                )


            with paid_col:

                if st.button(
                    "💵 CASH RECEIVED",
                    key=f"credit_paid_{row_id}",
                    use_container_width=True
                ):

                    payload = {
                        "action": "credit_to_cash",
                        "row_number": row_id
                    }


                    with st.spinner(
                        "Updating payment..."
                    ):

                        ok, msg = api_post(
                            payload
                        )


                    if ok:

                        fetch_customer_records.clear()

                        st.session_state.success_message = (
                            f"₹ {int(row['credit'])} "
                            f"received from "
                            f"{row['name']}."
                        )

                        st.rerun()

                    else:

                        st.error(
                            f"Error: {msg}"
                        )


# ============================================================
# TAB 3 — RENEWAL
# ============================================================

with tab3:

    st.markdown(
        """
        <div class="nc-section">
            🔔 Renewal Alerts — Next 15 Days
        </div>
        """,
        unsafe_allow_html=True
    )


    today = today_ist()

    renewal_rows = []


    if not df_all.empty:

        for _, row in df_all.iterrows():

            expiry_text = clean_text(
                row["expiry"]
            )


            if (
                expiry_text
                and expiry_text != "N/A"
            ):

                try:

                    expiry_date = datetime.strptime(
                        expiry_text[:10],
                        "%Y-%m-%d"
                    ).date()

                    days_left = (
                        expiry_date
                        - today
                    ).days


                    if 0 <= days_left <= 15:

                        renewal_rows.append(
                            (
                                row,
                                expiry_date,
                                days_left
                            )
                        )

                except Exception:

                    continue


    if not renewal_rows:

        st.success(
            "🎉 No renewals due in the next 15 days."
        )

    else:

        st.warning(
            f"⚠️ {len(renewal_rows)} renewal(s) "
            f"due within next 15 days."
        )


        for row, expiry_date, days_left in renewal_rows:

            formatted_date = (
                expiry_date.strftime(
                    "%d-%m-%Y"
                )
            )


            st.markdown(
                f"""
                <div class="nc-card-red">

                <b>🔴 {row['name']}</b>
                ({row['mobile']})

                <br>

                Service:
                <b>{row['service']}</b>

                <br>

                Expiry:
                <b>{formatted_date}</b>

                &nbsp; | &nbsp;

                {days_left} days remaining

                </div>
                """,
                unsafe_allow_html=True
            )


            message = (
                f"Hello {row['name']}, "
                f"your service {row['service']} "
                f"is expiring on {formatted_date}. "
                f"Please visit NOOR CYBER WORLD "
                f"to renew it on time."
            )


            wa_url = (
                "https://wa.me/91"
                + clean_text(
                    row["mobile"]
                )
                + "?text="
                + quote(message)
            )


            st.link_button(
                f"💬 SEND RENEWAL MESSAGE — {row['name']}",
                wa_url
            )


# ============================================================
# TAB 4 — EXPENSES
# ============================================================

with tab4:

    st.markdown(
        """
        <div class="nc-section">
            💸 Shop Expenses & Real Profit
        </div>
        """,
        unsafe_allow_html=True
    )


    exp_col1, exp_col2 = st.columns(
        [1, 2]
    )


    with exp_col1:

        st.subheader(
            "➕ Add Shop Expense"
        )


        expense_title = st.text_input(
            "Expense Title",
            placeholder="Paper, Rent, Tea, Electricity...",
            key="expense_title_input"
        )


        expense_amount = st.number_input(
            "Expense Amount (₹)",
            min_value=0,
            step=10,
            key="expense_amount_input"
        )


        if st.button(
            "💾 ADD EXPENSE",
            type="primary",
            use_container_width=True
        ):

            if not expense_title.strip():

                st.error(
                    "Please enter expense title."
                )

            elif expense_amount <= 0:

                st.error(
                    "Expense amount must be greater than zero."
                )

            else:

                payload = {
                    "action": "add_expense",
                    "created_at": selected_date_str,
                    "title": expense_title.strip(),
                    "amount": str(
                        int(expense_amount)
                    )
                }


                with st.spinner(
                    "Saving expense..."
                ):

                    ok, msg = api_post(
                        payload
                    )


                if ok:

                    fetch_expenses.clear()

                    st.session_state.success_message = (
                        "Expense added successfully."
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Failed: {msg}"
                    )


    with exp_col2:

        st.subheader(
            f"📊 Expenses for {selected_date_str}"
        )


        selected_expenses = expense_df[
            date_mask(
                expense_df,
                selected_date
            )
        ].copy()


        total_expenses = float(
            selected_expenses["amount"].sum()
        )


        actual_profit = (
            total_net
            - total_expenses
        )


        e1, e2, e3 = st.columns(3)


        e1.metric(
            "NET INCOME",
            money(total_net)
        )

        e2.metric(
            "EXPENSES",
            money(total_expenses)
        )

        e3.metric(
            "ACTUAL PROFIT",
            money(actual_profit)
        )


        st.markdown("---")


        if selected_expenses.empty:

            st.info(
                "No expenses recorded for this date."
            )

        else:

            for _, exp in selected_expenses.iterrows():

                exp_id = int(
                    exp["_row_number"]
                )


                ec1, ec2 = st.columns(
                    [7, 1]
                )


                with ec1:

                    st.markdown(
                        f"""
                        <div class="expense-card">

                        🔴 <b>{exp['title']}</b>

                        &nbsp;&nbsp; | &nbsp;&nbsp;

                        <b>
                            ₹ {float(exp['amount']):,.0f}
                        </b>

                        <br>

                        Date:
                        {exp['created_at']}

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                with ec2:

                    if st.button(
                        "🗑️",
                        key=f"delete_exp_{exp_id}",
                        help="Delete expense"
                    ):

                        payload = {
                            "action": "delete_expense",
                            "row_number": exp_id
                        }


                        with st.spinner(
                            "Deleting..."
                        ):

                            ok, msg = api_post(
                                payload
                            )


                        if ok:

                            fetch_expenses.clear()

                            st.session_state.success_message = (
                                "Expense deleted."
                            )

                            st.rerun()

                        else:

                            st.error(
                                msg
                            )


# ============================================================
# TAB 5 — RECORDS
# ============================================================

with tab5:

    st.markdown(
        """
        <div class="nc-section">
            📂 Customer Records & Instant Search
        </div>
        """,
        unsafe_allow_html=True
    )


    if df_all.empty:

        st.info(
            "No records available."
        )

    else:

        search = st.text_input(
            "🔍 Search Name / Mobile / Service",
            key="record_search"
        )


        if search.strip():

            q = search.strip().lower()

            mask = (
                df_all["name"]
                .str.lower()
                .str.contains(
                    q,
                    na=False
                )
                |
                df_all["mobile"]
                .str.lower()
                .str.contains(
                    q,
                    na=False
                )
                |
                df_all["service"]
                .str.lower()
                .str.contains(
                    q,
                    na=False
                )
            )

            records = df_all[
                mask
            ].copy()

        else:

            records = df_all.copy()


        # ----------------------------------------------------
        # EXPORT
        # ----------------------------------------------------

        export_df = records.drop(
            columns=["_row_number"],
            errors="ignore"
        )


        b1, b2 = st.columns(2)


        with b1:

            st.download_button(
                "📥 DOWNLOAD CSV",
                data=export_df.to_csv(
                    index=False
                ).encode(
                    "utf-8-sig"
                ),
                file_name=(
                    "NOOR_CYBER_WORLD_RECORDS.csv"
                ),
                mime="text/csv",
                use_container_width=True
            )


        with b2:

            pdf_data = generate_pdf(
                export_df
            )


            st.download_button(
                "📄 DOWNLOAD PDF",
                data=pdf_data,
                file_name=(
                    "NOOR_CYBER_WORLD_RECORDS.pdf"
                ),
                mime="application/pdf",
                use_container_width=True
            )


        st.markdown("---")


        st.caption(
            f"Showing {len(records)} records"
        )


        # ----------------------------------------------------
        # COMPACT TABLE HEADER
        # ----------------------------------------------------

        h = st.columns(
            [1.0, 1.6, 1.25, 2.4, 0.85, 0.85, 0.8, 0.8, 1.1, 1.2]
        )


        headers = [
            "DATE",
            "NAME",
            "MOBILE",
            "SERVICE",
            "AMOUNT",
            "NET",
            "CASH",
            "CREDIT",
            "EXPIRY",
            "ACTION"
        ]


        for col, title in zip(
            h,
            headers
        ):

            with col:

                st.markdown(
                    f"""
                    <div class="record-header">
                        {title}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # ----------------------------------------------------
        # TABLE ROWS
        # ----------------------------------------------------

        for _, row in records.iterrows():

            row_id = int(
                row["_row_number"]
            )


            r = st.columns(
                [
                    1.0,
                    1.6,
                    1.25,
                    2.4,
                    0.85,
                    0.85,
                    0.8,
                    0.8,
                    1.1,
                    1.2
                ]
            )


            values = [
                row["created_at"],
                row["name"],
                row["mobile"],
                row["service"],
                f"₹ {float(row['amount']):,.0f}",
                f"₹ {float(row['net_amount']):,.0f}",
                f"₹ {float(row['cash']):,.0f}",
                f"₹ {float(row['credit']):,.0f}",
                row["expiry"]
            ]


            for col, value in zip(
                r[:9],
                values
            ):

                with col:

                    st.markdown(
                        f"""
                        <div class="record-row">
                            {value}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


            with r[9]:

                a1, a2 = st.columns(2)


                with a1:

                    if st.button(
                        "✏️",
                        key=f"record_edit_{row_id}",
                        help="Edit"
                    ):

                        st.session_state.editing_row = (
                            row.to_dict()
                        )

                        st.session_state.selected_date = (
                            pd.to_datetime(
                                row["created_at"]
                            ).date()
                        )

                        st.rerun()


                with a2:

                    if st.button(
                        "🗑️",
                        key=f"record_delete_{row_id}",
                        help="Delete"
                    ):

                        st.session_state.delete_confirm_row = (
                            row.to_dict()
                        )

                        st.rerun()


# ============================================================
# GLOBAL DELETE CONFIRMATION
# ============================================================

if st.session_state.delete_confirm_row:

    delete_data = (
        st.session_state.delete_confirm_row
    )

    st.markdown("---")

    st.error(
        f"⚠️ Delete **{delete_data.get('name', '')}** "
        f"— ₹ {float(delete_data.get('amount', 0)):,.0f}?"
    )

    dc1, dc2 = st.columns(2)


    with dc1:

        if st.button(
            "✅ YES — DELETE",
            type="primary",
            use_container_width=True,
            key="global_yes_delete"
        ):

            payload = {
                "action": "delete",
                "row_number": int(
                    delete_data["_row_number"]
                )
            }


            with st.spinner(
                "Deleting..."
            ):

                ok, msg = api_post(
                    payload
                )


            if ok:

                fetch_customer_records.clear()

                st.session_state.delete_confirm_row = None

                st.session_state.success_message = (
                    "Entry deleted successfully."
                )

                st.rerun()

            else:

                st.error(
                    msg
                )


    with dc2:

        if st.button(
            "❌ NO — CANCEL",
            use_container_width=True,
            key="global_no_delete"
        ):

            st.session_state.delete_confirm_row = None

            st.rerun()


# ============================================================
# SUCCESS TOAST
# ============================================================

if st.session_state.success_message:

    st.toast(
        st.session_state.success_message,
        icon="✅"
    )

    st.session_state.success_message = None
