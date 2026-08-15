import streamlit as st
import pandas as pd
import requests
import json
import io
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import quote

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NOOR CYBER WORLD",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# TIMEZONE
# ============================================================

IST = timezone(timedelta(hours=5, minutes=30))


def today_ist():
    return datetime.now(IST).date()


# ============================================================
# GOOGLE APPS SCRIPT URL
# ============================================================

WEB_APP_URL = (
    "https://script.google.com/macros/s/AKfycbwSipN_etRHmOKXczikdg1gwzBvksliKCLQ0NYIJX9BbCGcyalc8H14aMTo_mNAbytK/exec"
)


# ============================================================
# CUSTOMER COLUMNS
# ============================================================

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


# ============================================================
# DEFAULT SERVICES
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
    "Xerox / Color Printout / Lamination / Scanning",
]


if "custom_services" not in st.session_state:
    st.session_state.custom_services = []

if "editing_row" not in st.session_state:
    st.session_state.editing_row = None

if "selected_date" not in st.session_state:
    st.session_state.selected_date = today_ist()


def get_all_services():

    services = DEFAULT_SERVICES + st.session_state.custom_services

    services = sorted(
        set(
            str(x).strip()
            for x in services
            if str(x).strip()
        ),
        key=lambda x: x.lower()
    )

    services.append("Other")

    return services


SERVICES = get_all_services()


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --green:#22c55e;
    --red:#ef4444;
    --cyan:#22d3ee;
    --dark:#0f172a;
    --border:rgba(148,163,184,.22);
}

.stApp {
    background:
        linear-gradient(
            120deg,
            rgba(2,6,23,.98),
            rgba(15,23,42,.96)
        );
    color:#f8fafc;
    font-family:'Inter',sans-serif;
}

.block-container {
    max-width:1500px;
    padding-top:1rem;
    padding-bottom:3rem;
}

/* HEADER */

.nc-header {
    width:100%;
    text-align:center;
    padding:12px 10px 18px;
    margin-bottom:8px;
    border-bottom:1px solid rgba(34,211,238,.18);
}

.nc-title {
    font-size:32px;
    line-height:1.1;
    font-weight:800;
    letter-spacing:3px;
    color:#ffffff;
}

.nc-main-title {
    margin-top:6px;
    font-size:18px;
    font-weight:700;
    letter-spacing:2px;
    color:#22d3ee;
}

.nc-sub {
    margin-top:5px;
    font-size:10px;
    letter-spacing:1.5px;
    color:#94a3b8;
}

/* SECTION */

.nc-section {
    font-size:20px;
    font-weight:800;
    color:#e2e8f0;
    margin:8px 0 14px;
}

/* METRICS */

div[data-testid="stMetric"] {
    background:rgba(15,23,42,.92);
    border:1px solid rgba(148,163,184,.18);
    border-radius:14px;
    padding:14px 16px;
    box-shadow:0 8px 25px rgba(0,0,0,.18);
}

div[data-testid="stMetricLabel"] {
    color:#94a3b8;
}

div[data-testid="stMetricValue"] {
    font-weight:800;
}

/* GREEN CARD */

.nc-card-green {
    background:linear-gradient(
        135deg,
        rgba(20,83,45,.55),
        rgba(15,23,42,.92)
    );
    border:1px solid rgba(34,197,94,.45);
    border-left:5px solid #22c55e;
    border-radius:10px;
    padding:11px 14px;
    margin:6px 0;
}

/* RED CARD */

.nc-card-red {
    background:linear-gradient(
        135deg,
        rgba(127,29,29,.52),
        rgba(15,23,42,.92)
    );
    border:1px solid rgba(239,68,68,.45);
    border-left:5px solid #ef4444;
    border-radius:10px;
    padding:11px 14px;
    margin:6px 0;
}

/* DASHBOARD BOX */

.dashboard-green {
    background:rgba(20,83,45,.30);
    border:1px solid rgba(34,197,94,.40);
    border-radius:12px;
    padding:14px;
    margin-bottom:8px;
}

.dashboard-red {
    background:rgba(127,29,29,.30);
    border:1px solid rgba(239,68,68,.40);
    border-radius:12px;
    padding:14px;
    margin-bottom:8px;
}

.dashboard-title {
    font-size:16px;
    font-weight:800;
    margin-bottom:8px;
}

.small-muted {
    color:#94a3b8;
    font-size:12px;
}

</style>

<div class="nc-header">
    <div class="nc-title">NOOR CYBER WORLD</div>
    <div class="nc-main-title">CUSTOMERS MANAGEMENT SYSTEM</div>
    <div class="nc-sub">
        DIGITAL SERVICE • CUSTOMER RECORD • SMART MANAGEMENT
    </div>
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# EMPTY DATAFRAME
# ============================================================

def empty_df():
    return pd.DataFrame(columns=CUSTOMER_COLUMNS)


# ============================================================
# CLEAN CUSTOMER DATA
# ============================================================

def clean_df(df):

    if df is None or df.empty:
        return empty_df()

    df = df.copy()

    for col in CUSTOMER_COLUMNS:

        if col not in df.columns:

            if col in ["amount", "net_amount", "cash", "credit"]:
                df[col] = 0
            else:
                df[col] = ""

    # Text columns
    for col in ["name", "mobile", "service", "expiry"]:
        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Date
    raw_date = (
        df["created_at"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    parsed = pd.to_datetime(
        raw_date,
        errors="coerce"
    )

    df["created_at"] = parsed.dt.strftime("%Y-%m-%d")

    df.loc[
        parsed.isna(),
        "created_at"
    ] = raw_date[parsed.isna()]

    # Numeric
    for col in ["amount", "net_amount", "cash", "credit"]:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    return df[CUSTOMER_COLUMNS]


# ============================================================
# FETCH CUSTOMER RECORDS
# ============================================================

@st.cache_data(ttl=5)
def fetch_sheet_records():

    try:

        response = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_records",
                "t": int(datetime.now().timestamp())
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
# FETCH EXPENSES
# ============================================================

@st.cache_data(ttl=5)
def fetch_expenses():

    try:

        response = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_expenses",
                "t": int(datetime.now().timestamp())
            },
            timeout=20
        )

        if response.status_code != 200:
            return pd.DataFrame(
                columns=[
                    "created_at",
                    "title",
                    "amount",
                    "_row_number"
                ]
            )

        data = response.json()

        if not isinstance(data, list):
            return pd.DataFrame(
                columns=[
                    "created_at",
                    "title",
                    "amount",
                    "_row_number"
                ]
            )

        df = pd.DataFrame(data)

        if df.empty:
            return pd.DataFrame(
                columns=[
                    "created_at",
                    "title",
                    "amount",
                    "_row_number"
                ]
            )

        for col in [
            "created_at",
            "title",
            "amount",
            "_row_number"
        ]:

            if col not in df.columns:
                df[col] = ""

        df["created_at"] = (
            df["created_at"]
            .fillna("")
            .astype(str)
        )

        df["title"] = (
            df["title"]
            .fillna("")
            .astype(str)
        )

        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce"
        ).fillna(0)

        return df[
            [
                "created_at",
                "title",
                "amount",
                "_row_number"
            ]
        ]

    except Exception:

        return pd.DataFrame(
            columns=[
                "created_at",
                "title",
                "amount",
                "_row_number"
            ]
        )


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
            timeout=20
        )

        try:

            data = response.json()

            return (
                bool(data.get("success")),
                str(
                    data.get(
                        "message",
                        data.get(
                            "error",
                            "Operation failed"
                        )
                    )
                )
            )

        except Exception:

            if response.status_code == 200:
                return True, "Success"

            return False, "Server error"

    except Exception as e:

        return False, str(e)


# ============================================================
# LOAD DATA
# ============================================================

df_all = fetch_sheet_records()
expenses_df = fetch_expenses()


# ============================================================
# MOBILE → NAME
# ============================================================

mobile_to_name_map = {}

if not df_all.empty:

    for _, row in df_all.iterrows():

        mobile = str(row["mobile"]).strip()
        name = str(row["name"]).strip()

        if mobile and name:
            mobile_to_name_map[mobile] = name


# ============================================================
# DATE MASK HELPER
# ============================================================

def date_mask_for(df, selected_date):

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
        dates.dt.strftime("%Y-%m-%d")
        == selected_date.strftime("%Y-%m-%d")
    )


# ============================================================
# TOP STATISTICS
# ============================================================

today = today_ist()

today_mask = date_mask_for(
    df_all,
    today
)

month_str = today.strftime("%Y-%m")
year_str = today.strftime("%Y")

if not df_all.empty:

    dates = pd.to_datetime(
        df_all["created_at"],
        errors="coerce"
    )

    month_mask = (
        dates.dt.strftime("%Y-%m")
        == month_str
    )

    year_mask = (
        dates.dt.strftime("%Y")
        == year_str
    )

else:

    month_mask = pd.Series(
        dtype=bool,
        index=df_all.index
    )

    year_mask = pd.Series(
        dtype=bool,
        index=df_all.index
    )


def sum_col(mask, col):

    if df_all.empty:
        return 0

    return int(
        df_all.loc[
            mask,
            col
        ].sum()
    )


today_gross = sum_col(today_mask, "amount")
today_cash = sum_col(today_mask, "cash")
today_credit = sum_col(today_mask, "credit")
today_net = sum_col(today_mask, "net_amount")

month_gross = sum_col(month_mask, "amount")
month_cash = sum_col(month_mask, "cash")
month_credit = sum_col(month_mask, "credit")
month_net = sum_col(month_mask, "net_amount")

year_gross = sum_col(year_mask, "amount")
year_cash = sum_col(year_mask, "cash")
year_credit = sum_col(year_mask, "credit")
year_net = sum_col(year_mask, "net_amount")


# ============================================================
# TODAY EXPENSES
# ============================================================

today_expense_mask = date_mask_for(
    expenses_df,
    today
)

today_expenses_df = (
    expenses_df[today_expense_mask].copy()
    if not expenses_df.empty
    else expenses_df.copy()
)

today_expenses = int(
    today_expenses_df["amount"].sum()
    if not today_expenses_df.empty
    else 0
)

today_actual_profit = today_net - today_expenses


# ============================================================
# TOP DAILY COLLECTION
# ============================================================

st.markdown(
    f"""
    <div class="dashboard-green">

        <div class="dashboard-title">
            📊 DAILY COLLECTION
        </div>

        <span class="small-muted">
            Today • {today.strftime("%d-%m-%Y")}
        </span>

        <br><br>

        💰 Total:
        <b style="color:#22d3ee;">
            ₹ {today_gross:,}
        </b>

        &nbsp;&nbsp; | &nbsp;&nbsp;

        💵 Cash:
        <b style="color:#22c55e;">
            ₹ {today_cash:,}
        </b>

        &nbsp;&nbsp; | &nbsp;&nbsp;

        🔴 Credit:
        <b style="color:#ef4444;">
            ₹ {today_credit:,}
        </b>

        &nbsp;&nbsp; | &nbsp;&nbsp;

        📈 Net:
        <b style="color:#22c55e;">
            ₹ {today_net:,}
        </b>

        &nbsp;&nbsp; | &nbsp;&nbsp;

        💸 Expense:
        <b style="color:#ef4444;">
            ₹ {today_expenses:,}
        </b>

        &nbsp;&nbsp; | &nbsp;&nbsp;

        🟢 Actual:
        <b style="color:#22c55e;">
            ₹ {today_actual_profit:,}
        </b>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MONTH / YEAR
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "TODAY COLLECTION",
        f"₹ {today_gross:,}"
    )

with c2:
    st.metric(
        "TODAY CASH",
        f"₹ {today_cash:,}"
    )

with c3:
    st.metric(
        "TODAY CREDIT",
        f"₹ {today_credit:,}"
    )

with c4:
    st.metric(
        "TODAY NET PROFIT",
        f"₹ {today_net:,}"
    )


# ============================================================
# DATE SELECTOR
# ============================================================

st.markdown("---")

p_col, d_col, n_col = st.columns([1, 4, 1])

with p_col:

    if st.button(
        "❮ PREVIOUS DAY",
        use_container_width=True
    ):

        st.session_state.selected_date -= timedelta(days=1)
        st.rerun()


with d_col:

    picked = st.date_input(
        "Working Date",
        value=st.session_state.selected_date,
        label_visibility="collapsed"
    )

    if picked != st.session_state.selected_date:

        st.session_state.selected_date = picked
        st.rerun()


with n_col:

    if st.button(
        "NEXT DAY ❯",
        use_container_width=True
    ):

        st.session_state.selected_date += timedelta(days=1)
        st.rerun()


selected_date = st.session_state.selected_date
selected_date_str = selected_date.strftime("%Y-%m-%d")


day_mask = date_mask_for(
    df_all,
    selected_date
)

day_df = (
    df_all[day_mask].copy()
    if not df_all.empty
    else empty_df()
)

selected_expense_mask = date_mask_for(
    expenses_df,
    selected_date
)

selected_expenses_df = (
    expenses_df[selected_expense_mask].copy()
    if not expenses_df.empty
    else expenses_df.copy()
)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 TODAY'S ENTRIES",
    "🔴 CREDIT COLLECTION",
    "🔔 RENEWAL ALERTS",
    "💸 SHOP EXPENSES",
    "📂 RECORDS & SEARCH"
])


# ============================================================
# TAB 1 — TODAY'S ENTRIES
# ============================================================

with tab1:

    st.markdown(
        f"""
        <div class="nc-section">
            🟢 ENTRIES FOR {selected_date.strftime("%d-%m-%Y")}
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------
    # DAY SUMMARY
    # -----------------------------------------------

    if day_df.empty:

        total_gross = 0
        total_net = 0
        cash_sum = 0
        credit_sum = 0

    else:

        total_gross = int(day_df["amount"].sum())
        total_net = int(day_df["net_amount"].sum())
        cash_sum = int(day_df["cash"].sum())
        credit_sum = int(day_df["credit"].sum())

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "TOTAL COLLECTION",
        f"₹ {total_gross:,}"
    )

    m2.metric(
        "CASH RECEIVED",
        f"₹ {cash_sum:,}"
    )

    m3.metric(
        "PENDING CREDIT",
        f"₹ {credit_sum:,}"
    )

    m4.metric(
        "NET PROFIT",
        f"₹ {total_net:,}"
    )

    st.markdown("---")

    # -----------------------------------------------
    # TODAY'S CUSTOMER ENTRIES
    # -----------------------------------------------

    st.markdown(
        "### 🟢 Today's Entries"
    )

    if day_df.empty:

        st.info(
            "No customer entries for this date."
        )

    else:

        display_df = day_df[
            [
                "created_at",
                "name",
                "mobile",
                "service",
                "amount",
                "net_amount",
                "cash",
                "credit",
                "expiry"
            ]
        ].copy()

        display_df.columns = [
            "Date",
            "Customer",
            "Mobile",
            "Service",
            "Total",
            "Net",
            "Cash",
            "Credit",
            "Expiry"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Total": st.column_config.NumberColumn(
                    format="₹ %d"
                ),
                "Net": st.column_config.NumberColumn(
                    format="₹ %d"
                ),
                "Cash": st.column_config.NumberColumn(
                    format="₹ %d"
                ),
                "Credit": st.column_config.NumberColumn(
                    format="₹ %d"
                )
            }
        )

    # -----------------------------------------------
    # TODAY'S EXPENSES
    # -----------------------------------------------

    st.markdown("---")

    st.markdown(
        "### 🔴 Today's Expenses"
    )

    if selected_expenses_df.empty:

        st.info(
            "No expenses for this date."
        )

    else:

        expense_display = selected_expenses_df[
            [
                "created_at",
                "title",
                "amount"
            ]
        ].copy()

        expense_display.columns = [
            "Date",
            "Expense",
            "Amount"
        ]

        st.dataframe(
            expense_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount": st.column_config.NumberColumn(
                    format="₹ %d"
                )
            }
        )

        selected_total_expense = int(
            selected_expenses_df["amount"].sum()
        )

        st.error(
            f"🔴 Total Expenses: ₹ {selected_total_expense:,}"
        )

    # -----------------------------------------------
    # ADD / EDIT ENTRY
    # -----------------------------------------------

    st.markdown("---")

    is_editing = (
        st.session_state.editing_row is not None
    )

    st.markdown(
        f"""
        <div class="nc-section">
            {"✏️ EDIT CUSTOMER ENTRY" if is_editing else "➕ ADD NEW CUSTOMER ENTRY"}
        </div>
        """,
        unsafe_allow_html=True
    )

    edit_data = (
        st.session_state.editing_row
        or {}
    )

    left, right = st.columns(2)

    # -----------------------------------------------
    # LEFT
    # -----------------------------------------------

    with left:

        mobile_input = st.text_input(
            "Mobile Number *",
            value=str(
                edit_data.get(
                    "mobile",
                    ""
                )
            ),
            key="input_mobile"
        )

        clean_mobile = mobile_input.strip()

        auto_name = ""

        if (
            clean_mobile in mobile_to_name_map
            and not is_editing
        ):

            auto_name = mobile_to_name_map[
                clean_mobile
            ]

            st.success(
                f"Existing Customer: {auto_name}"
            )

        default_name = (
            str(edit_data.get("name", ""))
            if is_editing
            else auto_name
        )

        name_input = st.text_input(
            "Customer Name *",
            value=default_name,
            key="input_customer_name"
        )

        curr_serv = str(
            edit_data.get(
                "service",
                SERVICES[0]
            )
        )

        if curr_serv in SERVICES:
            service_index = SERVICES.index(
                curr_serv
            )
        else:
            service_index = SERVICES.index(
                "Other"
            )

        service_selected = st.selectbox(
            "Service *",
            SERVICES,
            index=service_index,
            key="input_service"
        )

        if service_selected == "Other":

            custom_service_input = st.text_input(
                "Custom Service Name *",
                value=(
                    curr_serv
                    if curr_serv not in SERVICES
                    else ""
                ),
                key="input_custom_service"
            )

        else:

            custom_service_input = ""

    # -----------------------------------------------
    # RIGHT
    # -----------------------------------------------

    with right:

        amount = st.number_input(
            "Total Fee / Gross Amount (₹) *",
            min_value=0,
            step=10,
            value=int(
                float(
                    edit_data.get(
                        "amount",
                        0
                    )
                )
            ),
            key="input_amount"
        )

        net_amount = st.number_input(
            "Net Income / Profit (₹) *",
            min_value=0,
            step=10,
            value=int(
                float(
                    edit_data.get(
                        "net_amount",
                        0
                    )
                )
            ),
            key="input_net"
        )

        existing_credit = float(
            edit_data.get(
                "credit",
                0
            )
        )

        default_payment_index = (
            1
            if existing_credit > 0
            else 0
        )

        payment_choice = st.radio(
            "Payment Type *",
            [
                "💵 Cash",
                "🔴 Credit"
            ],
            index=default_payment_index,
            horizontal=True,
            key="input_payment"
        )

        if payment_choice == "🔴 Credit":

            calculated_cash = 0
            calculated_credit = int(amount)

        else:

            calculated_cash = int(amount)
            calculated_credit = 0

        st.markdown(
            f"""
            <div class="dashboard-green">

            <b>PAYMENT SPLIT</b><br><br>

            💵 Cash:
            <b>₹ {calculated_cash:,}</b>

            &nbsp;&nbsp;&nbsp;

            🔴 Credit:
            <b>₹ {calculated_credit:,}</b>

            </div>
            """,
            unsafe_allow_html=True
        )

        existing_expiry = str(
            edit_data.get(
                "expiry",
                "N/A"
            )
        )

        has_expiry = st.checkbox(
            "Requires Renewal / Validity?",
            value=(
                existing_expiry not in [
                    "",
                    "N/A"
                ]
            ),
            key="input_has_expiry"
        )

        validity_unit = st.selectbox(
            "Validity Unit",
            [
                "Days",
                "Months",
                "Years"
            ],
            index=1,
            key="input_validity_unit"
        )

        validity_value = st.number_input(
            "Validity Duration",
            min_value=1,
            value=1,
            step=1,
            key="input_validity_value"
        )

    # -----------------------------------------------
    # SAVE / CANCEL
    # -----------------------------------------------

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
                    "Please enter customer name."
                )
                st.stop()

            if not mobile_input.strip():
                st.error(
                    "Please enter mobile number."
                )
                st.stop()

            # SERVICE
            final_service = service_selected

            if service_selected == "Other":

                if not custom_service_input.strip():

                    st.error(
                        "Please enter custom service name."
                    )
                    st.stop()

                final_service = (
                    custom_service_input.strip()
                )

                if (
                    final_service
                    not in st.session_state.custom_services
                ):

                    st.session_state.custom_services.append(
                        final_service
                    )

            # EXPIRY
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

            # PAYMENT
            if payment_choice == "🔴 Credit":

                final_cash = 0
                final_credit = int(amount)

            else:

                final_cash = int(amount)
                final_credit = 0

            # PAYLOAD
            payload = {

                "action": (
                    "edit"
                    if is_editing
                    else "add"
                ),

                "created_at": selected_date_str,

                "name": name_input.strip(),

                "mobile": mobile_input.strip(),

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

                "expiry": expiry,

                "row_number": int(
                    edit_data.get(
                        "_row_number",
                        0
                    )
                )
            }

            with st.spinner(
                "Saving..."
            ):

                ok, msg = api_post(
                    payload
                )

            if ok:

                st.session_state.editing_row = None

                fetch_sheet_records.clear()
                fetch_expenses.clear()

                st.session_state.success_message = (
                    "Entry saved successfully!"
                )

                st.session_state.last_saved_wa = (
                    "https://wa.me/91"
                    + mobile_input.strip()
                    + "?text="
                    + quote(
                        f"Dear {name_input.strip()}, "
                        f"Thank you for choosing NOOR CYBER WORLD "
                        f"for {final_service}! "
                        f"Total Amount: Rs.{int(amount)}. "
                        f"We are happy to serve you."
                    )
                )

                st.rerun()

            else:

                st.error(
                    f"Failed: {msg}"
                )

    with cancel_col:

        if is_editing:

            if st.button(
                "❌ CANCEL EDIT",
                use_container_width=True
            ):

                st.session_state.editing_row = None
                st.rerun()

    # -----------------------------------------------
    # EDIT / DELETE TABLE
    # -----------------------------------------------

    if not day_df.empty:

        st.markdown("---")
        st.markdown("### ⚙️ Manage Today's Entries")

        for _, row in day_df.iterrows():

            ec1, ec2, ec3, ec4 = st.columns(
                [3, 3, 1, 1]
            )

            with ec1:
                st.write(
                    f"**{row['name']}**"
                )

            with ec2:
                st.write(
                    str(row["service"])
                )

            with ec3:

                if st.button(
                    "✏️",
                    key=f"edit_today_{row['_row_number']}",
                    help="Edit"
                ):

                    st.session_state.editing_row = (
                        row.to_dict()
                    )

                    st.rerun()

            with ec4:

                if st.button(
                    "🗑️",
                    key=f"delete_today_{row['_row_number']}",
                    help="Delete"
                ):

                    ok, msg = api_post({
                        "action": "delete",
                        "row_number": int(
                            row["_row_number"]
                        )
                    })

                    if ok:

                        fetch_sheet_records.clear()

                        st.success(
                            "Deleted."
                        )

                        st.rerun()

                    else:

                        st.error(msg)


# ============================================================
# TAB 2 — CREDIT COLLECTION
# ============================================================

with tab2:

    st.markdown(
        "<div class='nc-section'>🔴 PENDING CREDIT / UDHARI</div>",
        unsafe_allow_html=True
    )

    if df_all.empty:

        credit_df = empty_df()

    else:

        credit_df = df_all[
            df_all["credit"] > 0
        ].copy()

    if credit_df.empty:

        st.success(
            "🎉 No pending credit!"
        )

    else:

        total_pending = int(
            credit_df["credit"].sum()
        )

        st.error(
            f"⚠️ TOTAL PENDING CREDIT: ₹ {total_pending:,}"
        )

        st.dataframe(
            credit_df[
                [
                    "created_at",
                    "name",
                    "mobile",
                    "service",
                    "credit"
                ]
            ].rename(
                columns={
                    "created_at": "Date",
                    "name": "Customer",
                    "mobile": "Mobile",
                    "service": "Service",
                    "credit": "Pending Credit"
                }
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Pending Credit":
                    st.column_config.NumberColumn(
                        format="₹ %d"
                    )
            }
        )

        st.markdown("---")

        for _, row in credit_df.iterrows():

            c1, c2, c3 = st.columns(
                [5, 2, 2]
            )

            with c1:

                st.markdown(
                    f"""
                    <div class="nc-card-red">

                    <b>🔴 {row['name']}</b>
                    &nbsp; ({row['mobile']})

                    <br>

                    {row['service']}

                    <br>

                    Pending:
                    <b style="color:#ef4444;">
                    ₹ {int(row['credit']):,}
                    </b>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c2:

                msg = (
                    f"Hello {row['name']}, "
                    f"your payment of Rs."
                    f"{int(row['credit'])} "
                    f"for {row['service']} "
                    f"is pending. "
                    f"Please clear your balance. "
                    f"Thank you - NOOR CYBER WORLD."
                )

                wa = (
                    "https://wa.me/91"
                    + str(row["mobile"]).strip()
                    + "?text="
                    + quote(msg)
                )

                st.link_button(
                    "💬 REMINDER",
                    wa,
                    use_container_width=True
                )

            with c3:

                if st.button(
                    "💵 RECEIVED",
                    key=f"receive_{row['_row_number']}",
                    use_container_width=True
                ):

                    received = int(
                        row["credit"]
                    )

                    ok, msg = api_post({

                        "action":
                            "credit_to_cash",

                        "row_number":
                            int(row["_row_number"]),

                        "cash":
                            str(
                                int(row["cash"])
                                + received
                            ),

                        "credit":
                            "0"
                    })

                    if ok:

                        fetch_sheet_records.clear()

                        st.success(
                            f"₹ {received:,} received."
                        )

                        st.rerun()

                    else:

                        st.error(msg)


# ============================================================
# TAB 3 — RENEWAL
# ============================================================

with tab3:

    st.markdown(
        "<div class='nc-section'>🔔 RENEWAL ALERTS — NEXT 15 DAYS</div>",
        unsafe_allow_html=True
    )

    renewals = []

    if not df_all.empty:

        for _, row in df_all.iterrows():

            exp = str(
                row["expiry"]
            ).strip()

            if exp and exp != "N/A":

                try:

                    exp_date = datetime.strptime(
                        exp[:10],
                        "%Y-%m-%d"
                    ).date()

                    days_left = (
                        exp_date - today
                    ).days

                    if 0 <= days_left <= 15:

                        renewals.append(
                            (
                                row,
                                exp_date,
                                days_left
                            )
                        )

                except Exception:
                    pass

    if not renewals:

        st.success(
            "🎉 No renewals due in next 15 days."
        )

    else:

        st.warning(
            f"⚠️ {len(renewals)} renewal(s) pending."
        )

        for row, exp_date, days_left in renewals:

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
                <b>{exp_date.strftime("%d-%m-%Y")}</b>

                &nbsp; | &nbsp;

                {days_left} days remaining

                </div>
                """,
                unsafe_allow_html=True
            )

            msg = (
                f"Hello {row['name']}, "
                f"your {row['service']} "
                f"is expiring on "
                f"{exp_date.strftime('%d-%m-%Y')}. "
                f"Please visit NOOR CYBER WORLD "
                f"for renewal."
            )

            wa = (
                "https://wa.me/91"
                + str(row["mobile"]).strip()
                + "?text="
                + quote(msg)
            )

            st.link_button(
                "💬 SEND RENEWAL MESSAGE",
                wa
            )


# ============================================================
# TAB 4 — EXPENSES
# ============================================================

with tab4:

    st.markdown(
        "<div class='nc-section'>💸 SHOP EXPENSES & ACTUAL PROFIT</div>",
        unsafe_allow_html=True
    )

    left, right = st.columns(2)

    with left:

        st.markdown(
            "### ➕ Add Expense"
        )

        exp_title = st.text_input(
            "Expense Title",
            placeholder="Rent / Paper / Tea / Electricity...",
            key="expense_title"
        )

        exp_amount = st.number_input(
            "Expense Amount (₹)",
            min_value=0,
            step=10,
            key="expense_amount"
        )

        if st.button(
            "💾 SAVE EXPENSE",
            type="primary",
            use_container_width=True
        ):

            if not exp_title.strip():

                st.error(
                    "Enter expense title."
                )

            elif exp_amount <= 0:

                st.error(
                    "Enter expense amount."
                )

            else:

                ok, msg = api_post({

                    "action":
                        "add_expense",

                    "created_at":
                        selected_date_str,

                    "title":
                        exp_title.strip(),

                    "amount":
                        str(
                            int(exp_amount)
                        )
                })

                if ok:

                    fetch_expenses.clear()

                    st.success(
                        "Expense saved!"
                    )

                    st.rerun()

                else:

                    st.error(msg)

    with right:

        selected_expense_total = int(
            selected_expenses_df["amount"].sum()
            if not selected_expenses_df.empty
            else 0
        )

        selected_net = int(
            day_df["net_amount"].sum()
            if not day_df.empty
            else 0
        )

        actual_profit = (
            selected_net
            - selected_expense_total
        )

        st.markdown(
            f"""
            <div class="dashboard-red">

            <div class="dashboard-title">
                🔴 EXPENSE SUMMARY
            </div>

            Date:
            <b>{selected_date.strftime("%d-%m-%Y")}</b>

            <br><br>

            Net Income:
            <b>₹ {selected_net:,}</b>

            <br>

            Expenses:
            <b style="color:#ef4444;">
            ₹ {selected_expense_total:,}
            </b>

            <br>

            Actual Profit:
            <b style="color:#22c55e;">
            ₹ {actual_profit:,}
            </b>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown(
        f"### 🔴 Expenses for {selected_date.strftime('%d-%m-%Y')}"
    )

    if selected_expenses_df.empty:

        st.info(
            "No expenses recorded."
        )

    else:

        expense_table = selected_expenses_df[
            [
                "created_at",
                "title",
                "amount"
            ]
        ].copy()

        expense_table.columns = [
            "Date",
            "Expense",
            "Amount"
        ]

        st.dataframe(
            expense_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount":
                    st.column_config.NumberColumn(
                        format="₹ %d"
                    )
            }
        )

        st.markdown(
            f"""
            <div class="dashboard-red">
                🔴 <b>Total Expenses:
                ₹ {selected_expense_total:,}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        for _, row in selected_expenses_df.iterrows():

            ec1, ec2, ec3 = st.columns(
                [5, 2, 1]
            )

            with ec1:
                st.write(
                    f"🔴 **{row['title']}**"
                )

            with ec2:
                st.write(
                    f"₹ {int(row['amount']):,}"
                )

            with ec3:

                if st.button(
                    "🗑️",
                    key=f"expense_delete_{row['_row_number']}"
                ):

                    ok, msg = api_post({

                        "action":
                            "delete_expense",

                        "row_number":
                            int(
                                row["_row_number"]
                            )
                    })

                    if ok:

                        fetch_expenses.clear()

                        st.rerun()

                    else:

                        st.error(msg)


# ============================================================
# TAB 5 — RECORDS
# ============================================================

with tab5:

    st.markdown(
        "<div class='nc-section'>📂 ALL CUSTOMER RECORDS</div>",
        unsafe_allow_html=True
    )

    if df_all.empty:

        st.info(
            "No customer records available."
        )

    else:

        search_query = st.text_input(
            "🔍 Search Name / Mobile / Service",
            key="records_search"
        )

        if search_query.strip():

            q = search_query.strip().lower()

            filtered_df = df_all[
                df_all["name"]
                .str.lower()
                .str.contains(q, na=False)
                |
                df_all["mobile"]
                .str.lower()
                .str.contains(q, na=False)
                |
                df_all["service"]
                .str.lower()
                .str.contains(q, na=False)
            ].copy()

        else:

            filtered_df = df_all.copy()

        st.caption(
            f"Showing {len(filtered_df)} records"
        )

        # -----------------------------------------------
        # TABLE
        # -----------------------------------------------

        records_table = filtered_df[
            [
                "created_at",
                "name",
                "mobile",
                "service",
                "amount",
                "net_amount",
                "cash",
                "credit",
                "expiry"
            ]
        ].copy()

        records_table.columns = [
            "Date",
            "Customer",
            "Mobile",
            "Service",
            "Total",
            "Net",
            "Cash",
            "Credit",
            "Expiry"
        ]

        st.dataframe(
            records_table,
            use_container_width=True,
            hide_index=True,
            height=550,
            column_config={

                "Date":
                    st.column_config.TextColumn(
                        width="small"
                    ),

                "Customer":
                    st.column_config.TextColumn(
                        width="medium"
                    ),

                "Mobile":
                    st.column_config.TextColumn(
                        width="medium"
                    ),

                "Service":
                    st.column_config.TextColumn(
                        width="large"
                    ),

                "Total":
                    st.column_config.NumberColumn(
                        format="₹ %d"
                    ),

                "Net":
                    st.column_config.NumberColumn(
                        format="₹ %d"
                    ),

                "Cash":
                    st.column_config.NumberColumn(
                        format="₹ %d"
                    ),

                "Credit":
                    st.column_config.NumberColumn(
                        format="₹ %d"
                    ),

                "Expiry":
                    st.column_config.TextColumn(
                        width="small"
                    )
            }
        )

        # -----------------------------------------------
        # EDIT / DELETE
        # -----------------------------------------------

        st.markdown("---")

        st.markdown(
            "### ⚙️ Manage Record"
        )

        selected_row_number = st.selectbox(
            "Select Customer",
            filtered_df.index,
            format_func=lambda x:
                f"{filtered_df.loc[x, 'name']} | "
                f"{filtered_df.loc[x, 'mobile']} | "
                f"{filtered_df.loc[x, 'created_at']}",
            key="manage_record_select"
        )

        selected_row = filtered_df.loc[
            selected_row_number
        ]

        mc1, mc2 = st.columns(2)

        with mc1:

            if st.button(
                "✏️ EDIT SELECTED RECORD",
                use_container_width=True
            ):

                st.session_state.editing_row = (
                    selected_row.to_dict()
                )

                st.session_state.selected_date = (
                    datetime.strptime(
                        str(
                            selected_row[
                                "created_at"
                            ]
                        )[:10],
                        "%Y-%m-%d"
                    ).date()
                )

                st.info(
                    "Record selected for editing. "
                    "Open TODAY'S ENTRIES tab."
                )

        with mc2:

            if st.button(
                "🗑️ DELETE SELECTED RECORD",
                use_container_width=True
            ):

                ok, msg = api_post({

                    "action":
                        "delete",

                    "row_number":
                        int(
                            selected_row[
                                "_row_number"
                            ]
                        )
                })

                if ok:

                    fetch_sheet_records.clear()

                    st.success(
                        "Record deleted."
                    )

                    st.rerun()

                else:

                    st.error(msg)

        # -----------------------------------------------
        # DOWNLOAD
        # -----------------------------------------------

        st.markdown("---")

        export_df = filtered_df.drop(
            columns=["_row_number"],
            errors="ignore"
        )

        csv_data = export_df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "📥 DOWNLOAD CSV",
            csv_data,
            file_name="NOOR_CYBER_WORLD_RECORDS.csv",
            mime="text/csv",
            use_container_width=True
        )


# ============================================================
# WHATSAPP AFTER SAVE
# ============================================================

if "last_saved_wa" in st.session_state:

    st.markdown("---")

    st.success(
        "🎉 Entry saved successfully!"
    )

    st.link_button(
        "💬 SEND THANK YOU WHATSAPP",
        st.session_state.last_saved_wa,
        use_container_width=True
    )


# ============================================================
# SUCCESS TOAST
# ============================================================

if "success_message" in st.session_state:

    st.toast(
        st.session_state.pop(
            "success_message"
        ),
        icon="✅"
    )
