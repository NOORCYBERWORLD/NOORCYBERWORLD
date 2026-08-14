import streamlit as st
import pandas as pd
import requests

from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

from urllib.parse import quote
from io import BytesIO


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NOOR CYBER WORLD",
    page_icon="🖥️",
    layout="wide"
)


# ============================================================
# GOOGLE APPS SCRIPT WEB APP URL
# ============================================================

WEB_APP_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbzpDRn2srFz_HrHgjUs-EpAn3HzUA-gv9Rb5P-apR5uC83JOPYSDjggE8NKl2MC9S3f"
    "/exec"
)


# ============================================================
# IST
# ============================================================

IST_OFFSET = timezone(
    timedelta(hours=5, minutes=30)
)


def get_today_ist():

    return datetime.now(
        IST_OFFSET
    ).date()


# ============================================================
# UI STYLE
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
        linear-gradient(
            135deg,
            #0a0a0c 0%,
            #16181f 50%,
            #0d1117 100%
        );

        color: #ffffff;
    }

    .header-title {
        margin: 0;

        color: #ff2a2a;

        font-size: 32px;

        font-weight: 800;

        letter-spacing: 1.5px;
    }

    .header-subtitle {

        margin: 0;

        color: #3b82f6;

        font-size: 14px;

        font-weight: 600;
    }

    div[data-testid="stMetric"] {

        background:
        rgba(255,255,255,0.04);

        border-radius: 12px;

        padding: 15px;

        border:
        1px solid
        rgba(59,130,246,0.2);
    }

    .stButton > button {

        border-radius: 8px;

        font-weight: bold;
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
    <div
        style="
        padding-top:10px;
        margin-bottom:20px;
        "
    >

        <h1 class="header-title">
            NOOR CYBER WORLD
        </h1>

        <p class="header-subtitle">
            Center Management & Secure Cloud Entry System
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("---")


# ============================================================
# SUCCESS MESSAGE AFTER REFRESH
# ============================================================

if "success_message" in st.session_state:

    st.success(
        st.session_state.success_message
    )

    del st.session_state.success_message


# ============================================================
# GET GOOGLE SHEET DATA
# ============================================================

def get_records():

    columns = [
        "created_at",
        "name",
        "mobile",
        "service",
        "amount",
        "payment",
        "expiry",
        "_row_number"
    ]


    try:

        url = (
            WEB_APP_URL
            + "?t="
            + str(datetime.now().timestamp())
        )


        response = requests.get(
            url,
            timeout=20,
            allow_redirects=True
        )


        if response.status_code != 200:

            return pd.DataFrame(
                columns=columns
            )


        data = response.json()


        if isinstance(data, dict):

            if data.get("success") is False:

                return pd.DataFrame(
                    columns=columns
                )


            return pd.DataFrame(
                columns=columns
            )


        if not isinstance(data, list):

            return pd.DataFrame(
                columns=columns
            )


        if len(data) == 0:

            return pd.DataFrame(
                columns=columns
            )


        df = pd.DataFrame(data)


        # ----------------------------------------------------
        # REQUIRED COLUMNS
        # ----------------------------------------------------

        for column in columns:

            if column not in df.columns:

                df[column] = ""


        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        def clean_date(value):

            if value is None:

                return ""


            text = str(value).strip()


            if text == "":

                return ""


            # YYYY-MM-DD
            if len(text) >= 10:

                first10 = text[:10]

                try:

                    datetime.strptime(
                        first10,
                        "%Y-%m-%d"
                    )

                    return first10

                except Exception:

                    pass


            try:

                parsed = pd.to_datetime(
                    text,
                    errors="coerce"
                )


                if pd.notna(parsed):

                    return parsed.strftime(
                        "%Y-%m-%d"
                    )

            except Exception:

                pass


            return text


        df["created_at"] = (
            df["created_at"]
            .apply(clean_date)
            .astype(str)
        )


        # ----------------------------------------------------
        # AMOUNT
        # ----------------------------------------------------

        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce"
        ).fillna(0)


        # ----------------------------------------------------
        # TEXT COLUMNS
        # ----------------------------------------------------

        for column in [
            "name",
            "mobile",
            "service",
            "payment",
            "expiry"
        ]:

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
            )


        return df[columns]


    except Exception:

        return pd.DataFrame(
            columns=columns
        )


# ============================================================
# GOOGLE POST REQUEST
# ============================================================

def send_to_google(payload):

    try:

        response = requests.post(
            WEB_APP_URL,
            data=payload,
            timeout=20,
            allow_redirects=True
        )


        if response.status_code >= 400:

            return (
                False,
                f"HTTP Error {response.status_code}"
            )


        try:

            result = response.json()


            if isinstance(result, dict):

                if result.get("success"):

                    return (
                        True,
                        result.get(
                            "message",
                            "Success"
                        )
                    )


                return (
                    False,
                    result.get(
                        "error",
                        "Unknown Google Apps Script error"
                    )
                )


        except Exception:

            return (
                True,
                "Saved successfully"
            )


    except Exception as error:

        return (
            False,
            str(error)
        )


# ============================================================
# SERVICES
# ============================================================

services_list = [

    "Aadhaar Card Download / Update",

    "PAN Card New / Correction",

    "Voter ID Card Apply / Correction",

    "Ration Card Services",

    "Ayushman Bharat Card",

    "E-Shram Card",

    "Income Certificate",

    "Caste Certificate",

    "Domicile Certificate",

    "Non-Creamy Layer Certificate",

    "Gazette Notification / Name Change",

    "Passport Application",

    "Driving License (LL/DL) & RC Services",

    "PM Kisan Samman Nidhi / KYC",

    "PF / EPF Withdrawal & Claim",

    "Government Job Online Forms",

    "Admission & Scholarship Forms",

    "Railway / Bus / Air Ticket Booking",

    "Electricity / Gas / Water Bill Payment",

    "Money Transfer (DMT) / AEPS Cash Withdrawal",

    "Mobile / DTH Recharge",

    "Xerox / Color Printout / Lamination / Scanning",

    "Resume / Bio-Data Making",

    "Udyam Aadhaar / MSME Registration",

    "Shop Act License / FSSAI Food License",

    "GST Registration & Return Filing",

    "Income Tax Return (ITR) Filing",

    "Police Verification Application",

    "Digital Signature (DSC)",

    "PVC Card Printing",

    "Other"
]


# ============================================================
# SESSION STATE
# ============================================================

if "selected_view_date" not in st.session_state:

    st.session_state.selected_view_date = (
        get_today_ist()
    )


# ============================================================
# LOAD DATA
# ============================================================

df_all = get_records()


# ============================================================
# SELECTED DATE
# ============================================================

selected_date = (
    st.session_state.selected_view_date
)


date_string = selected_date.strftime(
    "%Y-%m-%d"
)


# ============================================================
# FILTER DAILY DATA
# ============================================================

if not df_all.empty:

    day_df = df_all[
        df_all["created_at"]
        .astype(str)
        .str[:10]
        == date_string
    ].copy()

else:

    day_df = pd.DataFrame()


# ============================================================
# TOTALS
# ============================================================

if not day_df.empty:

    day_total = float(
        day_df["amount"].sum()
    )


    total_cash = float(
        day_df[
            day_df["payment"]
            .str.strip()
            .str.lower()
            == "cash"
        ]["amount"].sum()
    )


    total_online = float(
        day_df[
            day_df["payment"]
            .str.strip()
            .str.lower()
            == "online"
        ]["amount"].sum()
    )

else:

    day_total = 0

    total_cash = 0

    total_online = 0


# ============================================================
# DATE NAVIGATION
# ============================================================

previous_col, date_col, next_col = st.columns(
    [1, 4, 1]
)


with previous_col:

    if st.button(
        "❮ Previous",
        use_container_width=True
    ):

        st.session_state.selected_view_date -= (
            timedelta(days=1)
        )

        st.rerun()


with date_col:

    picked_date = st.date_input(

        (
            "📅 Date: "
            + selected_date.strftime(
                "%B %d, %Y (%A)"
            )
            + f"  |  Balance: ₹ {day_total:,.0f}"
        ),

        value=selected_date,

        key="main_date_picker"
    )


    if picked_date != selected_date:

        st.session_state.selected_view_date = (
            picked_date
        )

        st.rerun()


with next_col:

    if st.button(
        "Next ❯",
        use_container_width=True
    ):

        st.session_state.selected_view_date += (
            timedelta(days=1)
        )

        st.rerun()


st.markdown("---")


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(
    [
        "📊 Daily View & Add Entry",
        "🔔 Renewal Alerts",
        "📂 Full Google Sheet Data"
    ]
)


# ============================================================
# TAB 1
# ============================================================

with tab1:

    st.subheader(
        "📋 Entries for "
        + selected_date.strftime(
            "%d-%m-%Y (%A)"
        )
    )


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    metric1, metric2, metric3 = st.columns(3)


    metric1.metric(
        "Day Total",
        f"₹ {day_total:,.0f}"
    )


    metric2.metric(
        "Day Cash",
        f"₹ {total_cash:,.0f}"
    )


    metric3.metric(
        "Day Online / UPI",
        f"₹ {total_online:,.0f}"
    )


    st.markdown("---")


    # --------------------------------------------------------
    # DAILY ENTRIES
    # --------------------------------------------------------

    if not day_df.empty:

        display_df = day_df.drop(
            columns=["_row_number"],
            errors="ignore"
        )


        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "ℹ️ No entries recorded for this date yet."
        )


    st.markdown("---")


    # ========================================================
    # ADD ENTRY
    # ========================================================

    st.subheader(
        "➕ Add Entry for "
        + selected_date.strftime(
            "%d-%m-%Y"
        )
    )


    left, right = st.columns(2)


    with left:

        customer_name = st.text_input(
            "Customer Name*",
            key="customer_name"
        )


        mobile_number = st.text_input(
            "Mobile Number*",
            key="mobile_number"
        )


        service = st.selectbox(
            "Search / Select Service*",
            services_list,
            key="service"
        )


        custom_service = st.text_input(
            "Type Custom Service Name (If 'Other' Selected)",
            key="custom_service"
        )


    with right:

        amount = st.number_input(
            "Amount (₹)",
            min_value=0,
            step=10,
            key="amount"
        )


        payment_mode = st.radio(
            "Payment Mode",
            [
                "Cash",
                "Online"
            ],
            horizontal=True,
            key="payment_mode"
        )


        requires_expiry = st.checkbox(
            "Requires Renewal / Validity?",
            key="requires_expiry"
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
            "Validity Duration Value",
            min_value=1,
            value=1,
            step=1,
            key="validity_value"
        )


    st.write("")


    # ========================================================
    # SAVE ENTRY
    # ========================================================

    if st.button(
        "💾 Save Entry to Cloud Sheet",
        type="primary",
        use_container_width=True
    ):


        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        if not customer_name.strip():

            st.error(
                "⚠️ Please enter Customer Name!"
            )

            st.stop()


        # ----------------------------------------------------
        # MOBILE
        # ----------------------------------------------------

        clean_mobile = (
            mobile_number
            .replace(" ", "")
            .replace("-", "")
            .replace("+91", "")
        )


        if (
            not clean_mobile.isdigit()
            or len(clean_mobile) != 10
        ):

            st.error(
                "⚠️ Please enter a valid 10-digit Mobile Number!"
            )

            st.stop()


        # ----------------------------------------------------
        # SERVICE
        # ----------------------------------------------------

        final_service = service


        if service == "Other":

            if not custom_service.strip():

                st.error(
                    "⚠️ Please enter custom service name!"
                )

                st.stop()


            final_service = (
                custom_service.strip()
            )


        # ----------------------------------------------------
        # EXPIRY
        # ----------------------------------------------------

        expiry = "N/A"


        if requires_expiry:

            if validity_unit == "Days":

                expiry_date = (
                    selected_date
                    + timedelta(
                        days=int(validity_value)
                    )
                )


            elif validity_unit == "Months":

                expiry_date = (
                    selected_date
                    + relativedelta(
                        months=int(validity_value)
                    )
                )


            else:

                expiry_date = (
                    selected_date
                    + relativedelta(
                        years=int(validity_value)
                    )
                )


            expiry = expiry_date.strftime(
                "%Y-%m-%d"
            )


        # ----------------------------------------------------
        # PAYLOAD
        # ----------------------------------------------------

        payload = {

            "action": "add",

            "created_at": date_string,

            "name": customer_name.strip(),

            "mobile": clean_mobile,

            "service": final_service,

            "amount": str(amount),

            "payment": payment_mode,

            "expiry": expiry
        }


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        with st.spinner(
            "Saving entry to Google Sheet..."
        ):

            success, message = (
                send_to_google(payload)
            )


        if success:

            st.session_state.success_message = (
                f"✅ Entry for "
                f"'{customer_name.strip()}' "
                f"(₹{amount:,.0f}) "
                f"saved successfully!"
            )


            st.rerun()


        else:

            st.error(
                "❌ Google Sheet Error"
            )

            st.code(
                message
            )


# ============================================================
# TAB 2 — RENEWAL ALERTS
# ============================================================

with tab2:

    st.subheader(
        "⚠️ Renewal Alerts (Next 15 Days)"
    )


    today = get_today_ist()

    alerts_found = False


    if (
        not df_all.empty
        and "expiry" in df_all.columns
    ):


        for _, row in df_all.iterrows():

            expiry_value = (
                str(row["expiry"])
                .strip()
            )


            if expiry_value in [
                "",
                "N/A",
                "NA",
                "None",
                "nan"
            ]:

                continue


            try:

                expiry_date = (
                    datetime.strptime(
                        expiry_value[:10],
                        "%Y-%m-%d"
                    ).date()
                )


                days_left = (
                    expiry_date - today
                ).days


                if 0 <= days_left <= 15:

                    alerts_found = True


                    formatted_expiry = (
                        expiry_date.strftime(
                            "%d-%m-%Y"
                        )
                    )


                    customer = str(
                        row["name"]
                    )


                    service_name = str(
                        row["service"]
                    )


                    mobile = str(
                        row["mobile"]
                    )


                    message = (
                        f"Hello {customer}, "
                        f"your {service_name} "
                        f"is expiring on "
                        f"{formatted_expiry}. "
                        f"Please visit "
                        f"NOOR CYBER WORLD "
                        f"for renewal."
                    )


                    whatsapp_url = (
                        "https://wa.me/91"
                        + mobile
                        + "?text="
                        + quote(message)
                    )


                    st.warning(
                        f"🔴 **{customer}** - "
                        f"{service_name} "
                        f"(Expires: "
                        f"{formatted_expiry} | "
                        f"{days_left} Days Left)"
                    )


                    st.markdown(
                        "[💬 Send WhatsApp Message]"
                        f"({whatsapp_url})"
                    )


            except Exception:

                continue


    if not alerts_found:

        st.info(
            "🎉 No renewals due in the next 15 days."
        )


# ============================================================
# TAB 3 — FULL DATA
# ============================================================

with tab3:

    st.subheader(
        "📂 Full Google Sheet Data"
    )


    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    if st.button(
        "🔄 Refresh Data"
    ):

        st.rerun()


    if df_all.empty:

        st.info(
            "No records available in Google Sheet."
        )


    else:

        # ====================================================
        # DOWNLOAD SECTION
        # ====================================================

        download1, download2 = st.columns(2)


        # ----------------------------------------------------
        # CSV
        # ----------------------------------------------------

        with download1:

            csv_df = df_all.drop(
                columns=["_row_number"],
                errors="ignore"
            )


            csv_data = csv_df.to_csv(
                index=False
            ).encode(
                "utf-8-sig"
            )


            st.download_button(

                "📥 Download CSV",

                data=csv_data,

                file_name=(
                    "NOOR_CYBER_WORLD_CUSTOMERS.csv"
                ),

                mime="text/csv",

                use_container_width=True
            )


        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        with download2:

            try:

                from reportlab.lib import colors

                from reportlab.lib.pagesizes import (
                    A4,
                    landscape
                )

                from reportlab.platypus import (
                    SimpleDocTemplate,
                    Table,
                    TableStyle,
                    Paragraph,
                    Spacer
                )

                from reportlab.lib.styles import (
                    getSampleStyleSheet
                )

                from reportlab.lib.enums import (
                    TA_CENTER
                )


                pdf_buffer = BytesIO()


                pdf_doc = SimpleDocTemplate(

                    pdf_buffer,

                    pagesize=landscape(A4),

                    rightMargin=20,

                    leftMargin=20,

                    topMargin=20,

                    bottomMargin=20
                )


                styles = (
                    getSampleStyleSheet()
                )


                title_style = (
                    styles["Title"]
                )

                title_style.alignment = (
                    TA_CENTER
                )


                elements = []


                elements.append(
                    Paragraph(
                        "NOOR CYBER WORLD",
                        title_style
                    )
                )


                elements.append(
                    Spacer(1, 8)
                )


                elements.append(
                    Paragraph(
                        "Customer Records",
                        styles["Heading2"]
                    )
                )


                elements.append(
                    Spacer(1, 10)
                )


                pdf_df = df_all.drop(
                    columns=["_row_number"],
                    errors="ignore"
                ).copy()


                pdf_df = pdf_df.rename(
                    columns={
                        "created_at": "Date",
                        "name": "Customer",
                        "mobile": "Mobile",
                        "service": "Service",
                        "amount": "Amount",
                        "payment": "Payment",
                        "expiry": "Expiry"
                    }
                )


                pdf_data = [
                    list(pdf_df.columns)
                ]


                for _, row in pdf_df.iterrows():

                    pdf_data.append(
                        [
                            str(value)
                            for value
                            in row.tolist()
                        ]
                    )


                pdf_table = Table(
                    pdf_data,
                    repeatRows=1
                )


                pdf_table.setStyle(
                    TableStyle([

                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor(
                                "#1f2937"
                            )
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
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey
                        ),

                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            7
                        ),

                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "MIDDLE"
                        ),

                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [
                                colors.white,
                                colors.HexColor(
                                    "#f3f4f6"
                                )
                            ]
                        )

                    ])
                )


                elements.append(
                    pdf_table
                )


                pdf_doc.build(
                    elements
                )


                pdf_buffer.seek(0)


                st.download_button(

                    "📄 Download PDF",

                    data=pdf_buffer,

                    file_name=(
                        "NOOR_CYBER_WORLD_CUSTOMERS.pdf"
                    ),

                    mime="application/pdf",

                    use_container_width=True
                )


            except ImportError:

                st.error(
                    "PDF बनाने के लिए "
                    "`reportlab` install करना होगा."
                )


        st.markdown("---")


        # ====================================================
        # EDIT CUSTOMER DATA
        # ====================================================

        st.subheader(
            "✏️ Edit Customer Data"
        )


        st.caption(
            "नीचे table में customer की information "
            "edit करें और फिर Save Changes दबाएँ."
        )


        editable_df = df_all.drop(
            columns=["_row_number"],
            errors="ignore"
        ).copy()


        edited_df = st.data_editor(

            editable_df,

            use_container_width=True,

            hide_index=True,

            num_rows="fixed",

            key="customer_editor",

            column_config={

                "created_at":
                    st.column_config.TextColumn(
                        "Date"
                    ),

                "name":
                    st.column_config.TextColumn(
                        "Customer Name"
                    ),

                "mobile":
                    st.column_config.TextColumn(
                        "Mobile"
                    ),

                "service":
                    st.column_config.TextColumn(
                        "Service"
                    ),

                "amount":
                    st.column_config.NumberColumn(
                        "Amount ₹",
                        min_value=0
                    ),

                "payment":
                    st.column_config.SelectboxColumn(
                        "Payment",
                        options=[
                            "Cash",
                            "Online"
                        ]
                    ),

                "expiry":
                    st.column_config.TextColumn(
                        "Expiry"
                    )
            }
        )


        st.write("")


        # ====================================================
        # SAVE EDITED DATA
        # ====================================================

        if st.button(
            "💾 Save Changes to Google Sheet",
            type="primary",
            use_container_width=True
        ):


            changes_found = False

            errors = []


            for index in range(
                len(edited_df)
            ):


                original = (
                    editable_df.iloc[index]
                )


                edited = (
                    edited_df.iloc[index]
                )


                changed = False


                for column in editable_df.columns:

                    old_value = str(
                        original[column]
                    ).strip()


                    new_value = str(
                        edited[column]
                    ).strip()


                    if old_value != new_value:

                        changed = True

                        break


                if not changed:

                    continue


                changes_found = True


                row_number = int(
                    df_all.iloc[index][
                        "_row_number"
                    ]
                )


                update_payload = {

                    "action": "update",

                    "row_number": str(
                        row_number
                    ),

                    "created_at": str(
                        edited["created_at"]
                    ),

                    "name": str(
                        edited["name"]
                    ),

                    "mobile": str(
                        edited["mobile"]
                    ),

                    "service": str(
                        edited["service"]
                    ),

                    "amount": str(
                        edited["amount"]
                    ),

                    "payment": str(
                        edited["payment"]
                    ),

                    "expiry": str(
                        edited["expiry"]
                    )
                }


                success, message = (
                    send_to_google(
                        update_payload
                    )
                )


                if not success:

                    errors.append(
                        f"Row {row_number}: "
                        f"{message}"
                    )


            if not changes_found:

                st.info(
                    "ℹ️ No changes detected."
                )


            elif errors:

                st.error(
                    "❌ Some changes could not be saved."
                )


                for error in errors:

                    st.error(error)


            else:

                st.session_state.success_message = (
                    "✅ Customer data updated successfully!"
                )


                st.rerun()


        # ====================================================
        # CURRENT DATA
        # ====================================================

        st.markdown("---")


        st.subheader(
            "📋 Current Customer Records"
        )


        final_display = df_all.drop(
            columns=["_row_number"],
            errors="ignore"
        )


        st.dataframe(
            final_display,
            use_container_width=True,
            hide_index=True
        )
