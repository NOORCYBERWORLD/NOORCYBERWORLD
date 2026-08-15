import streamlit as st
import pandas as pd
import requests
import json
import io
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import quote

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# ============================================================
# PAGE CONFIG
# ============================================================



# ============================================================
# TIMEZONE
# ============================================================

IST = timezone(timedelta(hours=5, minutes=30))


def today_ist():
    return datetime.now(IST).date()


def today_str():
    return today_ist().strftime("%Y-%m-%d")


# ============================================================
# GOOGLE APPS SCRIPT URL
# ============================================================

WEB_APP_URL = (
    "https://script.google.com/macros/s/AKfycbwSipN_etRHmOKXczikdg1gwzBvksliKCLQ0NYIJX9BbCGcyalc8H14aMTo_mNAbytK/exec"
)


# ============================================================
# COLUMNS
# ============================================================

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


if "selected_date" not in st.session_state:
    st.session_state.selected_date = today_ist()


if "editing_customer" not in st.session_state:
    st.session_state.editing_customer = None


if "last_saved_wa" not in st.session_state:
    st.session_state.last_saved_wa = None


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


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&display=swap');

:root {
    --green:#22c55e;
    --red:#ef4444;
    --cyan:#22d3ee;
    --blue:#38bdf8;
    --dark:#0f172a;
}

.stApp {
    background:
        linear-gradient(
            115deg,
            rgba(5,8,15,.97),
            rgba(7,18,32,.92)
        ),
        url("https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=2400&q=80")
        center/cover fixed no-repeat;
    color:#f8fafc;
    font-family:'Inter',sans-serif;
}

.block-container {
    max-width:1500px;
    padding-top:1rem;
    padding-bottom:3rem;
}

.nc-header {
    text-align:center;
    padding:12px 10px 18px;
    margin-bottom:5px;
}

.nc-title {
    font-family:'Orbitron',Arial,sans-serif;
    font-size:38px;
    font-weight:800;
    letter-spacing:4px;
    line-height:1.25;
    color:#ffffff;
    text-shadow:
        0 0 8px rgba(34,211,238,.75),
        0 0 22px rgba(34,211,238,.35);
    margin:0;
}

.nc-main-title {
    font-family:'Orbitron',Arial,sans-serif;
    font-size:20px;
    font-weight:700;
    letter-spacing:2px;
    color:#22d3ee;
    margin-top:4px;
}

.nc-sub {
    font-size:11px;
    letter-spacing:1.5px;
    color:#cbd5e1;
    margin-top:4px;
}

.nc-section {
    font-family:'Orbitron',sans-serif;
    font-size:18px;
    font-weight:700;
    color:#e2e8f0;
    margin:8px 0 14px;
}

div[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            rgba(15,23,42,.95),
            rgba(30,41,59,.82)
        );
    border:1px solid rgba(96,165,250,.25);
    border-radius:16px;
    padding:14px;
    box-shadow:0 10px 30px rgba(0,0,0,.25);
}

div[data-testid="stMetricLabel"] {
    color:#cbd5e1;
}

div[data-testid="stMetricValue"] {
    font-weight:800;
}

.nc-card-green {
    background:
        linear-gradient(
            145deg,
            rgba(22,101,52,.35),
            rgba(15,23,42,.88)
        );
    border:1px solid rgba(34,197,94,.45);
    border-left:5px solid #22c55e;
    border-radius:12px;
    padding:11px 14px;
    margin:5px 0;
}

.nc-card-red {
    background:
        linear-gradient(
            145deg,
            rgba(153,27,27,.35),
            rgba(15,23,42,.88)
        );
    border:1px solid rgba(239,68,68,.45);
    border-left:5px solid #ef4444;
    border-radius:12px;
    padding:11px 14px;
    margin:5px 0;
}

.nc-summary {
    background:rgba(15,23,42,.92);
    border:1px solid rgba(34,211,238,.28);
    border-radius:12px;
    padding:9px 14px;
    text-align:right;
    font-size:12px;
    line-height:1.7;
}

.nc-summary .value {
    font-weight:800;
    color:#22d3ee;
}

.nc-summary .profit {
    font-weight:800;
    color:#22c55e;
}

.nc-summary .credit {
    font-weight:800;
    color:#ef4444;
}

.expense-card {
    background:
        linear-gradient(
            145deg,
            rgba(127,29,29,.45),
            rgba(15,23,42,.9)
        );
    border:1px solid rgba(239,68,68,.5);
    border-left:5px solid #ef4444;
    border-radius:10px;
    padding:10px 14px;
    margin:5px 0;
}

</style>

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
# EMPTY DATAFRAME
# ============================================================

def empty_df():
    return pd.DataFrame(columns=COLUMNS)


# ============================================================
# CLEAN DATA
# ============================================================

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

    text_columns = [
        "name",
        "mobile",
        "service",
        "expiry"
    ]

    for col in text_columns:

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    raw = (
        df["created_at"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    parsed = pd.to_datetime(
        raw,
        errors="coerce"
    )

    df["created_at"] = parsed.dt.strftime(
        "%Y-%m-%d"
    )

    invalid = parsed.isna()

    df.loc[
        invalid,
        "created_at"
    ] = raw[invalid]

    # --------------------------------------------------------
    # NUMBERS
    # --------------------------------------------------------

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

    return df[COLUMNS]


# ============================================================
# FETCH CUSTOMERS
# ============================================================

@st.cache_data(ttl=3)
def fetch_sheet_records():

    try:

        response = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_records",
                "t": int(
                    datetime.now(IST).timestamp()
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
# FETCH EXPENSES
# ============================================================

@st.cache_data(ttl=3)
def fetch_expenses():

    try:

        response = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_expenses",
                "t": int(
                    datetime.now(IST).timestamp()
                )
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

        if "_row_number" not in df.columns:
            df["_row_number"] = 0

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

        return df

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

        if response.status_code != 200:
            return False, f"HTTP {response.status_code}"

        try:

            result = response.json()

            return (
                bool(result.get("success")),
                str(
                    result.get(
                        "message",
                        result.get(
                            "error",
                            "Operation failed"
                        )
                    )
                )
            )

        except Exception:

            return False, "Invalid server response."

    except Exception as e:

        return False, str(e)


# ============================================================
# REFRESH
# ============================================================

def refresh_data():

    fetch_sheet_records.clear()
    fetch_expenses.clear()


# ============================================================
# LOAD DATA
# ============================================================

df_all = fetch_sheet_records()
expenses_df = fetch_expenses()


# ============================================================
# MOBILE → NAME MAP
# ============================================================

mobile_to_name = {}

if not df_all.empty:

    for _, row in df_all.iterrows():

        mobile = str(
            row["mobile"]
        ).strip()

        name = str(
            row["name"]
        ).strip()

        if mobile and name:
            mobile_to_name[mobile] = name


# ============================================================
# DATE MASKS
# ============================================================

now = datetime.now(IST)

today_date = now.date()
today_date_str = today_date.strftime("%Y-%m-%d")
month_str = now.strftime("%Y-%m")
year_str = now.strftime("%Y")


if not df_all.empty:

    created = pd.to_datetime(
        df_all["created_at"],
        errors="coerce"
    )

    day_mask = (
        created.dt.strftime("%Y-%m-%d")
        == today_date_str
    )

    month_mask = (
        created.dt.strftime("%Y-%m")
        == month_str
    )

    year_mask = (
        created.dt.strftime("%Y")
        == year_str
    )

else:

    day_mask = pd.Series(
        dtype=bool
    )

    month_mask = pd.Series(
        dtype=bool
    )

    year_mask = pd.Series(
        dtype=bool
    )


# ============================================================
# TOP SUMMARY
# ============================================================

if not df_all.empty:

    today_net = df_all.loc[
        day_mask,
        "net_amount"
    ].sum()

    month_net = df_all.loc[
        month_mask,
        "net_amount"
    ].sum()

    year_net = df_all.loc[
        year_mask,
        "net_amount"
    ].sum()

    today_cash = df_all.loc[
        day_mask,
        "cash"
    ].sum()

    today_credit = df_all.loc[
        day_mask,
        "credit"
    ].sum()

else:

    today_net = 0
    month_net = 0
    year_net = 0
    today_cash = 0
    today_credit = 0


st.markdown(
    f"""
<div class="nc-summary">

    <b>📅 TODAY NET INCOME:</b>
    <span class="profit">₹ {today_net:,.0f}</span>
    &nbsp;&nbsp; | &nbsp;&nbsp;

    <b>🗓️ MONTH NET INCOME:</b>
    <span class="profit">₹ {month_net:,.0f}</span>
    &nbsp;&nbsp; | &nbsp;&nbsp;

    <b>📊 YEAR NET INCOME:</b>
    <span class="profit">₹ {year_net:,.0f}</span>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# SELECTED DAY DATA
# ============================================================

selected_date_str = (
    st.session_state.selected_date.strftime(
        "%Y-%m-%d"
    )
)

if not df_all.empty:

    selected_dates = pd.to_datetime(
        df_all["created_at"],
        errors="coerce"
    )

    selected_mask = (
        selected_dates.dt.strftime("%Y-%m-%d")
        == selected_date_str
    )

    day_df = df_all[
        selected_mask
    ].copy()

else:

    day_df = empty_df()


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

        st.session_state.selected_date -= timedelta(
            days=1
        )

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

        st.session_state.selected_date += timedelta(
            days=1
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


# ============================================================
# TAB 1
# ============================================================

with tab1:

    st.markdown(
        f"""
        <div class="nc-section">
            📋 Entries for
            {st.session_state.selected_date.strftime('%d-%m-%Y')}
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # DAY SUMMARY
    # --------------------------------------------------------

    if day_df.empty:

        total_gross = 0
        total_net = 0
        cash_sum = 0
        credit_sum = 0

    else:

        total_gross = int(
            day_df["amount"].sum()
        )

        total_net = int(
            day_df["net_amount"].sum()
        )

        cash_sum = int(
            day_df["cash"].sum()
        )

        credit_sum = int(
            day_df["credit"].sum()
        )


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


    # --------------------------------------------------------
    # TODAY / SELECTED DATE ENTRIES
    # --------------------------------------------------------

    if day_df.empty:

        st.info(
            "ℹ️ No entries recorded for this date."
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
            "Amount",
            "Net Profit",
            "Cash",
            "Credit",
            "Expiry"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount": st.column_config.NumberColumn(
                    "Amount",
                    format="₹ %d"
                ),
                "Net Profit": st.column_config.NumberColumn(
                    "Net Profit",
                    format="₹ %d"
                ),
                "Cash": st.column_config.NumberColumn(
                    "Cash",
                    format="₹ %d"
                ),
                "Credit": st.column_config.NumberColumn(
                    "Credit",
                    format="₹ %d"
                )
            }
        )


    st.markdown("---")


    # ========================================================
    # ADD / EDIT CUSTOMER
    # ========================================================

    is_editing = (
        st.session_state.editing_customer
        is not None
    )

    st.markdown(
        f"""
        <div class="nc-section">
            {
                "✏️ EDIT CUSTOMER ENTRY"
                if is_editing
                else "➕ ADD NEW CUSTOMER ENTRY"
            }
        </div>
        """,
        unsafe_allow_html=True
    )


    edit_data = (
        st.session_state.editing_customer
        or {}
    )


    left, right = st.columns(2)


    # --------------------------------------------------------
    # LEFT
    # --------------------------------------------------------

    with left:

        mobile_input = st.text_input(
            "Mobile Number *",
            value=str(
                edit_data.get(
                    "mobile",
                    ""
                )
            ),
            key="mobile_input"
        ).strip()


        # ----------------------------------------------------
        # AUTO CUSTOMER NAME
        # ----------------------------------------------------

        auto_name = mobile_to_name.get(
            mobile_input,
            ""
        )


        if is_editing:

            default_name = str(
                edit_data.get(
                    "name",
                    ""
                )
            )

        else:

            default_name = auto_name


        name_input = st.text_input(
            "Customer Name *",
            value=default_name,
            key=f"name_input_{mobile_input}_{is_editing}"
        )


        services = get_services()


        current_service = str(
            edit_data.get(
                "service",
                services[0]
            )
        )


        if current_service in services:

            service_index = services.index(
                current_service
            )

        else:

            service_index = services.index(
                "Other"
            )


        service_selected = st.selectbox(
            "Search / Select Service *",
            services,
            index=service_index,
            key="service_select"
        )


        if service_selected == "Other":

            custom_service = st.text_input(
                "Custom Service Name *",
                value=(
                    current_service
                    if current_service not in services
                    else ""
                ),
                key="custom_service"
            )

        else:

            custom_service = ""


    # --------------------------------------------------------
    # RIGHT
    # --------------------------------------------------------

    with right:

        amount = st.number_input(
            "Total Fee / Amount (₹) *",
            min_value=0,
            step=10,
            value=int(
                edit_data.get(
                    "amount",
                    0
                )
            ),
            key="amount_input"
        )


        net_amount = st.number_input(
            "Net Profit (₹) *",
            min_value=0,
            step=10,
            value=int(
                edit_data.get(
                    "net_amount",
                    0
                )
            ),
            key="net_amount_input"
        )


        existing_credit = float(
            edit_data.get(
                "credit",
                0
            )
        )


        if is_editing and existing_credit > 0:

            payment_index = 1

        else:

            payment_index = 0


        payment_choice = st.radio(
            "Payment Type *",
            [
                "💵 CASH",
                "🔴 CREDIT / UDHARI"
            ],
            index=payment_index,
            horizontal=True,
            key="payment_choice"
        )


        if "CREDIT" in payment_choice:

            calculated_cash = 0
            calculated_credit = int(amount)

        else:

            calculated_cash = int(amount)
            calculated_credit = 0


        st.info(
            f"""
**PAYMENT SPLIT**

💵 Cash: ₹ {calculated_cash:,}

🔴 Credit: ₹ {calculated_credit:,}
"""
        )


        existing_expiry = str(
            edit_data.get(
                "expiry",
                "N/A"
            )
        ).strip()


        has_expiry = st.checkbox(
            "Requires Renewal / Validity?",
            value=(
                existing_expiry
                not in ["", "N/A"]
            ),
            key="has_expiry"
        )


        validity_unit = st.selectbox(
            "Validity Unit",
            [
                "Days",
                "Months",
                "Years"
            ],
            index=1,
            key="validity_unit"
        )


        validity_value = st.number_input(
            "Validity Duration",
            min_value=1,
            value=1,
            step=1,
            key="validity_value"
        )


    # --------------------------------------------------------
    # SAVE / UPDATE
    # --------------------------------------------------------

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

            final_name = name_input.strip()
            final_mobile = mobile_input.strip()


            if not final_name or not final_mobile:

                st.error(
                    "Customer Name आणि Mobile Number आवश्यक आहेत."
                )

                st.stop()


            if amount <= 0:

                st.error(
                    "Amount ₹0 पेक्षा जास्त असावा."
                )

                st.stop()


            if net_amount < 0:

                st.error(
                    "Net Profit invalid आहे."
                )

                st.stop()


            # ------------------------------------------------
            # SERVICE
            # ------------------------------------------------

            if service_selected == "Other":

                if not custom_service.strip():

                    st.error(
                        "Custom Service Name द्या."
                    )

                    st.stop()


                final_service = custom_service.strip()


                if (
                    final_service
                    not in st.session_state.custom_services
                ):

                    st.session_state.custom_services.append(
                        final_service
                    )

            else:

                final_service = service_selected


            # ------------------------------------------------
            # EXPIRY
            # ------------------------------------------------

            expiry = "N/A"


            if has_expiry:

                base_date = (
                    st.session_state.selected_date
                )


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

            if "CREDIT" in payment_choice:

                final_cash = 0
                final_credit = int(amount)

            else:

                final_cash = int(amount)
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

                "name": final_name,

                "mobile": final_mobile,

                "service": final_service,

                "amount": int(amount),

                "net_amount": int(net_amount),

                "cash": final_cash,

                "credit": final_credit,

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

                ok, message = api_post(
                    payload
                )


            if ok:

                st.session_state.editing_customer = None

                refresh_data()

                thank_message = (
                    f"Dear {final_name}, "
                    f"Thank you for choosing "
                    f"NOOR CYBER WORLD for "
                    f"{final_service}! "
                    f"Total Amount: Rs.{int(amount)}. "
                    f"We are happy to serve you."
                )


                st.session_state.last_saved_wa = (
                    "https://wa.me/91"
                    + final_mobile
                    + "?text="
                    + quote(
                        thank_message
                    )
                )


                st.success(
                    "✅ Entry Saved Successfully!"
                )

                st.rerun()

            else:

                st.error(
                    f"Save failed: {message}"
                )


    with cancel_col:

        if is_editing:

            if st.button(
                "❌ CANCEL EDIT",
                use_container_width=True
            ):

                st.session_state.editing_customer = None

                st.rerun()


    # --------------------------------------------------------
    # WHATSAPP
    # --------------------------------------------------------

    if st.session_state.last_saved_wa:

        st.link_button(
            "💬 SEND THANK YOU WHATSAPP",
            st.session_state.last_saved_wa,
            use_container_width=True
        )


# ============================================================
# TAB 2 — CREDIT
# ============================================================

with tab2:

    st.markdown(
        """
        <div class="nc-section">
            🔴 PENDING CREDIT / UDHARI COLLECTION
        </div>
        """,
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

        pending_total = int(
            credit_df["credit"].sum()
        )


        st.error(
            f"⚠️ TOTAL PENDING CREDIT: ₹ {pending_total:,}"
        )


        st.markdown("---")


        for idx, row in credit_df.iterrows():

            info, reminder, paid = st.columns(
                [5, 2, 2]
            )


            with info:

                st.markdown(
                    f"""
                    <div class="nc-card-red">

                    <b>🔴 {row['name']}</b>
                    ({row['mobile']})

                    <br>

                    Service:
                    <b>{row['service']}</b>

                    <br>

                    Date:
                    {row['created_at']}

                    <br>

                    Pending Credit:
                    <b style="font-size:18px;color:#ef4444;">
                    ₹ {float(row['credit']):,.0f}
                    </b>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with reminder:

                message = (
                    f"Hello {row['name']}, "
                    f"your payment of Rs."
                    f"{int(row['credit'])} "
                    f"for {row['service']} "
                    f"is pending. "
                    f"Please clear your balance. "
                    f"Thank you - NOOR CYBER WORLD."
                )


                wa_url = (
                    "https://wa.me/91"
                    + str(row["mobile"]).strip()
                    + "?text="
                    + quote(message)
                )


                st.link_button(
                    "💬 SEND REMINDER",
                    wa_url,
                    use_container_width=True
                )


            with paid:

                if st.button(
                    "💵 CASH RECEIVED",
                    key=f"credit_cash_{row['_row_number']}",
                    use_container_width=True
                ):

                    payload = {

                        "action":
                            "credit_to_cash",

                        "row_number":
                            int(
                                row["_row_number"]
                            )

                    }


                    with st.spinner(
                        "Updating payment..."
                    ):

                        ok, message = api_post(
                            payload
                        )


                    if ok:

                        refresh_data()

                        st.success(
                            f"₹ {int(row['credit']):,} received from {row['name']}."
                        )

                        st.rerun()

                    else:

                        st.error(
                            message
                        )


# ============================================================
# TAB 3 — RENEWALS
# ============================================================

with tab3:

    st.markdown(
        """
        <div class="nc-section">
            🔔 RENEWAL ALERTS — NEXT 15 DAYS
        </div>
        """,
        unsafe_allow_html=True
    )


    renewals = []

    today = today_ist()


    if not df_all.empty:

        for _, row in df_all.iterrows():

            expiry = str(
                row["expiry"]
            ).strip()


            if not expiry or expiry == "N/A":
                continue


            try:

                expiry_date = datetime.strptime(
                    expiry[:10],
                    "%Y-%m-%d"
                ).date()


                days_left = (
                    expiry_date - today
                ).days


                if 0 <= days_left <= 15:

                    renewals.append(
                        (
                            row,
                            expiry_date,
                            days_left
                        )
                    )

            except Exception:

                continue


    if not renewals:

        st.success(
            "🎉 No renewals due in next 15 days."
        )

    else:

        st.warning(
            f"⚠️ {len(renewals)} renewal(s) pending."
        )


        for row, expiry_date, days_left in renewals:

            formatted = expiry_date.strftime(
                "%d-%m-%Y"
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
                <b>{formatted}</b>

                &nbsp; — &nbsp;

                {days_left} days remaining

                </div>
                """,
                unsafe_allow_html=True
            )


            message = (
                f"Hello {row['name']}, "
                f"your {row['service']} "
                f"is expiring on {formatted}. "
                f"Please visit NOOR CYBER WORLD "
                f"for renewal."
            )


            wa_url = (
                "https://wa.me/91"
                + str(row["mobile"]).strip()
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
            💸 SHOP EXPENSE & REAL PROFIT
        </div>
        """,
        unsafe_allow_html=True
    )


    exp_left, exp_right = st.columns(
        [1, 2]
    )


    with exp_left:

        st.subheader(
            "➕ Add Shop Expense"
        )


        expense_title = st.text_input(
            "Expense Title",
            placeholder="Paper, Rent, Tea, Electricity..."
        )


        expense_amount = st.number_input(
            "Expense Amount (₹)",
            min_value=0,
            step=10
        )


        if st.button(
            "💾 ADD EXPENSE",
            type="primary",
            use_container_width=True
        ):

            if not expense_title.strip():

                st.error(
                    "Expense title required."
                )

                st.stop()


            if expense_amount <= 0:

                st.error(
                    "Expense amount must be greater than zero."
                )

                st.stop()


            payload = {

                "action":
                    "add_expense",

                "created_at":
                    selected_date_str,

                "title":
                    expense_title.strip(),

                "amount":
                    int(expense_amount)

            }


            ok, message = api_post(
                payload
            )


            if ok:

                refresh_data()

                st.success(
                    "Expense added."
                )

                st.rerun()

            else:

                st.error(
                    message
                )


    with exp_right:

        st.subheader(
            f"📊 Expense Summary — {selected_date_str}"
        )


        if expenses_df.empty:

            today_expenses = expenses_df.copy()

        else:

            today_expenses = expenses_df[
                expenses_df["created_at"]
                == selected_date_str
            ].copy()


        total_expenses = int(
            today_expenses["amount"].sum()
            if not today_expenses.empty
            else 0
        )


        selected_net = int(
            day_df["net_amount"].sum()
            if not day_df.empty
            else 0
        )


        real_profit = (
            selected_net
            - total_expenses
        )


        e1, e2, e3 = st.columns(3)


        e1.metric(
            "NET PROFIT",
            f"₹ {selected_net:,}"
        )


        e2.metric(
            "EXPENSES",
            f"₹ {total_expenses:,}"
        )


        e3.metric(
            "REAL PROFIT",
            f"₹ {real_profit:,}"
        )


        st.markdown("---")


        if today_expenses.empty:

            st.info(
                "No expenses recorded for this date."
            )

        else:

            for _, exp in today_expenses.iterrows():

                c1, c2 = st.columns(
                    [5, 1]
                )


                with c1:

                    st.markdown(
                        f"""
                        <div class="expense-card">

                        🔴 <b>{exp['title']}</b>

                        &nbsp;&nbsp;

                        ₹ {int(exp['amount']):,}

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                with c2:

                    if st.button(
                        "🗑️",
                        key=f"expense_delete_{exp['_row_number']}",
                        use_container_width=True
                    ):

                        payload = {

                            "action":
                                "delete_expense",

                            "row_number":
                                int(
                                    exp["_row_number"]
                                )

                        }


                        ok, message = api_post(
                            payload
                        )


                        if ok:

                            refresh_data()

                            st.rerun()

                        else:

                            st.error(
                                message
                            )


# ============================================================
# TAB 5 — RECORDS
# ============================================================

with tab5:

    st.markdown(
        """
        <div class="nc-section">
            📂 CUSTOMER RECORDS & SEARCH
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
            "🔍 Search Name / Mobile / Service"
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

            filtered = df_all[mask].copy()

        else:

            filtered = df_all.copy()


        st.caption(
            f"Showing {len(filtered)} records"
        )


        # ----------------------------------------------------
        # COMPACT TABLE
        # ----------------------------------------------------

        table_df = filtered[
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


        table_df.columns = [
            "Date",
            "Customer",
            "Mobile",
            "Service",
            "Amount",
            "Net Profit",
            "Cash",
            "Credit",
            "Expiry"
        ]


        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            height=500,
            column_config={
                "Date": st.column_config.TextColumn(
                    "Date",
                    width="small"
                ),
                "Customer": st.column_config.TextColumn(
                    "Customer",
                    width="medium"
                ),
                "Mobile": st.column_config.TextColumn(
                    "Mobile",
                    width="small"
                ),
                "Service": st.column_config.TextColumn(
                    "Service",
                    width="large"
                ),
                "Amount": st.column_config.NumberColumn(
                    "Amount",
                    format="₹ %d"
                ),
                "Net Profit": st.column_config.NumberColumn(
                    "Net Profit",
                    format="₹ %d"
                ),
                "Cash": st.column_config.NumberColumn(
                    "Cash",
                    format="₹ %d"
                ),
                "Credit": st.column_config.NumberColumn(
                    "Credit",
                    format="₹ %d"
                )
            }
        )


        st.markdown("---")


        # ----------------------------------------------------
        # RECORD ACTIONS
        # ----------------------------------------------------

        st.subheader(
            "✏️ Edit / Delete Record"
        )


        selected_row = st.selectbox(
            "Select Record",
            filtered["_row_number"].tolist(),
            format_func=lambda x: (
                f"{filtered.loc[filtered['_row_number'] == x, 'name'].iloc[0]}"
                f" — "
                f"{filtered.loc[filtered['_row_number'] == x, 'mobile'].iloc[0]}"
                f" — "
                f"{filtered.loc[filtered['_row_number'] == x, 'created_at'].iloc[0]}"
            )
        )


        selected_record = filtered[
            filtered["_row_number"]
            == selected_row
        ].iloc[0].to_dict()


        a1, a2 = st.columns(2)


        with a1:

            if st.button(
                "✏️ EDIT SELECTED RECORD",
                use_container_width=True
            ):

                st.session_state.editing_customer = (
                    selected_record
                )

                st.session_state.selected_date = (
                    datetime.strptime(
                        selected_record["created_at"],
                        "%Y-%m-%d"
                    ).date()
                )

                st.rerun()


        with a2:

            if st.button(
                "🗑️ DELETE SELECTED RECORD",
                use_container_width=True
            ):

                st.session_state.delete_confirm = (
                    selected_record
                )


        # ----------------------------------------------------
        # DELETE CONFIRMATION
        # ----------------------------------------------------

        if (
            "delete_confirm"
            in st.session_state
            and st.session_state.delete_confirm
        ):

            record = (
                st.session_state.delete_confirm
            )


            st.warning(
                f"⚠️ Delete {record['name']}'s record?"
            )


            y, n = st.columns(2)


            with y:

                if st.button(
                    "✅ YES, DELETE",
                    type="primary",
                    use_container_width=True
                ):

                    payload = {

                        "action":
                            "delete",

                        "row_number":
                            int(
                                record["_row_number"]
                            )

                    }


                    ok, message = api_post(
                        payload
                    )


                    if ok:

                        st.session_state.delete_confirm = None

                        refresh_data()

                        st.success(
                            "Record deleted."
                        )

                        st.rerun()

                    else:

                        st.error(
                            message
                        )


            with n:

                if st.button(
                    "❌ NO, CANCEL",
                    use_container_width=True
                ):

                    st.session_state.delete_confirm = None

                    st.rerun()


        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        export_df = filtered.drop(
            columns=["_row_number"],
            errors="ignore"
        )


        csv_data = export_df.to_csv(
            index=False
        ).encode(
            "utf-8-sig"
        )


        st.download_button(
            "📥 DOWNLOAD CSV",
            data=csv_data,
            file_name="NOOR_CYBER_WORLD_RECORDS.csv",
            mime="text/csv",
            use_container_width=True
        )


# ============================================================
# END
# ============================================================
