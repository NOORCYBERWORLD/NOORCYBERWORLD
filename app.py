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
    "created_at", "name", "mobile", "service",
    "amount", "net_amount", "cash", "credit",
    "expiry", "_row_number"
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


def today_ist():
    return datetime.now(IST).date()


def services():
    return sorted(
        set(
            BASE_SERVICES +
            st.session_state.custom_services
        ),
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

            df[col] = (
                0
                if col in [
                    "amount",
                    "net_amount",
                    "cash",
                    "credit"
                ]
                else ""
            )

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

    # IMPORTANT:
    # Do NOT use pandas datetime conversion here.
    # It can shift Google Sheet dates by one day.

    raw = (
        df["created_at"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["created_at"] = raw.str[:10]

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

    return df[COLUMNS]


@st.cache_data(ttl=5)
def get_records():

    try:

        r = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_records",
                "t": int(
                    datetime.now().timestamp()
                )
            },
            timeout=20
        )

        if r.status_code != 200:
            return empty_df()

        data = r.json()

        return clean_df(
            pd.DataFrame(data)
        )

    except Exception:

        return empty_df()


def get_expenses():

    try:

        r = requests.get(
            WEB_APP_URL,
            params={
                "action": "get_expenses",
                "t": int(
                    datetime.now().timestamp()
                )
            },
            timeout=20
        )

        if r.status_code != 200:
            return []

        data = r.json()

        return (
            data
            if isinstance(data, list)
            else []
        )

    except Exception:

        return []


def post_api(payload):

    try:

        r = requests.post(
            WEB_APP_URL,
            data=json.dumps(payload),
            headers={
                "Content-Type":
                "application/json"
            },
            timeout=20
        )

        try:

            data = r.json()

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
                r.status_code < 400,
                "Success"
            )

    except Exception as e:

        return False, str(e)


# ============================================================
# STYLE + HEADER
# ============================================================

st.markdown(
"""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&display=swap'
);

.stApp{
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

.block-container{
    max-width:1450px;
    padding-top:1rem;
    padding-bottom:3rem;
}

.nc-header{
    text-align:center;
    padding:8px 10px 8px;
    margin:0 0 6px;
}

.nc-title{
    font-family:Orbitron,Arial,sans-serif;
    font-size:44px;
    line-height:1.2;
    font-weight:800;
    letter-spacing:3px;
    color:#22d3ee;
    text-shadow:
        0 0 18px rgba(34,211,238,.35);
}

.nc-main-title{
    font-family:Inter,Arial,sans-serif;
    font-size:21px;
    font-weight:800;
    letter-spacing:2px;
    color:#ffffff;
    margin-top:2px;
}

.nc-sub{
    font-size:11px;
    letter-spacing:2px;
    color:#94a3b8;
    margin-top:3px;
}

.nc-income{
    display:flex;
    justify-content:flex-end;
    align-items:center;
    gap:10px;

    background:rgba(15,23,42,.88);
    border:1px solid rgba(34,211,238,.25);
    border-radius:12px;

    padding:7px 13px;
    margin:4px 0 8px;

    font-size:12px;
    line-height:1.5;
    white-space:nowrap;
}

.nc-income .label{
    color:#cbd5e1;
    font-weight:700;
}

.nc-income .profit{
    color:#22c55e;
    font-weight:800;
}

.nc-income .sep{
    color:#64748b;
}

.nc-top{
    background:rgba(15,23,42,.88);
    border:1px solid rgba(34,211,238,.25);
    border-radius:12px;
    padding:7px 13px;
    text-align:right;
    font-size:12px;
    line-height:1.8;
}

.profit{
    color:#22c55e;
    font-weight:800;
}

.cash{
    color:#22c55e;
    font-weight:800;
}

.credit{
    color:#ef4444;
    font-weight:800;
}

.nc-section{
    font-family:Orbitron,sans-serif;
    font-size:18px;
    font-weight:700;
    color:#e2e8f0;
    margin:8px 0 14px;
}

.nc-green{
    background:
        linear-gradient(
            145deg,
            rgba(22,101,52,.30),
            rgba(15,23,42,.88)
        );

    border:1px solid rgba(34,197,94,.42);
    border-left:5px solid #22c55e;
    border-radius:12px;
    padding:10px 13px;
    margin:5px 0;
}

.nc-red{
    background:
        linear-gradient(
            145deg,
            rgba(127,29,29,.30),
            rgba(15,23,42,.88)
        );

    border:1px solid rgba(239,68,68,.42);
    border-left:5px solid #ef4444;
    border-radius:12px;
    padding:10px 13px;
    margin:5px 0;
}

div[data-testid="stMetric"]{
    background:
        linear-gradient(
            145deg,
            rgba(15,23,42,.95),
            rgba(30,41,59,.75)
        );

    border:1px solid rgba(96,165,250,.20);
    border-radius:15px;
    padding:15px;
}

.stButton>button{
    border-radius:9px;
    font-weight:700;
}

</style>
""",
unsafe_allow_html=True
)


# ============================================================
# HEADER
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
# LOAD DATA
# ============================================================

df = get_records()
expenses = get_expenses()

if df.empty:
    df = empty_df()


selected_date = (
    st.session_state.selected_date
)

selected_date_str = (
    selected_date.strftime(
        "%Y-%m-%d"
    )
)


if not df.empty:

    day_df = df[
        df["created_at"]
        .str[:10]
        == selected_date_str
    ].copy()

else:

    day_df = empty_df()


# ============================================================
# TOP NET-INCOME SUMMARY
# ============================================================

if not df.empty:

    today_s = (
        today_ist()
        .strftime("%Y-%m-%d")
    )

    month_s = (
        today_ist()
        .strftime("%Y-%m")
    )

    year_s = (
        today_ist()
        .strftime("%Y")
    )

    today_net = df.loc[
        df["created_at"].str[:10]
        == today_s,
        "net_amount"
    ].sum()

    month_net = df.loc[
        df["created_at"].str[:7]
        == month_s,
        "net_amount"
    ].sum()

    year_net = df.loc[
        df["created_at"].str[:4]
        == year_s,
        "net_amount"
    ].sum()

else:

    today_net = 0
    month_net = 0
    year_net = 0


st.markdown(
f"""
<div class="nc-income">

    <span class="label">
        📅 TODAY NET INCOME:
    </span>

    <span class="profit">
        ₹ {today_net:,.0f}
    </span>

    <span class="sep">|</span>

    <span class="label">
        🗓️ MONTH NET INCOME:
    </span>

    <span class="profit">
        ₹ {month_net:,.0f}
    </span>

    <span class="sep">|</span>

    <span class="label">
        📊 YEAR NET INCOME:
    </span>

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

p, d, n = st.columns([1,4,1])

with p:

    if st.button(
        "❮ PREVIOUS DAY",
        use_container_width=True
    ):

        st.session_state.selected_date -= (
            timedelta(days=1)
        )

        st.rerun()


with d:

    picked = st.date_input(
        "Working Date",
        value=selected_date,
        label_visibility="collapsed"
    )

    if picked != selected_date:

        st.session_state.selected_date = (
            picked
        )

        st.rerun()


with n:

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

    total_gross = (
        int(day_df["amount"].sum())
        if not day_df.empty
        else 0
    )

    total_net = (
        int(day_df["net_amount"].sum())
        if not day_df.empty
        else 0
    )

    cash_sum = (
        int(day_df["cash"].sum())
        if not day_df.empty
        else 0
    )

    credit_sum = (
        int(day_df["credit"].sum())
        if not day_df.empty
        else 0
    )

    a, b, c, e = st.columns(4)

    a.metric(
        "TOTAL COLLECTION",
        f"₹ {total_gross:,}"
    )

    b.metric(
        "CASH RECEIVED",
        f"₹ {cash_sum:,}"
    )

    c.metric(
        "PENDING CREDIT",
        f"₹ {credit_sum:,}"
    )

    e.metric(
        "NET PROFIT",
        f"₹ {total_net:,}"
    )

    st.markdown("---")

    if day_df.empty:

        st.info(
            "ℹ️ No entries recorded for this date yet."
        )

    else:

        table = day_df.drop(
            columns=["_row_number"]
        ).copy()

        table.columns = [
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

            table[col] = table[col].map(
                lambda x:
                    f"₹ {float(x):,.0f}"
            )

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            "#### Entry Actions"
        )

        for _, row in day_df.iterrows():

            rn = int(
                row["_row_number"]
            )

            cls = (
                "nc-red"
                if float(row["credit"]) > 0
                else "nc-green"
            )

            info, edit_col, del_col = (
                st.columns([8,1,1])
            )

            with info:

                st.markdown(
                    f"""
                    <div class="{cls}">

                    <b>{row['name']}</b>
                    • {row['mobile']}
                    • {row['service']}

                    &nbsp; | &nbsp;

                    Amount ₹
                    {float(row['amount']):,.0f}

                    &nbsp; | &nbsp;

                    Cash ₹
                    {float(row['cash']):,.0f}

                    &nbsp; | &nbsp;

                    Credit ₹
                    {float(row['credit']):,.0f}

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with edit_col:

                if st.button(
                    "✏️",
                    key=f"day_edit_{rn}"
                ):

                    st.session_state.editing_row = (
                        row.to_dict()
                    )

                    st.rerun()

            with del_col:

                if st.button(
                    "🗑️",
                    key=f"day_del_{rn}"
                ):

                    st.session_state.confirm_delete = rn

                    st.rerun()


    if st.session_state.confirm_delete:

        rn = (
            st.session_state.confirm_delete
        )

        st.warning(
            "⚠️ Confirm deletion of this customer entry."
        )

        y, no = st.columns(2)

        with y:

            if st.button(
                "YES, DELETE",
                type="primary",
                use_container_width=True
            ):

                ok, msg = post_api({
                    "action": "delete",
                    "row_number": rn
                })

                if ok:

                    st.session_state.confirm_delete = None

                    get_records.clear()

                    st.session_state.success_message = (
                        "Entry deleted successfully."
                    )

                    st.rerun()

                else:

                    st.error(msg)

        with no:

            if st.button(
                "NO, CANCEL",
                use_container_width=True
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

    st.markdown(
        "<div class='nc-section'>{}</div>".format(
            "✏️ EDIT CUSTOMER ENTRY"
            if editing
            else
            "➕ ADD NEW CUSTOMER ENTRY"
        ),
        unsafe_allow_html=True
    )


    left, right = st.columns(2)


    with left:

        mobile = st.text_input(
            "Mobile Number *",
            value=str(
                old.get(
                    "mobile",
                    ""
                )
            ),
            key="mobile_field"
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
            key=f"name_field_{mobile}_{editing}"
        ).strip()


        svcs = services()

        old_service = str(
            old.get(
                "service",
                svcs[0]
            )
        )

        idx = (
            svcs.index(old_service)
            if old_service in svcs
            else svcs.index("Other")
        )


        selected_service = st.selectbox(
            "Search / Select Service *",
            svcs,
            index=idx,
            key="service_field"
        )


        custom_service = ""

        if selected_service == "Other":

            custom_service = st.text_input(
                "Custom Service Name *",
                value=(
                    old_service
                    if old_service not in svcs
                    else ""
                ),
                key="custom_service_field"
            ).strip()


    with right:

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
            key="amount_field"
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
            key="net_field"
        )


        old_credit = float(
            old.get(
                "credit",
                0
            )
        )

        pay_index = (
            1
            if old_credit > 0
            else 0
        )


        payment = st.radio(
            "Payment Type *",
            [
                "💵 CASH",
                "🔴 CREDIT (UDHARI)"
            ],
            index=pay_index,
            horizontal=True,
            key="payment_field"
        )


        if "CREDIT" in payment:

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
            💵 Cash: ₹ {cash_value:,}

            🔴 Credit: ₹ {credit_value:,}
            """
        )


        expiry_exists = (
            str(
                old.get(
                    "expiry",
                    "N/A"
                )
            ).strip()
            not in ["", "N/A"]
        )


        has_expiry = st.checkbox(
            "Requires Renewal / Validity?",
            value=expiry_exists,
            key="has_expiry"
        )


        unit = st.selectbox(
            "Validity Unit",
            [
                "Days",
                "Months",
                "Years"
            ],
            index=1,
            key="validity_unit"
        )


        duration = st.number_input(
            "Validity Duration",
            min_value=1,
            value=1,
            step=1,
            key="validity_duration"
        )


    save, cancel = st.columns(2)


    with save:

        label = (
            "💾 UPDATE ENTRY"
            if editing
            else
            "⚡ SAVE ENTRY"
        )


        if st.button(
            label,
            type="primary",
            use_container_width=True
        ):

            if not name or not mobile:

                st.error(
                    "Please enter Customer Name and Mobile Number."
                )

                st.stop()


            final_service = (
                selected_service
            )


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


            expiry = "N/A"


            if has_expiry:

                base = selected_date


                if unit == "Days":

                    exp = (
                        base
                        + timedelta(
                            days=int(duration)
                        )
                    )

                elif unit == "Months":

                    exp = (
                        base
                        + relativedelta(
                            months=int(duration)
                        )
                    )

                else:

                    exp = (
                        base
                        + relativedelta(
                            years=int(duration)
                        )
                    )


                expiry = exp.strftime(
                    "%Y-%m-%d"
                )


            payload = {

                "action":
                    "edit"
                    if editing
                    else
                    "add",

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


            ok, msg = post_api(
                payload
            )


            if ok:

                get_records.clear()

                st.session_state.editing_row = None

                st.session_state.last_saved_wa = (
                    "https://wa.me/91"
                    + mobile
                    + "?text="
                    + quote(
                        f"Dear {name}, "
                        f"Thank you for choosing "
                        f"NOOR CYBER WORLD for "
                        f"{final_service}! "
                        f"Total Amount: "
                        f"Rs.{int(amount)}."
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


    with cancel:

        if (
            editing
            and st.button(
                "❌ CANCEL EDIT",
                use_container_width=True
            )
        ):

            st.session_state.editing_row = None

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
        """
        <div class="nc-section">
            🔴 PENDING CREDIT / UDHARI COLLECTION
        </div>
        """,
        unsafe_allow_html=True
    )


    credit_df = (
        df[df["credit"] > 0].copy()
        if not df.empty
        else empty_df()
    )


    if credit_df.empty:

        st.success(
            "🎉 No pending credit! All payments are clear."
        )

    else:

        pending = int(
            credit_df["credit"].sum()
        )

        st.error(
            f"⚠️ Total Pending Credit: "
            f"₹ {pending:,} "
            f"({len(credit_df)} Entries)"
        )


        for _, row in credit_df.iterrows():

            rn = int(
                row["_row_number"]
            )

            c1, c2, c3 = st.columns(
                [6,2,2]
            )


            with c1:

                st.markdown(
                    f"""
                    <div class="nc-red">

                    <b>🔴 {row['name']}</b>
                    ({row['mobile']})

                    <br>

                    Service:
                    <b>{row['service']}</b>

                    <br>

                    Pending Credit:

                    <b style="
                        font-size:18px;
                        color:#ef4444;
                    ">
                        ₹ {float(row['credit']):,.0f}
                    </b>

                    <br>

                    Date:
                    {row['created_at']}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with c2:

                msg = quote(
                    f"Hello {row['name']}, "
                    f"this is a gentle reminder from "
                    f"NOOR CYBER WORLD. "
                    f"Your payment of "
                    f"Rs.{int(row['credit'])} "
                    f"for {row['service']} "
                    f"is pending. "
                    f"Please clear your balance. "
                    f"Thank you!"
                )


                st.link_button(
                    "💬 SEND REMINDER",
                    f"https://wa.me/91"
                    f"{str(row['mobile']).strip()}"
                    f"?text={msg}",
                    use_container_width=True
                )


            with c3:

                if st.button(
                    "💵 CASH RECEIVED",
                    key=f"credit_cash_{rn}",
                    use_container_width=True
                ):

                    ok, msg = post_api({
                        "action":
                            "credit_to_cash",

                        "row_number":
                            rn
                    })


                    if ok:

                        get_records.clear()

                        st.session_state.success_message = (
                            f"₹ {int(row['credit'])} "
                            f"received from "
                            f"{row['name']}."
                        )

                        st.rerun()

                    else:

                        st.error(msg)


# ============================================================
# TAB 3 - RENEWALS
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


    alerts = []

    today = today_ist()


    for _, row in df.iterrows():

        exp = str(
            row["expiry"]
        ).strip()


        if exp and exp != "N/A":

            try:

                ed = datetime.strptime(
                    exp[:10],
                    "%Y-%m-%d"
                ).date()

                left = (
                    ed - today
                ).days


                if 0 <= left <= 15:

                    alerts.append(
                        (
                            row,
                            ed,
                            left
                        )
                    )

            except Exception:

                pass


    if not alerts:

        st.success(
            "🎉 No renewals due in the next 15 days."
        )

    else:

        st.warning(
            f"⚠️ {len(alerts)} renewal(s) pending."
        )


        for row, ed, left in alerts:

            date_text = (
                ed.strftime(
                    "%d-%m-%Y"
                )
            )


            st.markdown(
                f"""
                <div class="nc-red">

                <b>🔴 {row['name']}</b>
                ({row['mobile']})

                <br>

                Service:
                <b>{row['service']}</b>

                <br>

                Expiry:
                <b>{date_text}</b>
                —
                {left} days remaining

                </div>
                """,
                unsafe_allow_html=True
            )


            msg = quote(
                f"Hello {row['name']}, "
                f"your service {row['service']} "
                f"is expiring on {date_text}. "
                f"Please visit "
                f"NOOR CYBER WORLD "
                f"to renew it."
            )


            st.link_button(
                f"💬 SEND RENEWAL WHATSAPP TO "
                f"{row['name']}",
                f"https://wa.me/91"
                f"{str(row['mobile']).strip()}"
                f"?text={msg}"
            )
