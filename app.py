import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import quote


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

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzpDRn2srFz_HrHgjUs-EpAn3HzUA-gv9Rb5P-apR5uC83JOPYSDjggE8NKl2MC9S3f/exec"


# ============================================================
# IST TIMEZONE
# ============================================================

IST_OFFSET = timezone(timedelta(hours=5, minutes=30))


def get_today_ist():
    return datetime.now(IST_OFFSET).date()


# ============================================================
# CUSTOM UI
# ============================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
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
    background: rgba(255, 255, 255, 0.04);
    border-radius: 12px;
    padding: 15px;
    border: 1px solid rgba(59, 130, 246, 0.2);
}

.stButton > button {
    border-radius: 8px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div style='padding-top: 10px; margin-bottom: 20px;'>
    <h1 class="header-title">NOOR CYBER WORLD</h1>
    <p class="header-subtitle">
        Center Management & Secure Cloud Entry System
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ============================================================
# SUCCESS MESSAGE AFTER RERUN
# ============================================================

if "save_success_message" in st.session_state:

    st.success(st.session_state.save_success_message)

    del st.session_state.save_success_message


# ============================================================
# GET RECORDS FROM GOOGLE SHEET
# ============================================================

def get_records():

    empty_df = pd.DataFrame(
        columns=[
            "created_at",
            "name",
            "mobile",
            "service",
            "amount",
            "payment",
            "expiry"
        ]
    )

    try:

        fetch_url = f"{WEB_APP_URL}?t={datetime.now().timestamp()}"

        res = requests.get(
            fetch_url,
            timeout=15,
            allow_redirects=True
        )

        if res.status_code != 200:
            return empty_df

        try:
            data = res.json()
        except Exception:
            return empty_df

        # Apps Script error response
        if isinstance(data, dict):

            if data.get("success") is False:
                return empty_df

            return empty_df

        if not isinstance(data, list):
            return empty_df

        if len(data) == 0:
            return empty_df

        df = pd.DataFrame(data)

        # Make sure required columns exist
        required_columns = [
            "created_at",
            "name",
            "mobile",
            "service",
            "amount",
            "payment",
            "expiry"
        ]

        for col in required_columns:

            if col not in df.columns:
                df[col] = ""

        # --------------------------------------------------------
        # DATE NORMALIZATION
        # --------------------------------------------------------

        if "created_at" in df.columns:

            df["created_at"] = pd.to_datetime(
                df["created_at"],
                errors="coerce"
            ).dt.strftime("%Y-%m-%d")

            df["created_at"] = df["created_at"].fillna("")

        # --------------------------------------------------------
        # AMOUNT
        # --------------------------------------------------------

        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce"
        ).fillna(0)

        # --------------------------------------------------------
        # MOBILE
        # --------------------------------------------------------

        df["mobile"] = df["mobile"].astype(str)

        # --------------------------------------------------------
        # EXPIRY
        # --------------------------------------------------------

        if "expiry" in df.columns:

            expiry_original = df["expiry"].astype(str)

            expiry_dates = pd.to_datetime(
                expiry_original,
                errors="coerce"
            )

            df["expiry"] = expiry_dates.dt.strftime("%Y-%m-%d")

            # Restore N/A / blank values
            df.loc[
                expiry_original.str.upper().isin(
                    ["N/A", "NA", "", "NONE", "NAN"]
                ),
                "expiry"
            ] = "N/A"

            df["expiry"] = df["expiry"].fillna("N/A")

        return df[required_columns]

    except Exception:
        return empty_df


# ============================================================
# ADD RECORD TO GOOGLE SHEET
# ============================================================

def add_record(
    created_at,
    name,
    mobile,
    service,
    amount,
    payment,
    expiry
):

    payload = {

        "created_at": str(created_at),

        "name": str(name),

        "mobile": str(mobile),

        "service": str(service),

        "amount": str(amount),

        "payment": str(payment),

        "expiry": str(expiry)
    }

    try:

        res = requests.post(
            WEB_APP_URL,
            data=payload,
            timeout=20,
            allow_redirects=True
        )

        if res.status_code >= 400:
            return False

        # Check Apps Script JSON response
        try:

            result = res.json()

            if isinstance(result, dict):

                return result.get("success", False)

            return False

        except Exception:

            # If Apps Script saved the data but response
            # is not JSON, consider HTTP success.
            return res.status_code < 400

    except Exception:

        return False


# ============================================================
# SESSION STATE
# ============================================================

if "selected_view_date" not in st.session_state:

    st.session_state.selected_view_date = get_today_ist()


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
# LOAD ALL RECORDS
# ============================================================

df_all = get_records()


# ============================================================
# SELECTED DATE
# ============================================================

curr_date_str = (
    st.session_state.selected_view_date
    .strftime("%Y-%m-%d")
)


# ============================================================
# FILTER SELECTED DAY
# ============================================================

if not df_all.empty and "created_at" in df_all.columns:

    day_df = df_all[
        df_all["created_at"] == curr_date_str
    ].copy()

else:

    day_df = pd.DataFrame()

    
# ============================================================
# DAY TOTAL
# ============================================================

if not day_df.empty:

    day_total = float(
        day_df["amount"].sum()
    )

else:

    day_total = 0


# ============================================================
# DATE NAVIGATION
# ============================================================

col_prev, col_date, col_next = st.columns([1, 4, 1])


# ------------------------------------------------------------
# PREVIOUS
# ------------------------------------------------------------

with col_prev:

    st.write("")

    if st.button(
        "❮ Previous",
        use_container_width=True
    ):

        st.session_state.selected_view_date -= timedelta(days=1)

        st.rerun()


# ------------------------------------------------------------
# DATE PICKER
# ------------------------------------------------------------

with col_date:

    selected_from_cal = st.date_input(

        f"📅 Date: "
        f"{st.session_state.selected_view_date.strftime('%B %d, %Y (%A)')}"
        f"  |  Balance: ₹ {day_total:,.0f}",

        value=st.session_state.selected_view_date,

        key="date_picker_main"
    )

    if selected_from_cal != st.session_state.selected_view_date:

        st.session_state.selected_view_date = selected_from_cal

        st.rerun()


# ------------------------------------------------------------
# NEXT
# ------------------------------------------------------------

with col_next:

    st.write("")

    if st.button(
        "Next ❯",
        use_container_width=True
    ):

        st.session_state.selected_view_date += timedelta(days=1)

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
        f"{st.session_state.selected_view_date.strftime('%d-%m-%Y (%A)')}"
    )


    # --------------------------------------------------------
    # CASH / ONLINE TOTAL
    # --------------------------------------------------------

    if not day_df.empty:

        total_cash = float(
            day_df[
                day_df["payment"].astype(str).str.strip().str.lower()
                == "cash"
            ]["amount"].sum()
        )

        total_online = float(
            day_df[
                day_df["payment"].astype(str).str.strip().str.lower()
                == "online"
            ]["amount"].sum()
        )

    else:

        total_cash = 0

        total_online = 0


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)


    c1.metric(
        "Day Total",
        f"₹ {total_cash + total_online:,.0f}"
    )


    c2.metric(
        "Day Cash",
        f"₹ {total_cash:,.0f}"
    )


    c3.metric(
        "Day Online / UPI",
        f"₹ {total_online:,.0f}"
    )


    st.markdown("---")


    # --------------------------------------------------------
    # DAILY TABLE
    # --------------------------------------------------------

    if not day_df.empty:

        st.dataframe(
            day_df,
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
        f"{st.session_state.selected_view_date.strftime('%d-%m-%Y')}"
    )


    col_a, col_b = st.columns(2)


    # --------------------------------------------------------
    # LEFT SIDE
    # --------------------------------------------------------

    with col_a:

        name = st.text_input(
            "Customer Name*",
            key="cust_name_input"
        )


        mobile = st.text_input(
            "Mobile Number*",
            key="cust_mob_input"
        )


        selected_service = st.selectbox(
            "Search / Select Service*",
            services_list,
            key="srv_select_input"
        )


        custom_srv = st.text_input(
            "Type Custom Service Name (If 'Other' Selected)",
            key="custom_srv_input"
        )


    # --------------------------------------------------------
    # RIGHT SIDE
    # --------------------------------------------------------

    with col_b:

        amount = st.number_input(
            "Amount (₹)",
            min_value=0,
            step=10,
            key="amt_input"
        )


        pay_mode = st.radio(
            "Payment Mode",
            ["Cash", "Online"],
            horizontal=True,
            key="pay_mode_input"
        )


        has_expiry = st.checkbox(
            "Requires Renewal / Validity?",
            key="has_exp_input"
        )


        dur_unit = st.selectbox(
            "Validity Unit",
            ["Days", "Months", "Years"],
            index=1,
            key="dur_unit_input"
        )


        dur_val = st.number_input(
            "Validity Duration Value",
            min_value=1,
            value=1,
            step=1,
            key="dur_val_input"
        )


    st.write("")


    # ========================================================
    # SAVE BUTTON
    # ========================================================

    if st.button(
        "💾 Save Entry to Cloud Sheet",
        type="primary",
        use_container_width=True
    ):


        # ----------------------------------------------------
        # VALIDATE NAME
        # ----------------------------------------------------

        if not name.strip():

            st.error(
                "⚠️ Please enter Customer Name!"
            )

            st.stop()


        # ----------------------------------------------------
        # VALIDATE MOBILE
        # ----------------------------------------------------

        clean_mobile = (
            mobile
            .replace(" ", "")
            .replace("-", "")
            .replace("+91", "")
        )


        if not clean_mobile.isdigit():

            st.error(
                "⚠️ Please enter a valid Mobile Number!"
            )

            st.stop()


        if len(clean_mobile) != 10:

            st.error(
                "⚠️ Mobile Number must contain 10 digits!"
            )

            st.stop()


        # ----------------------------------------------------
        # SERVICE
        # ----------------------------------------------------

        final_service = selected_service


        if selected_service == "Other":

            if custom_srv.strip():

                final_service = custom_srv.strip()

            else:

                st.error(
                    "⚠️ Please type the custom service name!"
                )

                st.stop()


        # ----------------------------------------------------
        # EXPIRY
        # ----------------------------------------------------

        exp_str = "N/A"


        if has_expiry:

            entry_d = (
                st.session_state.selected_view_date
            )


            if dur_unit == "Days":

                calc_exp = (
                    entry_d
                    + timedelta(days=int(dur_val))
                )


            elif dur_unit == "Months":

                calc_exp = (
                    entry_d
                    + relativedelta(months=int(dur_val))
                )


            else:

                calc_exp = (
                    entry_d
                    + relativedelta(years=int(dur_val))
                )


            exp_str = calc_exp.strftime(
                "%Y-%m-%d"
            )


        # ----------------------------------------------------
        # ENTRY DATE
        # ----------------------------------------------------

        date_str = (
            st.session_state.selected_view_date
            .strftime("%Y-%m-%d")
        )


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        with st.spinner(
            "Saving entry to Google Sheet..."
        ):

            success = add_record(
                date_str,
                name.strip(),
                clean_mobile,
                final_service,
                amount,
                pay_mode,
                exp_str
            )


        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if success:

            st.session_state.save_success_message = (
                f"✅ Success! Entry for '{name.strip()}' "
                f"(₹{amount:,.0f}) saved successfully!"
            )

            # IMPORTANT:
            # Rerun the complete application.
            # get_records() will execute again,
            # fresh data will come from Google Sheet,
            # and Day Total will update immediately.

            st.rerun()


        # ----------------------------------------------------
        # ERROR
        # ----------------------------------------------------

        else:

            st.error(
                "❌ Google Sheet server error. "
                "Please try again."
            )


# ============================================================
# TAB 2 - RENEWAL ALERTS
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


        for idx, row in df_all.iterrows():

            exp_val = row["expiry"]


            if (
                exp_val != "N/A"
                and exp_val != ""
                and exp_val is not None
            ):


                try:

                    exp_d = datetime.strptime(
                        str(exp_val),
                        "%Y-%m-%d"
                    ).date()


                    days_left = (
                        exp_d - today
                    ).days


                    if 0 <= days_left <= 15:

                        alerts_found = True


                        formatted_exp = (
                            exp_d.strftime("%d-%m-%Y")
                        )


                        customer_name = str(
                            row.get("name", "")
                        )


                        service_name = str(
                            row.get("service", "")
                        )


                        mobile_number = str(
                            row.get("mobile", "")
                        )


                        msg = (
                            f"Hello {customer_name}, "
                            f"your {service_name} is expiring "
                            f"on {formatted_exp}. "
                            f"Please visit NOOR CYBER WORLD "
                            f"for renewal."
                        )


                        # Proper URL encoding
                        wa_link = (
                            "https://wa.me/91"
                            f"{mobile_number}"
                            f"?text={quote(msg)}"
                        )


                        st.warning(
                            f"🔴 **{customer_name}** - "
                            f"{service_name} "
                            f"(Expires: {formatted_exp} | "
                            f"{days_left} Days Left)"
                        )


                        st.markdown(
                            f"[💬 Send WhatsApp Message]({wa_link})"
                        )


                except Exception:

                    continue


    if not alerts_found:

        st.info(
            "🎉 No renewals due in the next 15 days."
        )


# ============================================================
# TAB 3 - FULL GOOGLE SHEET DATA
# ============================================================

with tab3:

    st.subheader(
        "📂 All Cloud Records"
    )


    if df_all.empty:

        st.info(
            "No records available in Google Sheet."
        )


    else:

        st.dataframe(
            df_all,
            use_container_width=True,
            hide_index=True
        )
