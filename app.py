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
# INDIA TIME
# ============================================================

IST = timezone(
    timedelta(hours=5, minutes=30)
)


def today_ist():

    return datetime.now(IST).date()


# ============================================================
# PAGE CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
        linear-gradient(
            135deg,
            #090a0d 0%,
            #15171d 50%,
            #0b0d12 100%
        );
    }

    .main-title {
        color: #ff2525;
        font-size: 34px;
        font-weight: 900;
        margin-bottom: 0;
    }

    .sub-title {
        color: #3b82f6;
        font-size: 14px;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(59,130,246,0.25);
        border-radius: 12px;
        padding: 15px;
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
    <div>
        <div class="main-title">
            NOOR CYBER WORLD
        </div>

        <div class="sub-title">
            Customer Management & Secure Cloud Entry System
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# SUCCESS MESSAGE
# ============================================================

if "success_message" in st.session_state:

    st.success(
        st.session_state.success_message
    )

    del st.session_state.success_message


# ============================================================
# SERVICES
# ============================================================

SERVICES = [

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
# GET DATA FROM GOOGLE SHEET
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
            timeout=30
        )

        if response.status_code != 200:

            return pd.DataFrame(
                columns=columns
            )

        data = response.json()

        if isinstance(data, dict):

            if data.get("success") is False:

                st.error(
                    "Google Sheet Error: "
                    + str(
                        data.get(
                            "error",
                            "Unknown error"
                        )
                    )
                )

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
        # MAKE ALL REQUIRED COLUMNS
        # ----------------------------------------------------

        for column in columns:

            if column not in df.columns:

                df[column] = ""


        # ----------------------------------------------------
        # DATE CLEANING
        # ----------------------------------------------------

        def clean_date(value):

            if value is None:
                return ""

            text = str(value).strip()

            if text == "":
                return ""

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

            return text[:10]


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
        # TEXT
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


        # ----------------------------------------------------
        # ROW NUMBER SAFETY
        # ----------------------------------------------------

        if "_row_number" not in df.columns:

            df["_row_number"] = range(
                2,
                len(df) + 2
            )


        # If Apps Script somehow sends empty row numbers
        for i in range(len(df)):

            value = df.iloc[i]["_row_number"]

            try:

                if str(value).strip() == "":
                    df.at[i, "_row_number"] = i + 2

            except Exception:

                df.at[i, "_row_number"] = i + 2


        return df[columns]


    except Exception as error:

        st.error(
            "❌ Could not load Google Sheet data."
        )

        st.caption(
            str(error)
        )

        return pd.DataFrame(
            columns=columns
        )


# ============================================================
# SEND DATA TO GOOGLE
# ============================================================

def send_to_google(payload):

    try:

        response = requests.post(
            WEB_APP_URL,
            data=payload,
            timeout=30
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
                        "Google Apps Script error"
                    )
                )

        except Exception:

            # Google Apps Script may return
            # redirect/HTML in some cases.
            return (
                True,
                "Request completed"
            )

        return (
            True,
            "Success"
        )

    except Exception as error:

        return (
            False,
            str(error)
        )


# ============================================================
# SESSION DATE
# ============================================================

if "selected_date" not in st.session_state:

    st.session_state.selected_date = today_ist()


# ============================================================
# LOAD DATA
# ============================================================

df_all = get_records()


# ============================================================
# DATE
# ============================================================

selected_date = (
    st.session_state.selected_date
)

selected_date_string = (
    selected_date.strftime("%Y-%m-%d")
)


# ============================================================
# FILTER DAILY DATA
# ============================================================

if not df_all.empty:

    day_df = df_all[
        df_all["created_at"]
        .astype(str)
        .str[:10]
        == selected_date_string
    ].copy()

else:

    day_df = pd.DataFrame(
        columns=df_all.columns
    )


# ============================================================
# DAILY TOTALS
# ============================================================

if not day_df.empty:

    day_total = float(
        day_df["amount"].sum()
    )

    cash_df = day_df[
        day_df["payment"]
        .str.lower()
        .str.strip()
        == "cash"
    ]

    online_df = day_df[
        day_df["payment"]
        .str.lower()
        .str.strip()
        .isin([
            "online",
            "upi"
        ])
    ]

    cash_total = float(
        cash_df["amount"].sum()
    )

    online_total = float(
        online_df["amount"].sum()
    )

else:

    day_total = 0
    cash_total = 0
    online_total = 0


# ============================================================
# DATE NAVIGATION
# ============================================================

col_prev, col_date, col_next = st.columns(
    [1, 4, 1]
)


with col_prev:

    if st.button(
        "❮ Previous",
        use_container_width=True
    ):

        st.session_state.selected_date = (
            selected_date
            - timedelta(days=1)
        )

        st.rerun()


with col_date:

    new_date = st.date_input(
        "📅 Select Date",
        value=selected_date
    )

    if new_date != selected_date:

        st.session_state.selected_date = (
            new_date
        )

        st.rerun()


with col_next:

    if st.button(
        "Next ❯",
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

tab_daily, tab_alerts, tab_data = st.tabs(
    [
        "📊 Daily View & Add Entry",
        "🔔 Renewal Alerts",
        "📂 Full Google Sheet Data"
    ]
)


# ============================================================
# TAB 1
# ============================================================

with tab_daily:

    st.subheader(
        "📋 Entries for "
        + selected_date.strftime(
            "%d-%m-%Y (%A)"
        )
    )


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    m1, m2, m3 = st.columns(3)

    with m1:

        st.metric(
            "Day Total",
            f"₹ {day_total:,.0f}"
        )

    with m2:

        st.metric(
            "Day Cash",
            f"₹ {cash_total:,.0f}"
        )

    with m3:

        st.metric(
            "Day Online / UPI",
            f"₹ {online_total:,.0f}"
        )


    st.markdown("---")


    # --------------------------------------------------------
    # DAILY ENTRIES
    # --------------------------------------------------------

    if day_df.empty:

        st.info(
            "ℹ️ No entries recorded for this date yet."
        )

    else:

        daily_display = day_df.drop(
            columns=["_row_number"],
            errors="ignore"
        )

        daily_display = daily_display.rename(
            columns={
                "created_at": "Date",
                "name": "Customer",
                "mobile": "Mobile",
                "service": "Service",
                "amount": "Amount ₹",
                "payment": "Payment",
                "expiry": "Expiry"
            }
        )

        st.dataframe(
            daily_display,
            use_container_width=True,
            hide_index=True
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
            "Customer Name*"
        )

        mobile_number = st.text_input(
            "Mobile Number*"
        )

        service = st.selectbox(
            "Search / Select Service*",
            SERVICES
        )

        custom_service = st.text_input(
            "Type Custom Service Name "
            "(If 'Other' Selected)"
        )


    with right:

        amount = st.number_input(
            "Amount (₹)",
            min_value=0,
            value=0,
            step=10
        )

        payment_mode = st.radio(
            "Payment Mode",
            [
                "Cash",
                "Online"
            ],
            horizontal=True
        )

        requires_expiry = st.checkbox(
            "Requires Renewal / Validity?"
        )

        validity_unit = st.selectbox(
            "Validity Unit",
            [
                "Days",
                "Months",
                "Years"
            ],
            index=1
        )

        validity_value = st.number_input(
            "Validity Duration",
            min_value=1,
            value=1,
            step=1
        )


    # ========================================================
    # SAVE
    # ========================================================

    if st.button(
        "💾 Save Customer Entry",
        type="primary",
        use_container_width=True
    ):

        # ----------------------------------------------------
        # CUSTOMER NAME
        # ----------------------------------------------------

        if not customer_name.strip():

            st.error(
                "⚠️ Customer Name is required."
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
                "⚠️ Enter a valid 10-digit mobile number."
            )

            st.stop()


        # ----------------------------------------------------
        # SERVICE
        # ----------------------------------------------------

        final_service = service

        if service == "Other":

            if not custom_service.strip():

                st.error(
                    "⚠️ Enter custom service name."
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
                        days=int(
                            validity_value
                        )
                    )
                )

            elif validity_unit == "Months":

                expiry_date = (
                    selected_date
                    + relativedelta(
                        months=int(
                            validity_value
                        )
                    )
                )

            else:

                expiry_date = (
                    selected_date
                    + relativedelta(
                        years=int(
                            validity_value
                        )
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

            "created_at":
                selected_date_string,

            "name":
                customer_name.strip(),

            "mobile":
                clean_mobile,

            "service":
                final_service,

            "amount":
                str(amount),

            "payment":
                payment_mode,

            "expiry":
                expiry
        }


        # ----------------------------------------------------
        # SEND
        # ----------------------------------------------------

        with st.spinner(
            "Saving customer..."
        ):

            success, message = (
                send_to_google(
                    payload
                )
            )


        if success:

            st.session_state.success_message = (
                f"✅ Entry for "
                f"'{customer_name.strip()}' "
                f"(₹{amount:,.0f}) saved successfully!"
            )

            st.rerun()

        else:

            st.error(
                "❌ Entry could not be saved."
            )

            st.code(message)


# ============================================================
# TAB 2 — RENEWAL ALERTS
# ============================================================

with tab_alerts:

    st.subheader(
        "🔔 Renewal Alerts"
    )

    st.caption(
        "Next 15 days"
    )


    today = today_ist()

    found_alert = False


    if not df_all.empty:

        for _, row in df_all.iterrows():

            expiry = str(
                row["expiry"]
            ).strip()


            if expiry in [
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
                        expiry[:10],
                        "%Y-%m-%d"
                    ).date()
                )

            except Exception:

                continue


            days_left = (
                expiry_date - today
            ).days


            if 0 <= days_left <= 15:

                found_alert = True


                customer = str(
                    row["name"]
                )

                service_name = str(
                    row["service"]
                )

                mobile = str(
                    row["mobile"]
                )


                expiry_display = (
                    expiry_date.strftime(
                        "%d-%m-%Y"
                    )
                )


                if days_left == 0:

                    status = "EXPIRES TODAY"

                elif days_left == 1:

                    status = "1 DAY LEFT"

                else:

                    status = (
                        f"{days_left} DAYS LEFT"
                    )


                st.warning(
                    f"🔴 **{customer}**  |  "
                    f"{service_name}  |  "
                    f"Expiry: {expiry_display}  |  "
                    f"**{status}**"
                )


                message = (
                    f"Hello {customer}, "
                    f"your {service_name} "
                    f"is expiring on "
                    f"{expiry_display}. "
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


                st.markdown(
                    f"[💬 Send WhatsApp Message]"
                    f"({whatsapp_url})"
                )


    if not found_alert:

        st.success(
            "🎉 No renewals due in the next 15 days."
        )


# ============================================================
# TAB 3 — FULL DATA
# ============================================================

with tab_data:

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
            "No customer records found."
        )

    else:

        # ====================================================
        # EXPORT
        # ====================================================

        st.markdown(
            "### 📥 Download"
        )


        export_df = df_all.drop(
            columns=["_row_number"],
            errors="ignore"
        ).copy()


        export_df = export_df.rename(
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


        download_csv, download_pdf = (
            st.columns(2)
        )


        # ====================================================
        # CSV
        # ====================================================

        with download_csv:

            csv_data = export_df.to_csv(
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


        # ====================================================
        # PDF
        # ====================================================

        with download_pdf:

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


                document = (
                    SimpleDocTemplate(
                        pdf_buffer,
                        pagesize=landscape(A4),
                        rightMargin=18,
                        leftMargin=18,
                        topMargin=18,
                        bottomMargin=18
                    )
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


                story = []


                story.append(
                    Paragraph(
                        "NOOR CYBER WORLD",
                        title_style
                    )
                )


                story.append(
                    Spacer(1, 8)
                )


                story.append(
                    Paragraph(
                        "Customer Records",
                        styles["Heading2"]
                    )
                )


                story.append(
                    Spacer(1, 10)
                )


                table_data = [
                    list(
                        export_df.columns
                    )
                ]


                for _, row in export_df.iterrows():

                    table_data.append([
                        str(value)
                        for value in row.tolist()
                    ])


                table = Table(
                    table_data,
                    repeatRows=1
                )


                table.setStyle(
                    TableStyle([

                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor(
                                "#172033"
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
                            0.4,
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
                                    "#eeeeee"
                                )
                            ]
                        )

                    ])
                )


                story.append(table)


                document.build(
                    story
                )


                pdf_buffer.seek(0)


                st.download_button(
                    "📄 Download PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=(
                        "NOOR_CYBER_WORLD_CUSTOMERS.pdf"
                    ),
                    mime="application/pdf",
                    use_container_width=True
                )


            except ImportError:

                st.error(
                    "PDF library is not installed. "
                    "Add reportlab to requirements.txt."
                )


        st.markdown("---")


        # ====================================================
        # EDIT CUSTOMER
        # ====================================================

        st.subheader(
            "✏️ Edit Customer Data"
        )


        st.caption(
            "Table में data edit करें और "
            "'Save Changes' दबाएँ."
        )


        edit_columns = [
            "created_at",
            "name",
            "mobile",
            "service",
            "amount",
            "payment",
            "expiry"
        ]


        editable_df = df_all[
            edit_columns
        ].copy()


        edited_df = st.data_editor(

            editable_df,

            key="customer_editor",

            use_container_width=True,

            hide_index=True,

            num_rows="fixed",

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
        # SAVE EDITS
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


                # --------------------------------------------
                # CHECK CHANGES
                # --------------------------------------------

                changed = False


                for column in edit_columns:

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


                # --------------------------------------------
                # SAFE ROW NUMBER
                # --------------------------------------------

                try:

                    row_number = int(
                        float(
                            df_all.iloc[index][
                                "_row_number"
                            ]
                        )
                    )

                except Exception:

                    row_number = (
                        index + 2
                    )


                # --------------------------------------------
                # UPDATE PAYLOAD
                # --------------------------------------------

                payload = {

                    "action":
                        "update",

                    "row_number":
                        str(row_number),

                    "created_at":
                        str(
                            edited["created_at"]
                        ).strip(),

                    "name":
                        str(
                            edited["name"]
                        ).strip(),

                    "mobile":
                        str(
                            edited["mobile"]
                        ).strip(),

                    "service":
                        str(
                            edited["service"]
                        ).strip(),

                    "amount":
                        str(
                            edited["amount"]
                        ).strip(),

                    "payment":
                        str(
                            edited["payment"]
                        ).strip(),

                    "expiry":
                        str(
                            edited["expiry"]
                        ).strip()
                }


                success, message = (
                    send_to_google(
                        payload
                    )
                )


                if not success:

                    errors.append(
                        f"Row {row_number}: "
                        f"{message}"
                    )


            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

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
        # DELETE CUSTOMER
        # ====================================================

        st.markdown("---")

        st.subheader(
            "🗑️ Delete Customer Entry"
        )


        customer_options = []

        for index, row in df_all.iterrows():

            customer_options.append(
                (
                    index,
                    f"{row['name']} | "
                    f"{row['mobile']} | "
                    f"{row['service']} | "
                    f"₹{float(row['amount']):,.0f}"
                )
            )


        if customer_options:

            selected_customer = st.selectbox(
                "Select Customer",
                customer_options,
                format_func=lambda x: x[1]
            )


            if st.button(
                "🗑️ Delete Selected Customer",
                use_container_width=True
            ):

                selected_index = (
                    selected_customer[0]
                )


                try:

                    row_number = int(
                        float(
                            df_all.iloc[
                                selected_index
                            ][
                                "_row_number"
                            ]
                        )
                    )

                except Exception:

                    row_number = (
                        selected_index + 2
                    )


                payload = {

                    "action":
                        "delete",

                    "row_number":
                        str(row_number)
                }


                with st.spinner(
                    "Deleting customer..."
                ):

                    success, message = (
                        send_to_google(
                            payload
                        )
                    )


                if success:

                    st.session_state.success_message = (
                        "✅ Customer deleted successfully!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "❌ Delete failed."
                    )

                    st.code(
                        message
                    )


        # ====================================================
        # CURRENT RECORDS
        # ====================================================

        st.markdown("---")

        st.subheader(
            "📋 Current Customer Records"
        )


        st.dataframe(
            export_df,
            use_container_width=True,
            hide_index=True
        )
