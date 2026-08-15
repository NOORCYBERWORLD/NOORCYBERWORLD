# ============================================================
# NOOR CYBER WORLD
# CUSTOMER MANAGEMENT SYSTEM
# FINAL APP.PY
# ============================================================

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
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib import colors


# ============================================================
# NOOR CYBER WORLD — HEADER
# ============================================================

st.markdown(
    f"""
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

        <div class="nc-income-bar">

            <span class="income-item">
                📅 <b>TODAY NET INCOME:</b>
                <span class="profit">₹ {day_net:,.0f}</span>
            </span>

            <span class="income-separator">|</span>

            <span class="income-item">
                🗓️ <b>MONTH NET INCOME:</b>
                <span class="profit">₹ {month_net:,.0f}</span>
            </span>

            <span class="income-separator">|</span>

            <span class="income-item">
                📊 <b>YEAR NET INCOME:</b>
                <span class="profit">₹ {year_net:,.0f}</span>
            </span>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# GOOGLE APPS SCRIPT URL
# ============================================================

WEB_APP_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwSipN_etRHmOKXczikdg1gwzBvksliKCLQ0NYIJX9BbCGcyalc8H14aMTo_mNAbytK"
    "/exec"
)


# ============================================================
# TIMEZONE
# ============================================================

IST = timezone(
    timedelta(hours=5, minutes=30)
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

BASE_SERVICES = [
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

BASE_SERVICES = sorted(
    BASE_SERVICES,
    key=lambda x: x.lower()
)


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

if "confirm_credit" not in st.session_state:
    st.session_state.confirm_credit = None

if "success_message" not in st.session_state:
    st.session_state.success_message = None

if "last_saved_wa" not in st.session_state:
    st.session_state.last_saved_wa = None


# ============================================================
# HELPER
# ============================================================

def today_ist():
    return datetime.now(IST).date()


def empty_df():
    return pd.DataFrame(
        columns=COLUMNS
    )


def get_services():

    all_services = (
        BASE_SERVICES
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
# CLEAN DATAFRAME
# ============================================================

def clean_df(df):

    if df is None or df.empty:
        return empty_df()

    df = df.copy()

    # Make sure all required columns exist
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

    # Text
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

    # --------------------------------------------------------
    # IMPORTANT DATE FIX
    # --------------------------------------------------------
    # Do NOT use pd.to_datetime here.
    # Google Sheet date timezone can shift one day.
    # We only keep YYYY-MM-DD.
    # --------------------------------------------------------

    raw_date = (
        df["created_at"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["created_at"] = (
        raw_date
        .str.replace(
            "T",
            " ",
            regex=False
        )
        .str[:10]
    )

    # Numeric
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

    # Row number
    df["_row_number"] = pd.to_numeric(
        df["_row_number"],
        errors="coerce"
    ).fillna(0).astype(int)

    return df[COLUMNS]


# ============================================================
# FETCH CUSTOMER RECORDS
# ============================================================

@st.cache_data(ttl=3)
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
# FETCH EXPENSES
# ============================================================

@st.cache_data(ttl=3)
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
# API POST
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
                    data.get(
                        "success",
                        False
                    )
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

            if response.status_code < 400:
                return True, "Success"

            return False, "Request failed"

    except Exception as e:

        return False, str(e)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&display=swap'
);


/* ----------------------------------------------------------
   MAIN APP
---------------------------------------------------------- */

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
    font-family:Inter,sans-serif;
}


/* ----------------------------------------------------------
   PAGE WIDTH
---------------------------------------------------------- */

.block-container {

    max-width:1450px;

    padding-top:1.5rem;
    padding-bottom:3rem;
}


/* ----------------------------------------------------------
   HEADER
---------------------------------------------------------- */

.nc-header {

    width:100%;

    text-align:center;

    padding:
        8px
        10px
        15px;

    margin:0 0 8px 0;

}


/* IMPORTANT:
   Title will NOT get cut from top.
*/

.nc-title {

    font-family:
        Orbitron,
        Arial,
        sans-serif;

    font-size:42px;

    line-height:1.25;

    font-weight:800;

    letter-spacing:3px;

    color:#22d3ee;

    text-shadow:
        0 0 10px
        rgba(34,211,238,.25),

        0 0 22px
        rgba(34,211,238,.18);

    margin:0;

    padding:4px 0;

}


/* Main title */

.nc-main-title {

    font-family:
        Inter,
        Arial,
        sans-serif;

    font-size:20px;

    line-height:1.3;

    font-weight:800;

    letter-spacing:2px;

    color:#ffffff;

    margin-top:5px;

}


/* Subtitle */

.nc-sub {

    font-family:Inter,sans-serif;

    font-size:11px;

    line-height:1.5;

    letter-spacing:2px;

    color:#94a3b8;

    margin-top:4px;

}


/* ----------------------------------------------------------
   TOP INCOME BOX
---------------------------------------------------------- */

.nc-top {

    background:
        linear-gradient(
            145deg,
            rgba(15,23,42,.96),
            rgba(30,41,59,.82)
        );

    border:
        1px solid
        rgba(34,211,238,.28);

    border-radius:12px;

    padding:8px 14px;

    text-align:right;

    font-size:12px;

    line-height:1.8;

    box-shadow:
        0 8px 25px
        rgba(0,0,0,.15);

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


/* ----------------------------------------------------------
   SECTION TITLE
---------------------------------------------------------- */

.nc-section {

    font-family:
        Orbitron,
        sans-serif;

    font-size:18px;

    font-weight:700;

    color:#e2e8f0;

    margin:
        8px 0
        14px 0;

}


/* ----------------------------------------------------------
   GREEN CARD
---------------------------------------------------------- */

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
        5px solid
        #22c55e;

    border-radius:12px;

    padding:
        10px 13px;

    margin:
        5px 0;

}


/* ----------------------------------------------------------
   RED CARD
---------------------------------------------------------- */

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
        5px solid
        #ef4444;

    border-radius:12px;

    padding:
        10px 13px;

    margin:
        5px 0;

}


/* ----------------------------------------------------------
   METRICS
---------------------------------------------------------- */

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


/* ----------------------------------------------------------
   BUTTON
---------------------------------------------------------- */

.stButton > button {

    border-radius:9px;

    font-weight:700;

}


/* ----------------------------------------------------------
   DATAFRAME
---------------------------------------------------------- */

div[data-testid="stDataFrame"] {

    border-radius:10px;

}


/* ----------------------------------------------------------
   TABS
---------------------------------------------------------- */

button[data-baseweb="tab"] {

    font-weight:700;

}


/* ----------------------------------------------------------
   MOBILE
---------------------------------------------------------- */

@media(max-width:800px) {

    .nc-title {

        font-size:28px;

        letter-spacing:2px;

    }

    .nc-main-title {

        font-size:15px;

        letter-spacing:1px;

    }

    .nc-sub {

        font-size:9px;

    }

    .nc-top {

        text-align:center;

        font-size:10px;

    }

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
# DATE
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

today_string = today_ist().strftime(
    "%Y-%m-%d"
)

month_string = today_ist().strftime(
    "%Y-%m"
)

year_string = today_ist().strftime(
    "%Y"
)


if not df.empty:

    today_net = df.loc[
        df["created_at"].str[:10]
        == today_string,
        "net_amount"
    ].sum()

    month_net = df.loc[
        df["created_at"].str[:7]
        == month_string,
        "net_amount"
    ].sum()

    year_net = df.loc[
        df["created_at"].str[:4]
        == year_string,
        "net_amount"
    ].sum()

else:

    today_net = 0
    month_net = 0
    year_net = 0


# ============================================================
# TOP INCOME DISPLAY
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

    if picked_date != selected_date:

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


# ============================================================
# TAB 1
# TODAY'S ENTRIES
# ============================================================

with tab1:

    st.markdown(
        f"""
        <div class="nc-section">
            📋 ENTRIES FOR
            {selected_date.strftime("%d-%m-%Y")}
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


    m1, m2, m3, m4 = (
        st.columns(4)
    )


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
    # TODAY ENTRIES
    # --------------------------------------------------------

    if day_df.empty:

        st.info(
            "ℹ️ No entries recorded for this date yet."
        )

    else:

        st.markdown(
            "### 🟢 Today's Entries"
        )


        display_day = (
            day_df
            .drop(
                columns=["_row_number"],
                errors="ignore"
            )
            .copy()
        )


        display_day.columns = [
            "Date",
            "Name",
            "Mobile",
            "Service",
            "Amount",
            "Net Profit",
            "Cash",
            "Credit",
            "Expiry"
        ]


        for col in [
            "Amount",
            "Net Profit",
            "Cash",
            "Credit"
        ]:

            display_day[col] = (
                display_day[col]
                .map(
                    lambda x:
                    f"₹ {float(x):,.0f}"
                )
            )


        st.dataframe(
            display_day,
            use_container_width=True,
            hide_index=True,
            height=380
        )


        st.markdown(
            "### ✏️ ENTRY ACTIONS"
        )


        for _, row in day_df.iterrows():

            row_number = int(
                row["_row_number"]
            )

            if float(row["credit"]) > 0:
                card_class = "nc-red"
                badge = "🔴 CREDIT"
            else:
                card_class = "nc-green"
                badge = "🟢 CASH"


            info_col, edit_col, delete_col = (
                st.columns([8,1,1])
            )


            with info_col:

                st.markdown(
                    f"""
                    <div class="{card_class}">

                    <b>
                        {row["name"]}
                    </b>

                    &nbsp; • &nbsp;

                    {row["mobile"]}

                    &nbsp; • &nbsp;

                    <b>{badge}</b>

                    <br>

                    {row["service"]}

                    &nbsp; | &nbsp;

                    Amount:
                    <b>
                        ₹ {float(row["amount"]):,.0f}
                    </b>

                    &nbsp; | &nbsp;

                    Cash:
                    <b>
                        ₹ {float(row["cash"]):,.0f}
                    </b>

                    &nbsp; | &nbsp;

                    Credit:
                    <b>
                        ₹ {float(row["credit"]):,.0f}
                    </b>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with edit_col:

                if st.button(
                    "✏️",
                    key=f"today_edit_{row_number}",
                    use_container_width=True
                ):

                    st.session_state.editing_row = (
                        row.to_dict()
                    )

                    st.session_state.last_saved_wa = None

                    st.rerun()


            with delete_col:

                if st.button(
                    "🗑️",
                    key=f"today_delete_{row_number}",
                    use_container_width=True
                ):

                    st.session_state.confirm_delete = (
                        row_number
                    )

                    st.rerun()


    # ========================================================
    # DELETE CONFIRMATION
    # ========================================================

    if st.session_state.confirm_delete:

        delete_row = (
            st.session_state.confirm_delete
        )

        st.warning(
            "⚠️ Are you sure you want to delete this entry?"
        )


        yes_col, no_col = (
            st.columns(2)
        )


        with yes_col:

            if st.button(
                "✅ YES, DELETE",
                type="primary",
                use_container_width=True,
                key="delete_yes_tab1"
            ):

                ok, msg = post_api(
                    {
                        "action": "delete",
                        "row_number": int(
                            delete_row
                        )
                    }
                )


                if ok:

                    st.session_state.confirm_delete = None

                    get_records.clear()

                    st.session_state.success_message = (
                        "Entry deleted successfully."
                    )

                    st.rerun()

                else:

                    st.error(msg)


        with no_col:

            if st.button(
                "❌ NO, CANCEL",
                use_container_width=True,
                key="delete_no_tab1"
            ):

                st.session_state.confirm_delete = None

                st.rerun()


    st.markdown("---")


    # ========================================================
    # ADD / EDIT FORM
    # ========================================================

    editing = (
        st.session_state.editing_row
        is not None
    )


    old = (
        st.session_state.editing_row
        or {}
    )


    if editing:

        st.markdown(
            "<div class='nc-section'>✏️ EDIT CUSTOMER ENTRY</div>",
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            "<div class='nc-section'>➕ ADD NEW CUSTOMER ENTRY</div>",
            unsafe_allow_html=True
        )


    left_col, right_col = (
        st.columns(2)
    )


    # ========================================================
    # LEFT SIDE
    # ========================================================

    with left_col:

        mobile = st.text_input(
            "Mobile Number *",
            value=str(
                old.get(
                    "mobile",
                    ""
                )
            ),
            key="customer_mobile"
        ).strip()


        # ----------------------------------------------------
        # AUTO CUSTOMER NAME
        # ----------------------------------------------------

        auto_name = ""


        if (
            mobile
            and not editing
            and not df.empty
        ):

            found = df[
                df["mobile"]
                .astype(str)
                .str.strip()
                == mobile
            ]


            if not found.empty:

                auto_name = str(
                    found.iloc[-1]["name"]
                ).strip()


        name = st.text_input(
            "Customer Name *",
            value=(
                str(
                    old.get(
                        "name",
                        ""
                    )
                )
                if editing
                else auto_name
            ),
            key=(
                f"customer_name_"
                f"{mobile}_"
                f"{editing}"
            )
        ).strip()


        service_list = get_services()


        old_service = str(
            old.get(
                "service",
                service_list[0]
            )
        )


        if old_service in service_list:

            service_index = (
                service_list.index(
                    old_service
                )
            )

        else:

            service_index = (
                service_list.index(
                    "Other"
                )
            )


        selected_service = st.selectbox(
            "Search / Select Service *",
            service_list,
            index=service_index,
            key="customer_service"
        )


        custom_service = ""


        if selected_service == "Other":

            custom_service = st.text_input(
                "Custom Service Name *",
                value=(
                    old_service
                    if old_service
                    not in service_list
                    else ""
                ),
                key="custom_service"
            ).strip()


    # ========================================================
    # RIGHT SIDE
    # ========================================================

    with right_col:

        amount = st.number_input(
            "Total Fee / Gross Amount (₹) *",
            min_value=0,
            step=10,
            value=int(
                float(
                    old.get(
                        "amount",
                        0
                    )
                )
            ),
            key="customer_amount"
        )


        net_amount = st.number_input(
            "Net Income / Profit (₹) *",
            min_value=0,
            step=10,
            value=int(
                float(
                    old.get(
                        "net_amount",
                        0
                    )
                )
            ),
            key="customer_net"
        )


        old_credit = float(
            old.get(
                "credit",
                0
            )
        )


        payment_index = (
            1
            if old_credit > 0
            else 0
        )


        payment_type = st.radio(
            "Payment Type *",
            [
                "💵 CASH",
                "🔴 CREDIT (UDHARI)"
            ],
            index=payment_index,
            horizontal=True,
            key="customer_payment"
        )


        # ----------------------------------------------------
        # PAYMENT CALCULATION
        # ----------------------------------------------------

        if "CREDIT" in payment_type:

            cash_value = 0

            credit_value = int(
                amount
            )

        else:

            cash_value = int(
                amount
            )

            credit_value = 0


        st.info(
            f"""
            **PAYMENT SPLIT**

            💵 Cash:
            ₹ {cash_value:,}

            &nbsp;&nbsp;&nbsp;

            🔴 Credit:
            ₹ {credit_value:,}
            """
        )


        old_expiry = str(
            old.get(
                "expiry",
                "N/A"
            )
        ).strip()


        expiry_exists = (
            old_expiry
            not in [
                "",
                "N/A"
            ]
        )


        has_expiry = st.checkbox(
            "Requires Renewal / Validity?",
            value=expiry_exists,
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


        validity_duration = st.number_input(
            "Validity Duration",
            min_value=1,
            step=1,
            value=1,
            key="customer_validity_duration"
        )


    # ========================================================
    # SAVE / CANCEL
    # ========================================================

    save_col, cancel_col = (
        st.columns(2)
    )


    with save_col:

        if editing:

            save_label = "💾 UPDATE ENTRY"

        else:

            save_label = "⚡ SAVE ENTRY"


        if st.button(
            save_label,
            type="primary",
            use_container_width=True,
            key="save_customer_entry"
        ):

            if not name:

                st.error(
                    "Please enter Customer Name."
                )

                st.stop()


            if not mobile:

                st.error(
                    "Please enter Mobile Number."
                )

                st.stop()


            # ------------------------------------------------
            # SERVICE
            # ------------------------------------------------

            final_service = selected_service


            if selected_service == "Other":

                if not custom_service:

                    st.error(
                        "Please enter Custom Service Name."
                    )

                    st.stop()


                final_service = (
                    custom_service
                )


                if (
                    final_service
                    not in
                    st.session_state.custom_services
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
                                validity_duration
                            )
                        )
                    )


                elif validity_unit == "Months":

                    expiry_date = (
                        base_date
                        + relativedelta(
                            months=int(
                                validity_duration
                            )
                        )
                    )


                else:

                    expiry_date = (
                        base_date
                        + relativedelta(
                            years=int(
                                validity_duration
                            )
                        )
                    )


                expiry = (
                    expiry_date.strftime(
                        "%Y-%m-%d"
                    )
                )


            # ------------------------------------------------
            # PAYLOAD
            # ------------------------------------------------

            payload = {

                "action": (
                    "edit"
                    if editing
                    else "add"
                ),

                "created_at":
                    selected_date_str,

                "name":
                    name,

                "mobile":
                    mobile,

                "service":
                    final_service,

                "amount":
                    str(
                        int(amount)
                    ),

                "net_amount":
                    str(
                        int(net_amount)
                    ),

                "cash":
                    str(
                        cash_value
                    ),

                "credit":
                    str(
                        credit_value
                    ),

                "expiry":
                    expiry
            }


            if editing:

                payload["row_number"] = int(
                    old["_row_number"]
                )


            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            with st.spinner(
                "Saving..."
            ):

                ok, msg = post_api(
                    payload
                )


            if ok:

                get_records.clear()

                st.session_state.editing_row = None


                thank_you = (
                    f"Dear {name}, "
                    f"Thank you for choosing "
                    f"NOOR CYBER WORLD for "
                    f"{final_service}! "
                    f"Total Amount: Rs.{int(amount)}."
                )


                st.session_state.last_saved_wa = (
                    "https://wa.me/91"
                    + mobile
                    + "?text="
                    + quote(
                        thank_you
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

        if editing:

            if st.button(
                "❌ CANCEL EDIT",
                use_container_width=True,
                key="cancel_customer_edit"
            ):

                st.session_state.editing_row = None

                st.rerun()


    # ========================================================
    # WHATSAPP
    # ========================================================

    if st.session_state.last_saved_wa:

        st.markdown("<br>", unsafe_allow_html=True)

        st.link_button(
            "💬 SEND THANK YOU WHATSAPP",
            st.session_state.last_saved_wa,
            use_container_width=True
        )


# ============================================================
# TAB 2
# CREDIT COLLECTION
# ============================================================

with tab2:

    st.markdown(
        "<div class='nc-section'>🔴 PENDING CREDIT / UDHARI COLLECTION</div>",
        unsafe_allow_html=True
    )


    if df.empty:

        credit_df = empty_df()

    else:

        credit_df = df[
            df["credit"] > 0
        ].copy()


    if credit_df.empty:

        st.success(
            "🎉 No pending credit! All payments are clear."
        )

    else:

        total_pending = int(
            credit_df["credit"].sum()
        )


        st.error(
            f"⚠️ TOTAL PENDING CREDIT: "
            f"₹ {total_pending:,} "
            f"({len(credit_df)} Entries)"
        )


        st.markdown("---")


        for _, row in credit_df.iterrows():

            row_number = int(
                row["_row_number"]
            )


            info_col, whatsapp_col, cash_col = (
                st.columns([6,2,2])
            )


            with info_col:

                st.markdown(
                    f"""
                    <div class="nc-red">

                    <b>
                        🔴 {row["name"]}
                    </b>

                    ({row["mobile"]})

                    <br>

                    Service:
                    <b>
                        {row["service"]}
                    </b>

                    <br>

                    Pending Credit:

                    <b style="
                        color:#ef4444;
                        font-size:18px;
                    ">

                        ₹ {float(row["credit"]):,.0f}

                    </b>

                    <br>

                    Date:
                    {row["created_at"]}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with whatsapp_col:

                reminder = quote(
                    f"Hello {row['name']}, "
                    f"this is a gentle reminder from "
                    f"NOOR CYBER WORLD. "
                    f"Your payment of Rs."
                    f"{int(row['credit'])} "
                    f"for {row['service']} "
                    f"is pending. "
                    f"Please clear your balance. "
                    f"Thank you!"
                )


                st.link_button(
                    "💬 SEND REMINDER",
                    (
                        "https://wa.me/91"
                        + str(
                            row["mobile"]
                        ).strip()
                        + "?text="
                        + reminder
                    ),
                    use_container_width=True
                )


            with cash_col:

                if st.button(
                    "💵 CASH RECEIVED",
                    key=f"cash_received_{row_number}",
                    use_container_width=True
                ):

                    st.session_state.confirm_credit = (
                        row_number
                    )

                    st.rerun()


        # ----------------------------------------------------
        # CREDIT CONFIRMATION
        # ----------------------------------------------------

        if st.session_state.confirm_credit:

            credit_row = (
                st.session_state.confirm_credit
            )


            st.warning(
                "⚠️ Confirm that this credit amount has been received in CASH."
            )


            yes_col, no_col = (
                st.columns(2)
            )


            with yes_col:

                if st.button(
                    "✅ YES, CASH RECEIVED",
                    type="primary",
                    use_container_width=True,
                    key="confirm_credit_yes"
                ):

                    ok, msg = post_api(
                        {
                            "action":
                                "credit_to_cash",

                            "row_number":
                                int(
                                    credit_row
                                )
                        }
                    )


                    if ok:

                        st.session_state.confirm_credit = None

                        get_records.clear()

                        st.session_state.success_message = (
                            "Credit successfully converted to Cash."
                        )

                        st.rerun()

                    else:

                        st.error(msg)


            with no_col:

                if st.button(
                    "❌ NO",
                    use_container_width=True,
                    key="confirm_credit_no"
                ):

                    st.session_state.confirm_credit = None

                    st.rerun()


# ============================================================
# TAB 3
# RENEWAL ALERTS
# ============================================================

with tab3:

    st.markdown(
        "<div class='nc-section'>🔔 RENEWAL ALERTS — NEXT 15 DAYS</div>",
        unsafe_allow_html=True
    )


    today = today_ist()

    renewal_list = []


    for _, row in df.iterrows():

        expiry = str(
            row["expiry"]
        ).strip()


        if (
            not expiry
            or expiry == "N/A"
        ):
            continue


        try:

            expiry_date = datetime.strptime(
                expiry[:10],
                "%Y-%m-%d"
            ).date()


            days_left = (
                expiry_date
                - today
            ).days


            if 0 <= days_left <= 15:

                renewal_list.append(
                    (
                        row,
                        expiry_date,
                        days_left
                    )
                )

        except Exception:

            continue


    if not renewal_list:

        st.success(
            "🎉 No renewals due in the next 15 days."
        )

    else:

        st.warning(
            f"⚠️ {len(renewal_list)} renewal(s) pending."
        )


        for row, expiry_date, days_left in renewal_list:

            date_text = (
                expiry_date.strftime(
                    "%d-%m-%Y"
                )
            )


            st.markdown(
                f"""
                <div class="nc-red">

                <b>
                    🔴 {row["name"]}
                </b>

                ({row["mobile"]})

                <br>

                Service:
                <b>
                    {row["service"]}
                </b>

                <br>

                Expiry:
                <b>
                    {date_text}
                </b>

                — {days_left} days remaining

                </div>
                """,
                unsafe_allow_html=True
            )


            renewal_message = quote(
                f"Hello {row['name']}, "
                f"your service {row['service']} "
                f"is expiring on {date_text}. "
                f"Please visit NOOR CYBER WORLD "
                f"to renew it on time."
            )


            st.link_button(
                f"💬 SEND RENEWAL WHATSAPP TO {row['name']}",
                (
                    "https://wa.me/91"
                    + str(
                        row["mobile"]
                    ).strip()
                    + "?text="
                    + renewal_message
                )
            )


# ============================================================
# TAB 4
# EXPENSES
# ============================================================

with tab4:

    st.markdown(
        "<div class='nc-section'>💸 SHOP EXPENSES & REAL PROFIT</div>",
        unsafe_allow_html=True
    )


    expense_left, expense_right = (
        st.columns([1,2])
    )


    # ========================================================
    # ADD EXPENSE
    # ========================================================

    with expense_left:

        st.subheader(
            "➕ Add Shop Expense"
        )


        expense_title = st.text_input(
            "Expense Title",
            key="expense_title"
        )


        expense_amount = st.number_input(
            "Expense Amount (₹)",
            min_value=0,
            step=10,
            key="expense_amount"
        )


        if st.button(
            "💾 ADD EXPENSE",
            type="primary",
            use_container_width=True,
            key="add_expense_button"
        ):

            if (
                not expense_title.strip()
                or expense_amount <= 0
            ):

                st.error(
                    "Enter valid expense title and amount."
                )

            else:

                ok, msg = post_api(
                    {
                        "action":
                            "add_expense",

                        "created_at":
                            selected_date_str,

                        "title":
                            expense_title.strip(),

                        "amount":
                            str(
                                int(
                                    expense_amount
                                )
                            )
                    }
                )


                if ok:

                    get_expenses.clear()

                    st.session_state.success_message = (
                        "Expense added successfully."
                    )

                    st.rerun()

                else:

                    st.error(msg)


    # ========================================================
    # EXPENSE SUMMARY
    # ========================================================

    with expense_right:

        selected_expenses = [
            exp
            for exp in expenses
            if str(
                exp.get(
                    "created_at",
                    ""
                )
            )[:10]
            == selected_date_str
        ]


        total_expenses = sum(
            float(
                exp.get(
                    "amount",
                    0
                )
            )
            for exp in selected_expenses
        )


        actual_saving = (
            total_net
            - total_expenses
        )


        e1, e2, e3 = (
            st.columns(3)
        )


        e1.metric(
            "NET PROFIT",
            f"₹ {total_net:,}"
        )


        e2.metric(
            "EXPENSES",
            f"₹ {total_expenses:,.0f}"
        )


        e3.metric(
            "ACTUAL SAVINGS",
            f"₹ {actual_saving:,.0f}"
        )


        st.markdown("---")


        if selected_expenses:

            st.markdown(
                "### 🔴 TODAY'S EXPENSES"
            )


            for exp in selected_expenses:

                expense_row = int(
                    exp.get(
                        "_row_number",
                        0
                    )
                )


                info_col, delete_col = (
                    st.columns([8,1])
                )


                with info_col:

                    st.markdown(
                        f"""
                        <div class="nc-red">

                        <b>
                            💸 {exp.get("title","")}
                        </b>

                        &nbsp; — &nbsp;

                        <b>
                            ₹ {float(exp.get("amount",0)):,.0f}
                        </b>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                with delete_col:

                    if expense_row:

                        if st.button(
                            "🗑️",
                            key=f"expense_delete_{expense_row}",
                            use_container_width=True
                        ):

                            ok, msg = post_api(
                                {
                                    "action":
                                        "delete_expense",

                                    "row_number":
                                        expense_row
                                }
                            )


                            if ok:

                                get_expenses.clear()

                                st.rerun()

                            else:

                                st.error(msg)

        else:

            st.info(
                "No expenses recorded for this date."
            )


# ============================================================
# TAB 5
# RECORDS & SEARCH
# ============================================================

with tab5:

    st.markdown(
        "<div class='nc-section'>📂 CUSTOMER RECORDS & SEARCH</div>",
        unsafe_allow_html=True
    )


    if df.empty:

        st.info(
            "No records available."
        )

    else:

        search = st.text_input(
            "🔍 Search Name / Mobile / Service",
            key="records_search"
        ).strip().lower()


        filtered_df = df.copy()


        if search:

            filtered_df = filtered_df[
                filtered_df["name"]
                .str.lower()
                .str.contains(
                    search,
                    na=False
                )
                |
                filtered_df["mobile"]
                .str.lower()
                .str.contains(
                    search,
                    na=False
                )
                |
                filtered_df["service"]
                .str.lower()
                .str.contains(
                    search,
                    na=False
                )
            ]


        # ====================================================
        # EXPORT
        # ====================================================

        export_df = filtered_df.drop(
            columns=[
                "_row_number"
            ],
            errors="ignore"
        ).copy()


        export_col1, export_col2 = (
            st.columns(2)
        )


        with export_col1:

            st.download_button(
                "📥 DOWNLOAD CSV",

                data=(
                    export_df
                    .to_csv(
                        index=False
                    )
                    .encode(
                        "utf-8-sig"
                    )
                ),

                file_name=(
                    "NOOR_CYBER_WORLD_RECORDS.csv"
                ),

                mime="text/csv",

                use_container_width=True
            )


        with export_col2:

            # ------------------------------------------------
            # PDF
            # ------------------------------------------------

            pdf_buffer = io.BytesIO()


            pdf_doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=letter,
                rightMargin=20,
                leftMargin=20,
                topMargin=20,
                bottomMargin=20
            )


            styles = (
                getSampleStyleSheet()
            )


            title_style = ParagraphStyle(
                "NCWTitle",
                parent=styles["Heading1"],
                alignment=1,
                fontSize=16,
                spaceAfter=10
            )


            pdf_elements = []


            pdf_elements.append(
                Paragraph(
                    "NOOR CYBER WORLD - CUSTOMER RECORDS",
                    title_style
                )
            )


            pdf_elements.append(
                Spacer(1,10)
            )


            pdf_rows = [
                [
                    "Date",
                    "Name",
                    "Mobile",
                    "Service",
                    "Gross",
                    "Net",
                    "Cash",
                    "Credit",
                    "Expiry"
                ]
            ]


            for _, row in export_df.iterrows():

                pdf_rows.append(
                    [
                        str(
                            row["created_at"]
                        ),

                        str(
                            row["name"]
                        ),

                        str(
                            row["mobile"]
                        ),

                        str(
                            row["service"]
                        ),

                        f"Rs. {float(row['amount']):.0f}",

                        f"Rs. {float(row['net_amount']):.0f}",

                        f"Rs. {float(row['cash']):.0f}",

                        f"Rs. {float(row['credit']):.0f}",

                        str(
                            row["expiry"]
                        )
                    ]
                )


            pdf_table = Table(
                pdf_rows,
                repeatRows=1
            )


            pdf_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0,0),
                            (-1,0),
                            colors.HexColor(
                                "#0f172a"
                            )
                        ),

                        (
                            "TEXTCOLOR",
                            (0,0),
                            (-1,0),
                            colors.white
                        ),

                        (
                            "GRID",
                            (0,0),
                            (-1,-1),
                            0.4,
                            colors.grey
                        ),

                        (
                            "FONTSIZE",
                            (0,0),
                            (-1,-1),
                            7
                        ),

                        (
                            "ALIGN",
                            (0,0),
                            (-1,-1),
                            "CENTER"
                        )
                    ]
                )
            )


            pdf_elements.append(
                pdf_table
            )


            pdf_doc.build(
                pdf_elements
            )


            pdf_buffer.seek(0)


            st.download_button(
                "📄 DOWNLOAD PDF",

                data=(
                    pdf_buffer.getvalue()
                ),

                file_name=(
                    "NOOR_CYBER_WORLD_RECORDS.pdf"
                ),

                mime="application/pdf",

                use_container_width=True
            )


        st.markdown("---")


        st.caption(
            f"Showing {len(filtered_df)} records"
        )


        # ====================================================
        # COMPACT RECORD TABLE
        # ====================================================

        record_view = (
            filtered_df
            .drop(
                columns=[
                    "_row_number"
                ],
                errors="ignore"
            )
            .copy()
        )


        record_view.columns = [
            "Date",
            "Name",
            "Mobile",
            "Service",
            "Amount",
            "Net Profit",
            "Cash",
            "Credit",
            "Expiry"
        ]


        for col in [
            "Amount",
            "Net Profit",
            "Cash",
            "Credit"
        ]:

            record_view[col] = (
                record_view[col]
                .map(
                    lambda x:
                    f"₹ {float(x):,.0f}"
                )
            )


        st.dataframe(
            record_view,
            use_container_width=True,
            hide_index=True,
            height=500
        )


        # ====================================================
        # ACTIONS
        # ====================================================

        st.markdown(
            "### ✏️ EDIT / DELETE RECORD"
        )


        for _, row in filtered_df.iterrows():

            row_number = int(
                row["_row_number"]
            )


            if float(row["credit"]) > 0:

                card_class = "nc-red"

            else:

                card_class = "nc-green"


            info_col, edit_col, delete_col = (
                st.columns([8,1,1])
            )


            with info_col:

                st.markdown(
                    f"""
                    <div class="{card_class}">

                    <b>
                        {row["name"]}
                    </b>

                    &nbsp; • &nbsp;

                    {row["mobile"]}

                    &nbsp; • &nbsp;

                    {row["service"]}

                    &nbsp; | &nbsp;

                    Amount:
                    ₹ {float(row["amount"]):,.0f}

                    &nbsp; | &nbsp;

                    Cash:
                    ₹ {float(row["cash"]):,.0f}

                    &nbsp; | &nbsp;

                    Credit:
                    ₹ {float(row["credit"]):,.0f}

                    &nbsp; | &nbsp;

                    Date:
                    {row["created_at"]}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with edit_col:

                if st.button(
                    "✏️",
                    key=f"record_edit_{row_number}",
                    use_container_width=True
                ):

                    st.session_state.editing_row = (
                        row.to_dict()
                    )


                    try:

                        st.session_state.selected_date = (
                            datetime.strptime(
                                str(
                                    row[
                                        "created_at"
                                    ]
                                )[:10],
                                "%Y-%m-%d"
                            ).date()
                        )

                    except Exception:

                        pass


                    st.session_state.last_saved_wa = None

                    st.rerun()


            with delete_col:

                if st.button(
                    "🗑️",
                    key=f"record_delete_{row_number}",
                    use_container_width=True
                ):

                    st.session_state.confirm_delete = (
                        row_number
                    )

                    st.rerun()


# ============================================================
# GLOBAL DELETE CONFIRMATION
# ============================================================

if st.session_state.confirm_delete:

    delete_row_number = (
        st.session_state.confirm_delete
    )


    st.warning(
        f"⚠️ Confirm deletion of entry "
        f"(Sheet Row {delete_row_number})"
    )


    yes_col, no_col = (
        st.columns(2)
    )


    with yes_col:

        if st.button(
            "✅ YES, DELETE ENTRY",
            type="primary",
            use_container_width=True,
            key="global_delete_yes"
        ):

            ok, msg = post_api(
                {
                    "action":
                        "delete",

                    "row_number":
                        int(
                            delete_row_number
                        )
                }
            )


            if ok:

                st.session_state.confirm_delete = None

                get_records.clear()

                st.session_state.success_message = (
                    "Entry deleted successfully."
                )

                st.rerun()

            else:

                st.error(msg)


    with no_col:

        if st.button(
            "❌ NO, KEEP ENTRY",
            use_container_width=True,
            key="global_delete_no"
        ):

            st.session_state.confirm_delete = None

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
