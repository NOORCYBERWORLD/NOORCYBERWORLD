import streamlit as st
import pandas as pd
import requests
import json
import io
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import quote

# Reportlab
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
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NOOR CYBER WORLD",
    layout="wide"
)


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
    "Xerox / Color Printout / Lamination / Scanning"
]

DEFAULT_SERVICES = sorted(
    DEFAULT_SERVICES,
    key=lambda x: x.lower()
) + ["Other"]


if "custom_services" not in st.session_state:
    st.session_state.custom_services = []

if "expenses" not in st.session_state:
    st.session_state.expenses = []

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now(IST).date()

if "editing_row" not in st.session_state:
    st.session_state.editing_row = None


def get_all_services():
    services = (
        DEFAULT_SERVICES[:-1]
        + st.session_state.custom_services
    )

    services = sorted(
        set(
            s.strip()
            for s in services
            if s and s.strip()
        ),
        key=lambda x: x.lower()
    )

    services.append("Other")

    return services


SERVICES = get_all_services()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&display=swap');

:root {
    --red:#ef4444;
    --green:#22c55e;
    --cyan:#22d3ee;
    --border:rgba(96,165,250,.22);
}

.stApp {
    background:
        linear-gradient(
            115deg,
            rgba(5,8,15,.96),
            rgba(7,18,32,.84)
        ),
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
    text-align:center;
    padding:10px 10px 15px;
    margin-bottom:10px;
}

.nc-title {
    font-family:Arial,sans-serif;
    font-size:32px;
    font-weight:800;
    letter-spacing:3px;
    color:white;
    margin-bottom:2px;
}

.nc-main-title {
    font-family:Arial,sans-serif;
    font-size:20px;
    font-weight:700;
    letter-spacing:2px;
    color:#22d3ee;
    margin-bottom:5px;
}

.nc-sub {
    font-size:11px;
    letter-spacing:1.5px;
    color:#cbd5e1;
}

div[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            rgba(15,23,42,.92),
            rgba(30,41,59,.72)
        );

    border:1px solid var(--border);
    border-radius:18px;
    padding:18px;

    box-shadow:0 12px 35px rgba(0,0,0,.22);
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
            rgba(15,23,42,.85)
        );

    border:1px solid rgba(34,197,94,.5);
    border-left:6px solid #22c55e;
    border-radius:14px;

    padding:14px;
    margin:8px 0;
}

.nc-card-red {
    background:
        linear-gradient(
            145deg,
            rgba(153,27,27,.35),
            rgba(15,23,42,.85)
        );

    border:1px solid rgba(239,68,68,.5);
    border-left:6px solid #ef4444;
    border-radius:14px;

    padding:14px;
    margin:8px 0;
}

.nc-section {
    font-family:'Orbitron',sans-serif;
    font-size:18px;
    font-weight:700;
    color:#e2e8f0;

    margin:8px 0 14px;
}

.top-corner-stats {
    background:rgba(15,23,42,.85);
    border:1px solid rgba(34,211,238,.3);
    border-radius:12px;

    padding:12px 18px;
    text-align:right;

    font-size:13px;
    color:#cbd5e1;
    line-height:1.6;
}

.top-corner-stats span.gross {
    color:#22d3ee;
    font-weight:700;
}

.top-corner-stats span.cash {
    color:#22c55e;
    font-weight:700;
}

.top-corner-stats span.credit {
    color:#ef4444;
    font-weight:700;
}

.alert-badge {
    background:rgba(239,68,68,.2);
    border:1px solid #ef4444;
    color:#fca5a5;

    padding:10px 16px;
    border-radius:12px;

    font-weight:700;
    font-size:16px;

    margin-bottom:15px;
    display:inline-block;
}

</style>

<div class="nc-header">

    <div class="nc-title">
        NOOR CYBER WORLD
    </div>

    <div class="nc-main-title">
        CUSTOMERS MANAGEMENT SYSTEM
    </div>

    <div class="nc-sub">
        DIGITAL SERVICE • CUSTOMER RECORD • SMART MANAGEMENT
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
# HELPER FUNCTIONS
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
            df[col] = 0 if col in [
                "amount",
                "net_amount",
                "cash",
                "credit"
            ] else ""

    # Text columns
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
        )

    # Date
    raw_date = (
        df["created_at"]
        .fillna("")
        .astype(str)
    )

    parsed_date = pd.to_datetime(
        raw_date,
        errors="coerce"
    )

    df["created_at"] = parsed_date.dt.strftime(
        "%Y-%m-%d"
    )

    df.loc[
        parsed_date.isna(),
        "created_at"
    ] = raw_date[parsed_date.isna()]

    # Numeric columns
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
# FETCH GOOGLE SHEET
# ============================================================

@st.cache_data(ttl=5)
def fetch_sheet_records():

    try:

        response = requests.get(
            WEB_APP_URL,
            params={
                "t": int(datetime.now().timestamp())
            },
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


# ============================================================
# POST TO GOOGLE APPS SCRIPT
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
                            "Failed"
                        )
                    )
                )
            )

        except Exception:

            return True, "Success"

    except Exception as e:

        return False, str(e)


# ============================================================
# PDF GENERATOR
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

    elements = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,
        spaceAfter=15
    )

    elements.append(
        Paragraph(
            "NOOR CYBER WORLD - CUSTOMER RECORDS",
            title_style
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    headers = [
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

    table_data = [headers]

    for _, row in df.iterrows():

        table_data.append([
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
        table_data,
        colWidths=[
            50,
            75,
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
                colors.whitesmoke
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
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
                (-1, 0),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                8
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
                0.5,
                colors.HexColor("#cbd5e1")
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica"
            ),
            (
                "FONTSIZE",
                (0, 1),
                (-1, -1),
                7
            )
        ])
    )

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return buffer


# ============================================================
# FETCH DATA
# ============================================================

df_all = fetch_sheet_records()


# ============================================================
# MOBILE → NAME MAP
# ============================================================

mobile_to_name_map = {}

if not df_all.empty:

    for _, row in df_all.iterrows():

        mobile = str(
            row["mobile"]
        ).strip()

        name = str(
            row["name"]
        ).strip()

        if mobile and name:
            mobile_to_name_map[mobile] = name


# ============================================================
# TOP HEADER STATISTICS
# ============================================================

now_ist = datetime.now(IST)

current_date_str = now_ist.strftime(
    "%Y-%m-%d"
)

current_month_str = now_ist.strftime(
    "%Y-%m"
)

current_year_str = now_ist.strftime(
    "%Y"
)


if not df_all.empty:

    created_dates = pd.to_datetime(
        df_all["created_at"],
        errors="coerce"
    )

    day_mask = (
        created_dates.dt.strftime("%Y-%m-%d")
        == current_date_str
    )

    month_mask = (
        created_dates.dt.strftime("%Y-%m")
        == current_month_str
    )

    year_mask = (
        created_dates.dt.strftime("%Y")
        == current_year_str
    )

    day_gross = df_all.loc[
        day_mask,
        "amount"
    ].sum()

    day_cash = df_all.loc[
        day_mask,
        "cash"
    ].sum()

    day_credit = df_all.loc[
        day_mask,
        "credit"
    ].sum()

    day_net = df_all.loc[
        day_mask,
        "net_amount"
    ].sum()

    month_gross = df_all.loc[
        month_mask,
        "amount"
    ].sum()

    month_cash = df_all.loc[
        month_mask,
        "cash"
    ].sum()

    month_credit = df_all.loc[
        month_mask,
        "credit"
    ].sum()

    month_net = df_all.loc[
        month_mask,
        "net_amount"
    ].sum()

    year_gross = df_all.loc[
        year_mask,
        "amount"
    ].sum()

    year_cash = df_all.loc[
        year_mask,
        "cash"
    ].sum()

    year_credit = df_all.loc[
        year_mask,
        "credit"
    ].sum()

    year_net = df_all.loc[
        year_mask,
        "net_amount"
    ].sum()

else:

    (
        day_gross,
        day_cash,
        day_credit,
        day_net,
        month_gross,
        month_cash,
        month_credit,
        month_net,
        year_gross,
        year_cash,
        year_credit,
        year_net
    ) = (0,) * 12


st.markdown(
    f"""
<div class="top-corner-stats">

    📅 <b>Today:</b>
    Total <span class="gross">₹ {day_gross:,.0f}</span>
    |
    Cash <span class="cash">₹ {day_cash:,.0f}</span>
    |
    Credit <span class="credit">₹ {day_credit:,.0f}</span>
    |
    Net Profit <span class="cash">₹ {day_net:,.0f}</span>

    <br>

    🗓️ <b>Month:</b>
    Total <span class="gross">₹ {month_gross:,.0f}</span>
    |
    Cash <span class="cash">₹ {month_cash:,.0f}</span>
    |
    Credit <span class="credit">₹ {month_credit:,.0f}</span>
    |
    Net Profit <span class="cash">₹ {month_net:,.0f}</span>

    <br>

    📊 <b>Year:</b>
    Total <span class="gross">₹ {year_gross:,.0f}</span>
    |
    Cash <span class="cash">₹ {year_cash:,.0f}</span>
    |
    Credit <span class="credit">₹ {year_credit:,.0f}</span>
    |
    Net Profit <span class="cash">₹ {year_net:,.0f}</span>

</div>
""",
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# DATE SELECTOR
# ============================================================

selected_date_str = (
    st.session_state.selected_date.strftime(
        "%Y-%m-%d"
    )
)


if not df_all.empty:

    date_mask = (
        pd.to_datetime(
            df_all["created_at"],
            errors="coerce"
        )
        .dt.strftime("%Y-%m-%d")
        == selected_date_str
    )

    day_df = df_all[date_mask].copy()

else:

    day_df = empty_df()


p_col, d_col, n_col = st.columns([1, 4, 1])


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
        "📅 Working Date",
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
        <div class='nc-section'>
            📋 Entries for
            {st.session_state.selected_date.strftime('%d-%m-%Y')}
        </div>
        """,
        unsafe_allow_html=True
    )


    if not day_df.empty:

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

    else:

        total_gross = 0
        total_net = 0
        cash_sum = 0
        credit_sum = 0


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


    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # TODAY'S RECORDS
    # --------------------------------------------------------

    if day_df.empty:

        st.info(
            "ℹ️ No entries recorded for this date yet."
        )

    else:

        for idx, row in day_df.iterrows():

            is_credit = float(
                row["credit"]
            ) > 0

            card_class = (
                "nc-card-red"
                if is_credit
                else "nc-card-green"
            )

            badge = (
                "🔴 CREDIT / UDHARI"
                if is_credit
                else "🟢 CASH"
            )

            c_info, c_btn1, c_btn2 = st.columns(
                [6, 1, 1]
            )

            with c_info:

                st.markdown(
                    f"""
                    <div class='{card_class}'>

                    <b>👤 {row['name']}</b>
                    ({row['mobile']})
                    &nbsp;&nbsp;|&nbsp;&nbsp;

                    <b>{badge}</b>

                    <br>

                    Service:
                    <b>{row['service']}</b>

                    |

                    Total Fee:
                    <b>₹ {float(row['amount']):,.0f}</b>

                    |

                    Net Profit:
                    <b>₹ {float(row['net_amount']):,.0f}</b>

                    <br>

                    Cash:
                    <b>₹ {float(row['cash']):,.0f}</b>

                    |

                    Credit:
                    <b>₹ {float(row['credit']):,.0f}</b>

                    |

                    Expiry:
                    {row['expiry']}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with c_btn1:

                if st.button(
                    "✏️ Edit",
                    key=f"edit_{idx}",
                    use_container_width=True
                ):

                    st.session_state.editing_row = (
                        row.to_dict()
                    )

                    st.rerun()


            with c_btn2:

                if st.button(
                    "🗑️ Delete",
                    key=f"del_{idx}",
                    use_container_width=True
                ):

                    with st.spinner(
                        "Deleting..."
                    ):

                        payload = {
                            "action": "delete",
                            "row_number": int(
                                row["_row_number"]
                            )
                        }

                        ok, msg = api_post(
                            payload
                        )

                        if ok:

                            fetch_sheet_records.clear()

                            st.session_state.success_message = (
                                "Deleted successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                f"Error: {msg}"
                            )


    st.markdown("---")


    # ========================================================
    # ADD / EDIT FORM
    # ========================================================

    is_editing = (
        st.session_state.editing_row
        is not None
    )

    form_title = (
        "✏️ Edit Customer Entry"
        if is_editing
        else "➕ Add New Customer Entry"
    )

    st.markdown(
        f"""
        <div class='nc-section'>
            {form_title}
        </div>
        """,
        unsafe_allow_html=True
    )


    edit_data = (
        st.session_state.editing_row
        or {}
    )


    left, right = st.columns(2)


    # --------------------------------------------------------
    # LEFT
    # --------------------------------------------------------

    with left:

        mobile_input = st.text_input(
            "Mobile Number*",
            value=edit_data.get(
                "mobile",
                ""
            ),
            key="input_mobile_num"
        )

        clean_mobile = str(
            mobile_input
        ).strip()


        auto_name = ""

        if (
            clean_mobile in mobile_to_name_map
            and not is_editing
        ):

            auto_name = mobile_to_name_map[
                clean_mobile
            ]

            st.success(
                f"🟢 Existing Customer Detected: **{auto_name}**"
            )


        default_name = (
            edit_data.get(
                "name",
                ""
            )
            if is_editing
            else auto_name
        )


        name_input = st.text_input(
            "Customer Name*",
            value=default_name,
            key=f"input_name_{clean_mobile}"
        )


        curr_serv = edit_data.get(
            "service",
            SERVICES[0]
        )


        if curr_serv in SERVICES:

            default_index = SERVICES.index(
                curr_serv
            )

        else:

            default_index = SERVICES.index(
                "Other"
            )


        service_selected = st.selectbox(
            "Search / Select Service*",
            SERVICES,
            index=default_index,
            key="input_service"
        )


        if service_selected == "Other":

            custom_val = (
                curr_serv
                if curr_serv not in SERVICES
                else ""
            )

            custom_service_input = st.text_input(
                "Custom Service Name*",
                value=custom_val,
                key="input_custom_service"
            )

        else:

            custom_service_input = ""


    # --------------------------------------------------------
    # RIGHT
    # --------------------------------------------------------

    with right:

        amount = st.number_input(
            "Total Fee / Gross Amount (₹)*",
            min_value=0,
            step=10,
            value=int(
                edit_data.get(
                    "amount",
                    0
                )
            ),
            key="input_amount"
        )


        net_amount = st.number_input(
            "Net Income / Profit (₹)*",
            min_value=0,
            step=10,
            value=int(
                edit_data.get(
                    "net_amount",
                    0
                )
            ),
            key="input_net_amount"
        )


        # ----------------------------------------------------
        # CASH / CREDIT
        # ----------------------------------------------------

        existing_credit = float(
            edit_data.get(
                "credit",
                0
            )
        )

        existing_cash = float(
            edit_data.get(
                "cash",
                0
            )
        )


        if is_editing:

            if existing_credit > 0:

                default_payment_index = 1

            else:

                default_payment_index = 0

        else:

            default_payment_index = 0


        payment_choice = st.radio(
            "Payment Type*",
            [
                "💵 Cash",
                "🔴 Credit (Udhari)"
            ],
            index=default_payment_index,
            horizontal=True,
            key="input_payment_type"
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


        st.info(
            f"""
            **Payment Split**

            💵 Cash: ₹ {calculated_cash:,}

            🔴 Credit: ₹ {calculated_credit:,}
            """
        )


        has_exp = (
            str(
                edit_data.get(
                    "expiry",
                    "N/A"
                )
            ).strip()
            not in ["N/A", ""]
        )


        has_expiry = st.checkbox(
            "Requires Renewal / Validity?",
            value=has_exp,
            key="input_expiry_check"
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
            key="input_validity_value"
        )


    # ========================================================
    # BUTTONS
    # ========================================================

    b_col1, b_col2 = st.columns(2)


    with b_col1:

        submit_btn_label = (
            "💾 UPDATE ENTRY"
            if is_editing
            else "⚡ SAVE ENTRY"
        )


        if st.button(
            submit_btn_label,
            type="primary",
            use_container_width=True
        ):

            if (
                not str(name_input).strip()
                or not str(mobile_input).strip()
            ):

                st.error(
                    "Please enter Customer Name and Mobile Number."
                )

            else:

                # ------------------------------------------------
                # SERVICE
                # ------------------------------------------------

                final_service = service_selected


                if service_selected == "Other":

                    if not custom_service_input.strip():

                        st.error(
                            "Please enter the Custom Service Name."
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


                # ------------------------------------------------
                # EXPIRY
                # ------------------------------------------------

                expiry = "N/A"


                if has_expiry:

                    base = (
                        st.session_state.selected_date
                    )


                    if validity_unit == "Days":

                        expiry_date = (
                            base
                            + timedelta(
                                days=int(
                                    validity_value
                                )
                            )
                        )

                    elif validity_unit == "Months":

                        expiry_date = (
                            base
                            + relativedelta(
                                months=int(
                                    validity_value
                                )
                            )
                        )

                    else:

                        expiry_date = (
                            base
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
                # CASH / CREDIT
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

                action_type = (
                    "edit"
                    if is_editing
                    else "add"
                )


                payload = {

                    "action": action_type,

                    "created_at": selected_date_str,

                    "name": str(
                        name_input
                    ).strip(),

                    "mobile": str(
                        mobile_input
                    ).strip(),

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

                    "row_number": edit_data.get(
                        "_row_number",
                        0
                    )
                }


                with st.spinner(
                    "Saving to Google Sheet..."
                ):

                    ok, msg = api_post(
                        payload
                    )


                if ok:

                    st.session_state.editing_row = None

                    fetch_sheet_records.clear()


                    ty_msg = (
                        f"Dear "
                        f"{str(name_input).strip()}, "
                        f"Thank you for choosing "
                        f"NOOR CYBER WORLD for "
                        f"{final_service}! "
                        f"Total Amount: Rs.{amount}. "
                        f"We are happy to serve you."
                    )


                    st.session_state.last_saved_wa = (
                        "https://wa.me/91"
                        + str(
                            mobile_input
                        ).strip()
                        + "?text="
                        + quote(ty_msg)
                    )


                    st.session_state.success_message = (
                        "✅ Entry Saved Successfully!"
                    )


                    st.rerun()


                else:

                    st.error(
                        f"Failed to save: {msg}"
                    )


    with b_col2:

        if is_editing:

            if st.button(
                "❌ CANCEL EDIT",
                use_container_width=True
            ):

                st.session_state.editing_row = None

                st.rerun()


    # ========================================================
    # WHATSAPP AFTER SAVE
    # ========================================================

    if "last_saved_wa" in st.session_state:

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        st.success(
            "🎉 Entry successfully saved!"
        )

        st.link_button(
            "💬 SEND THANK YOU SMS / WHATSAPP TO CUSTOMER",
            st.session_state.last_saved_wa,
            use_container_width=True
        )


# ============================================================
# TAB 2 — CREDIT COLLECTION
# ============================================================

with tab2:

    st.markdown(
        "<div class='nc-section'>🔴 Pending Credit / Udhari Collection</div>",
        unsafe_allow_html=True
    )


    credit_df = pd.DataFrame()


    if not df_all.empty:

        credit_df = df_all[
            pd.to_numeric(
                df_all["credit"],
                errors="coerce"
            ).fillna(0) > 0
        ].copy()


    if credit_df.empty:

        st.success(
            "🎉 No pending credit! All payments are clear."
        )

    else:

        total_pending_amount = (
            credit_df["credit"].sum()
        )


        st.error(
            f"⚠️ Total Pending Credit: "
            f"**₹ {total_pending_amount:,.0f}** "
            f"({len(credit_df)} Entries)"
        )


        st.markdown("---")


        for idx, row in credit_df.iterrows():

            col_info, col_msg, col_paid = st.columns(
                [5, 2, 2]
            )


            with col_info:

                st.markdown(
                    f"""
                    <div class='nc-card-red'>

                    <b>🔴 {row['name']}</b>
                    ({row['mobile']})

                    <br>

                    Service:
                    <b>{row['service']}</b>

                    <br>

                    Pending Credit:
                    <b style='color:#ef4444;font-size:18px;'>
                        ₹ {float(row['credit']):,.0f}
                    </b>

                    <br>

                    Date:
                    {row['created_at']}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with col_msg:

                credit_message = (
                    f"Hello {row['name']}, "
                    f"this is a gentle reminder from "
                    f"NOOR CYBER WORLD. "
                    f"Your payment of Rs."
                    f"{int(row['credit'])} "
                    f"for {row['service']} "
                    f"is pending. "
                    f"Please clear your balance "
                    f"as soon as possible. "
                    f"Thank you!"
                )


                wa_credit_url = (
                    "https://wa.me/91"
                    + str(
                        row["mobile"]
                    ).strip()
                    + "?text="
                    + quote(
                        credit_message
                    )
                )


                st.link_button(
                    "💬 SEND REMINDER",
                    wa_credit_url,
                    use_container_width=True
                )


            with col_paid:

                if st.button(
                    "💵 CASH RECEIVED",
                    key=f"cash_received_{idx}",
                    use_container_width=True
                ):

                    with st.spinner(
                        "Updating payment..."
                    ):

                        payload = {

                            "action": "credit_to_cash",

                            "row_number": int(
                                row["_row_number"]
                            ),

                            "amount": str(
                                int(row["amount"])
                            ),

                            "cash": str(
                                int(row["amount"])
                            ),

                            "credit": "0"
                        }


                        ok, msg = api_post(
                            payload
                        )


                        if ok:

                            fetch_sheet_records.clear()

                            st.session_state.success_message = (
                                f"₹ {int(row['credit'])} "
                                f"received from "
                                f"{row['name']}!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                f"Error: {msg}"
                            )


# ============================================================
# TAB 3 — RENEWAL ALERTS
# ============================================================

with tab3:

    st.markdown(
        "<div class='nc-section'>🔔 Renewal Alerts (Next 15 Days)</div>",
        unsafe_allow_html=True
    )


    today = today_ist()

    renewals_list = []


    if not df_all.empty:

        for _, row in df_all.iterrows():

            try:

                exp = str(
                    row["expiry"]
                ).strip()


                if exp and exp != "N/A":

                    exp_date = datetime.strptime(
                        exp[:10],
                        "%Y-%m-%d"
                    ).date()


                    days_left = (
                        exp_date - today
                    ).days


                    if 0 <= days_left <= 15:

                        renewals_list.append(
                            (
                                row,
                                exp_date,
                                days_left
                            )
                        )

            except Exception:

                continue


    if renewals_list:

        st.markdown(
            f"""
            <div class='alert-badge'>
                ⚠️ ALERT:
                {len(renewals_list)}
                Renewal(s) Pending
                in the Next 15 Days!
            </div>
            """,
            unsafe_allow_html=True
        )


        for row, exp_date, days_left in renewals_list:

            formatted = exp_date.strftime(
                "%d-%m-%Y"
            )


            st.markdown(
                f"""
                <div class='nc-card-red'>

                <b>🔴 {row['name']}</b>
                ({row['mobile']})

                <br>

                Service:
                <b>{row['service']}</b>

                <br>

                Expiry Date:
                <b>{formatted}</b>

                ({days_left} days remaining)

                </div>
                """,
                unsafe_allow_html=True
            )


            msg = (
                f"Hello {row['name']}, "
                f"your service {row['service']} "
                f"is expiring on {formatted}. "
                f"Please visit NOOR CYBER WORLD "
                f"to renew it on time."
            )


            wa = (
                "https://wa.me/91"
                + str(
                    row["mobile"]
                ).strip()
                + "?text="
                + quote(msg)
            )


            st.link_button(
                f"💬 SEND RENEWAL SMS TO {row['name']}",
                wa
            )


            st.markdown(
                "<br>",
                unsafe_allow_html=True
            )


    else:

        st.success(
            "🎉 No renewals due in the next 15 days."
        )


# ============================================================
# TAB 4 — SHOP EXPENSES
# ============================================================

with tab4:

    st.markdown(
        "<div class='nc-section'>💸 Shop Expense & Real Profit Tracker</div>",
        unsafe_allow_html=True
    )


    col_exp1, col_exp2 = st.columns(
        [1, 2]
    )


    with col_exp1:

        st.subheader(
            "➕ Add Shop Expense"
        )


        exp_title = st.text_input(
            "Expense Title (e.g. Paper Rim, Rent, Tea)",
            key="exp_title"
        )


        exp_amount = st.number_input(
            "Expense Amount (₹)",
            min_value=0,
            step=10,
            key="exp_amount"
        )


        if st.button(
            "💾 Add Expense",
            type="primary",
            use_container_width=True
        ):

            if (
                exp_title.strip()
                and exp_amount > 0
            ):

                st.session_state.expenses.append(
                    {
                        "date": selected_date_str,
                        "title": exp_title.strip(),
                        "amount": exp_amount
                    }
                )

                st.success(
                    "Expense Added!"
                )

                st.rerun()

            else:

                st.error(
                    "Please enter a valid expense title and amount."
                )


    with col_exp2:

        st.subheader(
            f"📊 Expense Summary for {selected_date_str}"
        )


        current_date_expenses = [
            e
            for e in st.session_state.expenses
            if e["date"] == selected_date_str
        ]


        total_exp = sum(
            e["amount"]
            for e in current_date_expenses
        )


        real_profit = (
            day_net - total_exp
        )


        e_m1, e_m2, e_m3 = st.columns(3)


        e_m1.metric(
            "GROSS NET PROFIT",
            f"₹ {day_net:,}"
        )


        e_m2.metric(
            "TOTAL EXPENSES",
            f"₹ {total_exp:,}"
        )


        e_m3.metric(
            "ACTUAL SAVINGS",
            f"₹ {real_profit:,}"
        )


        st.markdown("---")


        if current_date_expenses:

            st.markdown(
                "**Today's Expense Breakdown:**"
            )


            for exp in current_date_expenses:

                st.write(
                    f"• **{exp['title']}**: "
                    f"₹ {exp['amount']}"
                )

        else:

            st.info(
                "No expenses recorded for today yet."
            )


# ============================================================
# TAB 5 — RECORDS & SEARCH
# ============================================================

with tab5:

    st.markdown(
        "<div class='nc-section'>📂 Customer Records & Instant Search</div>",
        unsafe_allow_html=True
    )


    if df_all.empty:

        st.info(
            "No records available."
        )

    else:

        search_query = st.text_input(
            "🔍 Search Record "
            "(Type Customer Name, Mobile Number, or Service Name)",
            ""
        )


        if search_query.strip():

            q = (
                search_query
                .strip()
                .lower()
            )


            filtered_df = df_all[
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
            ]

        else:

            filtered_df = df_all


        export_df = filtered_df.drop(
            columns=["_row_number"],
            errors="ignore"
        )


        b1, b2 = st.columns(2)


        with b1:

            st.download_button(
                "📥 DOWNLOAD CSV",
                data=export_df.to_csv(
                    index=False
                ).encode("utf-8-sig"),
                file_name=(
                    "NOOR_CYBER_WORLD_RECORDS.csv"
                ),
                mime="text/csv",
                use_container_width=True
            )


        with b2:

            pdf_bytes = generate_pdf(
                export_df
            )


            st.download_button(
                "📄 DOWNLOAD PDF",
                data=pdf_bytes,
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


        for _, row in filtered_df.iterrows():

            is_credit = (
                float(row["credit"]) > 0
            )


            card_class = (
                "nc-card-red"
                if is_credit
                else "nc-card-green"
            )


            badge = (
                "🔴 CREDIT"
                if is_credit
                else "🟢 CASH"
            )


            st.markdown(
                f"""
                <div class='{card_class}'>

                <b>☁️ {row['name']}</b>
                ({row['mobile']})

                &nbsp;|&nbsp;

                {badge}

                <br>

                Service:
                <b>{row['service']}</b>

                |

                Total Fee:
                <b>₹ {float(row['amount']):,.0f}</b>

                |

                Net Profit:
                <b>₹ {float(row['net_amount']):,.0f}</b>

                <br>

                Cash:
                <b>₹ {float(row['cash']):,.0f}</b>

                |

                Credit:
                <b>₹ {float(row['credit']):,.0f}</b>

                <br>

                Date:
                {row['created_at']}

                |

                Expiry:
                {row['expiry']}

                </div>
                """,
                unsafe_allow_html=True
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
