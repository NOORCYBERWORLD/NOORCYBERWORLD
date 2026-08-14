import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

# Page Config
st.set_page_config(page_title="NOOR CYBER WORLD", page_icon="🖥️", layout="wide")

# Google Apps Script Web App URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzpDRn2srFz_HrHgjUs-EpAn3HzUA-gv9Rb5P-apR5uC83JOPYSDjggE8NKl2MC9S3f/exec"

# IST Offset
IST_OFFSET = timezone(timedelta(hours=5, minutes=30))

def get_today_ist():
    return datetime.now(IST_OFFSET).date()

# Custom UI Styling
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0a0a0c 0%, #16181f 50%, #0d1117 100%); color: #ffffff; }
    .header-title { margin: 0; color: #ff2a2a; font-size: 32px; font-weight: 800; letter-spacing: 1.5px; }
    .header-subtitle { margin: 0; color: #3b82f6; font-size: 14px; font-weight: 600; }
    div[data-testid="stMetric"] { background: rgba(255, 255, 255, 0.04); border-radius: 12px; padding: 15px; border: 1px solid rgba(59, 130, 246, 0.2); }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='padding-top: 10px; margin-bottom: 20px;'>
        <h1 class="header-title">NOOR CYBER WORLD</h1>
        <p class="header-subtitle">Center Management & Secure Cloud Entry System</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

def get_records():
    columns = [
        "created_at", "name", "mobile", "service",
        "amount", "payment", "expiry", "_row_number"
    ]

    st.session_state["api_error"] = ""

    try:
        res = requests.get(
            WEB_APP_URL,
            params={"t": int(datetime.now().timestamp())},
            timeout=25
        )

        if res.status_code != 200:
            st.session_state["api_error"] = f"Google Apps Script HTTP error: {res.status_code}"
            return pd.DataFrame(columns=columns)

        try:
            data = res.json()
        except Exception:
            st.session_state["api_error"] = (
                "Google Apps Script did not return JSON. "
                "Check the Apps Script deployment URL."
            )
            return pd.DataFrame(columns=columns)

        if isinstance(data, dict):
            st.session_state["api_error"] = str(
                data.get("error", "Google Apps Script returned an unexpected response.")
            )
            return pd.DataFrame(columns=columns)

        if not isinstance(data, list):
            st.session_state["api_error"] = "Unexpected data received from Google Sheet."
            return pd.DataFrame(columns=columns)

        if not data:
            return pd.DataFrame(columns=columns)

        df = pd.DataFrame(data)

        for col in columns:
            if col not in df.columns:
                df[col] = ""

        for col in ["name", "mobile", "service", "payment", "expiry"]:
            df[col] = df[col].fillna("").astype(str)

        raw_dates = df["created_at"].copy()
        parsed_dates = pd.to_datetime(raw_dates, errors="coerce")
        df["created_at"] = parsed_dates.dt.strftime("%Y-%m-%d")

        failed = parsed_dates.isna()
        df.loc[failed, "created_at"] = raw_dates.loc[failed].astype(str)

        df["amount"] = pd.to_numeric(
            df["amount"], errors="coerce"
        ).fillna(0)

        for i in range(len(df)):
            try:
                df.at[i, "_row_number"] = int(
                    float(df.at[i, "_row_number"])
                )
            except Exception:
                df.at[i, "_row_number"] = i + 2

        return df[columns]

    except Exception as e:
        st.session_state["api_error"] = f"Data loading error: {e}"
        return pd.DataFrame(columns=columns)

def add_record(created_at, name, mobile, service, amount, payment, expiry):
    payload = {
        "action": "add",
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
            timeout=25,
            allow_redirects=True
        )

        if res.status_code >= 400:
            return False, f"HTTP {res.status_code}"

        try:
            data = res.json()
            if data.get("success") is True:
                return True, str(
                    data.get("message", "Entry saved successfully.")
                )
            return False, str(
                data.get("error", data.get("message", "Save failed."))
            )
        except Exception:
            return False, "Invalid response from Google Apps Script."

    except Exception as e:
        return False, str(e)

def update_record(row_number, created_at, name, mobile, service, amount, payment, expiry):
    payload = {
        "action": "update",
        "row_number": str(row_number),
        "created_at": str(created_at),
        "name": str(name),
        "mobile": str(mobile),
        "service": str(service),
        "amount": str(amount),
        "payment": str(payment),
        "expiry": str(expiry)
    }
    try:
        res = requests.post(WEB_APP_URL, data=payload, timeout=20, allow_redirects=True)
        try:
            data = res.json()
            return bool(data.get("success", False)), str(data.get("message", data.get("error", "Unknown response")))
        except Exception:
            return res.status_code < 400, "Request completed"
    except Exception as e:
        return False, str(e)

def delete_record(row_number):
    payload = {"action": "delete", "row_number": str(row_number)}
    try:
        res = requests.post(WEB_APP_URL, data=payload, timeout=20, allow_redirects=True)
        try:
            data = res.json()
            return bool(data.get("success", False)), str(data.get("message", data.get("error", "Unknown response")))
        except Exception:
            return res.status_code < 400, "Request completed"
    except Exception as e:
        return False, str(e)


if "selected_view_date" not in st.session_state:
    st.session_state.selected_view_date = get_today_ist()

services_list = [
    "Aadhaar Card Download / Update", "PAN Card New / Correction", "Voter ID Card Apply / Correction",
    "Ration Card Services", "Ayushman Bharat Card", "E-Shram Card", "Income Certificate",
    "Caste Certificate", "Domicile Certificate", "Non-Creamy Layer Certificate",
    "Gazette Notification / Name Change", "Passport Application", "Driving License (LL/DL) & RC Services",
    "PM Kisan Samman Nidhi / KYC", "PF / EPF Withdrawal & Claim", "Government Job Online Forms",
    "Admission & Scholarship Forms", "Railway / Bus / Air Ticket Booking", "Electricity / Gas / Water Bill Payment",
    "Money Transfer (DMT) / AEPS Cash Withdrawal", "Mobile / DTH Recharge", "Xerox / Color Printout / Lamination / Scanning",
    "Resume / Bio-Data Making", "Udyam Aadhaar / MSME Registration", "Shop Act License / FSSAI Food License",
    "GST Registration & Return Filing", "Income Tax Return (ITR) Filing", "Police Verification Application",
    "Digital Signature (DSC)", "PVC Card Printing", "Other"
]

df_all = get_records()

if "success_message" in st.session_state:
    st.success(st.session_state.pop("success_message"))

if st.session_state.get("api_error"):
    st.error("⚠️ Google Sheet connection problem")
    st.caption(st.session_state["api_error"])

curr_date_str = st.session_state.selected_view_date.strftime("%Y-%m-%d")

if not df_all.empty and "created_at" in df_all.columns:
    normalized_created = pd.to_datetime(
        df_all["created_at"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    day_df = df_all[
        normalized_created == curr_date_str
    ].copy()

    day_total = int(
        day_df["amount"].sum()
    ) if not day_df.empty else 0
else:
    day_df = pd.DataFrame()
    day_total = 0

col_prev, col_date, col_next = st.columns([1, 4, 1])

with col_prev:
    st.write("")
    if st.button("❮ Previous", use_container_width=True):
        st.session_state.selected_view_date -= timedelta(days=1)
        st.rerun()

with col_date:
    selected_from_cal = st.date_input(
        f"📅 Date: {st.session_state.selected_view_date.strftime('%B %d, %Y (%A)')}  |  Balance: ₹ {day_total:,}",
        value=st.session_state.selected_view_date,
        key="date_picker_main"
    )
    if selected_from_cal != st.session_state.selected_view_date:
        st.session_state.selected_view_date = selected_from_cal
        st.rerun()

with col_next:
    st.write("")
    if st.button("Next ❯", use_container_width=True):
        st.session_state.selected_view_date += timedelta(days=1)
        st.rerun()

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Daily View & Add Entry", "🔔 Renewal Alerts", "📂 Full Google Sheet Data"])

with tab1:
    st.subheader(f"📋 Entries for {st.session_state.selected_view_date.strftime('%d-%m-%Y (%A)')}")
    
    if not day_df.empty:
        total_cash = int(day_df[day_df["payment"] == "Cash"]["amount"].sum())
        total_online = int(day_df[day_df["payment"] == "Online"]["amount"].sum())
    else:
        total_cash = 0
        total_online = 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Day Total", f"₹ {total_cash + total_online}")
    c2.metric("Day Cash", f"₹ {total_cash}")
    c3.metric("Day Online / UPI", f"₹ {total_online}")
    
    st.markdown("---")
    if not day_df.empty:
        st.dataframe(day_df, use_container_width=True)
    else:
        st.info("ℹ️ No entries recorded for this date yet.")

    st.markdown("---")
    st.subheader(f"➕ Add Entry for {st.session_state.selected_view_date.strftime('%d-%m-%Y')}")
    
    col_a, col_b = st.columns(2)
    with col_a:
        name = st.text_input("Customer Name*", key="cust_name_input")
        mobile = st.text_input("Mobile Number*", key="cust_mob_input")
        selected_service = st.selectbox("Search / Select Service*", services_list, key="srv_select_input")
        custom_srv = st.text_input("Type Custom Service Name (If 'Other' Selected)", key="custom_srv_input")

    with col_b:
        amount = st.number_input("Amount (₹)", min_value=0, step=10, key="amt_input")
        pay_mode = st.radio("Payment Mode", ["Cash", "Online"], horizontal=True, key="pay_mode_input")
        has_expiry = st.checkbox("Requires Renewal / Validity?", key="has_exp_input")
        dur_unit = st.selectbox("Validity Unit", ["Days", "Months", "Years"], index=1, key="dur_unit_input")
        dur_val = st.number_input("Validity Duration Value", min_value=1, value=1, key="dur_val_input")

    st.write("")
    if st.button("💾 Save Entry to Cloud Sheet", type="primary", use_container_width=True):
        if not name.strip() or not mobile.strip():
            st.error("⚠️ Please enter Customer Name and Mobile Number!")
        else:
            final_service = selected_service
            if selected_service == "Other":
                if custom_srv.strip():
                    final_service = custom_srv.strip()
                else:
                    st.error("⚠️ Please type the custom service name!")
                    st.stop()
            
            exp_str = "N/A"
            if has_expiry:
                entry_d = st.session_state.selected_view_date
                if dur_unit == "Days":
                    calc_exp = entry_d + timedelta(days=int(dur_val))
                elif dur_unit == "Months":
                    calc_exp = entry_d + relativedelta(months=int(dur_val))
                elif dur_unit == "Years":
                    calc_exp = entry_d + relativedelta(years=int(dur_val))
                exp_str = calc_exp.strftime("%Y-%m-%d")

            date_str = st.session_state.selected_view_date.strftime("%Y-%m-%d")
            
            with st.spinner("Saving entry to Google Sheet..."):
                success, message = add_record(
                    date_str,
                    name,
                    mobile,
                    final_service,
                    amount,
                    pay_mode,
                    exp_str
                )

            if success:
                st.session_state["success_message"] = (
                    f"✅ Success! Entry for '{name}' (₹{amount}) saved successfully!"
                )
                st.rerun()
            else:
                st.error("❌ Google Sheet server error. Please try again.")
                st.caption(message)

with tab2:
    st.subheader("⚠️ Renewal Alerts (Next 15 Days)")
    today = get_today_ist()
    alerts_found = False
    
    if not df_all.empty and "expiry" in df_all.columns:
        for idx, row in df_all.iterrows():
            exp_val = row["expiry"]
            if exp_val != "N/A" and exp_val != "" and exp_val is not None:
                try:
                    exp_d = datetime.strptime(str(exp_val), "%Y-%m-%d").date()
                    days_left = (exp_d - today).days
                    if 0 <= days_left <= 15:
                        alerts_found = True
                        formatted_exp = exp_d.strftime('%d-%m-%Y')
                        msg = f"Hello {row['name']}, your {row['service']} is expiring on {formatted_exp}. Please visit NOOR CYBER WORLD for renewal."
                        wa_link = f"https://wa.me/91{row['mobile']}?text={msg.replace(' ', '%20')}"
                        st.warning(f"🔴 **{row['name']}** - {row['service']} (Expires: {formatted_exp} | {days_left} Days Left)")
                        st.markdown(f"[💬 Send WhatsApp Message]({wa_link})")
                except Exception:
                    pass
                    
    if not alerts_found:
        st.info("🎉 No renewals due in the next 15 days.")

with tab3:
    st.subheader("📂 Current Customer Records")

    if st.button("🔄 Refresh Records", use_container_width=False):
        st.rerun()

    if df_all.empty:
        st.info("No records available in Google Sheet.")
    else:
        export_df = df_all.drop(columns=["_row_number"], errors="ignore").copy()

        # Downloads
        d1, d2 = st.columns(2)
        with d1:
            csv_data = export_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 Download CSV",
                data=csv_data,
                file_name="NOOR_CYBER_WORLD_RECORDS.csv",
                mime="text/csv",
                use_container_width=True
            )

        with d2:
            # PDF is intentionally handled without reportlab so the app does not
            # depend on an extra package. It is a simple printable PDF.
            def _pdf_escape(value):
                return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

            pdf_lines = ["NOOR CYBER WORLD", "CUSTOMER RECORDS", ""]
            for _, rr in export_df.iterrows():
                pdf_lines.append(
                    f"{rr.get('created_at','')} | {rr.get('name','')} | {rr.get('mobile','')} | "
                    f"{rr.get('service','')} | Rs {rr.get('amount',0)} | {rr.get('payment','')} | {rr.get('expiry','')}"
                )

            pages = [pdf_lines[i:i+42] for i in range(0, len(pdf_lines), 42)] or [[]]
            page_ids = [3 + i*2 for i in range(len(pages))]
            content_ids = [4 + i*2 for i in range(len(pages))]
            font_id = 3 + len(pages)*2
            objects = [
                "<< /Type /Catalog /Pages 2 0 R >>",
                "<< /Type /Pages /Kids [" + " ".join(f"{x} 0 R" for x in page_ids) + f"] /Count {len(pages)} >>"
            ]

            for pi, pg in enumerate(pages):
                stream = ["BT", "/F1 7 Tf"]
                y = 560
                for line in pg:
                    safe = _pdf_escape(line)[:150].encode("latin-1", "replace").decode("latin-1")
                    stream.append(f"1 0 0 1 25 {y} Tm")
                    stream.append(f"({safe}) Tj")
                    y -= 12
                stream.append("ET")
                stxt = "\n".join(stream)
                objects.append(
                    f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 842 595] /Contents {content_ids[pi]} 0 R "
                    f"/Resources << /Font << /F1 {font_id} 0 R >> >> >>"
                )
                objects.append(f"<< /Length {len(stxt.encode('latin-1'))} >>\nstream\n{stxt}\nendstream")

            objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
            pdf = b"%PDF-1.4\n"
            offsets = [0]
            for n, obj in enumerate(objects, 1):
                offsets.append(len(pdf))
                pdf += f"{n} 0 obj\n{obj}\nendobj\n".encode("latin-1", "replace")
            xref = len(pdf)
            pdf += f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode("latin-1")
            for off in offsets[1:]:
                pdf += f"{off:010d} 00000 n \n".encode("latin-1")
            pdf += f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode("latin-1")

            st.download_button(
                "📄 Download PDF",
                data=pdf,
                file_name="NOOR_CYBER_WORLD_RECORDS.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        st.markdown("---")

        # Edit form state
        if "edit_index" not in st.session_state:
            st.session_state.edit_index = None
        if "delete_index" not in st.session_state:
            st.session_state.delete_index = None

        if st.session_state.edit_index is not None:
            idx = st.session_state.edit_index
            if 0 <= idx < len(df_all):
                row = df_all.iloc[idx]
                st.subheader("✏️ Edit Customer")
                e1, e2 = st.columns(2)
                with e1:
                    e_date = st.text_input("Date", str(row["created_at"]), key="edit_date")
                    e_name = st.text_input("Customer Name", str(row["name"]), key="edit_name")
                    e_mobile = st.text_input("Mobile", str(row["mobile"]), key="edit_mobile")
                    e_service = st.text_input("Service", str(row["service"]), key="edit_service")
                with e2:
                    try:
                        e_amount_default = int(float(row["amount"]))
                    except Exception:
                        e_amount_default = 0
                    e_amount = st.number_input("Amount ₹", min_value=0, value=e_amount_default, step=10, key="edit_amount")
                    e_payment = st.selectbox("Payment", ["Cash", "Online"], index=0 if str(row["payment"]).strip() != "Online" else 1, key="edit_payment")
                    e_expiry = st.text_input("Expiry", str(row["expiry"]), key="edit_expiry")

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("💾 Save Changes", type="primary", use_container_width=True):
                        try:
                            row_number = int(float(row["_row_number"]))
                        except Exception:
                            row_number = idx + 2
                        ok, msg = update_record(row_number, e_date, e_name, e_mobile, e_service, e_amount, e_payment, e_expiry)
                        if ok:
                            st.session_state.edit_index = None
                            st.success("✅ Customer updated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Update failed.")
                            st.code(msg)
                with b2:
                    if st.button("❌ Cancel Edit", use_container_width=True):
                        st.session_state.edit_index = None
                        st.rerun()
                st.markdown("---")

        if st.session_state.delete_index is not None:
            idx = st.session_state.delete_index
            if 0 <= idx < len(df_all):
                row = df_all.iloc[idx]
                st.warning(f"⚠️ Delete '{row['name']}' ({row['mobile']})?")
                d1, d2 = st.columns(2)
                with d1:
                    if st.button("✅ Yes, Delete", type="primary", use_container_width=True):
                        try:
                            row_number = int(float(row["_row_number"]))
                        except Exception:
                            row_number = idx + 2
                        ok, msg = delete_record(row_number)
                        if ok:
                            st.session_state.delete_index = None
                            st.success("🗑️ Customer deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Delete failed.")
                            st.code(msg)
                with d2:
                    if st.button("❌ Cancel Delete", use_container_width=True):
                        st.session_state.delete_index = None
                        st.rerun()
                st.markdown("---")

        # Current records list with inline Edit/Delete controls
        st.subheader(f"📋 Current Records — {len(df_all)} Customers")
        hdr = st.columns([1.0, 1.4, 1.25, 2.0, 0.8, 0.9, 0.9, 0.5, 0.6])
        for c, text in zip(hdr, ["Date", "Customer", "Mobile", "Service", "Amount", "Payment", "Expiry", "✏️", "🗑️"]):
            c.markdown(f"**{text}**")
        st.markdown("---")

        for idx, row in df_all.iterrows():
            r = st.columns([1.0, 1.4, 1.25, 2.0, 0.8, 0.9, 0.9, 0.5, 0.6])
            r[0].write(str(row["created_at"]))
            r[1].write(str(row["name"]))
            r[2].write(str(row["mobile"]))
            r[3].write(str(row["service"]))
            r[4].write(f"₹ {float(row['amount']):,.0f}")
            r[5].write(str(row["payment"]))
            r[6].write(str(row["expiry"]))
            if r[7].button("✏️", key=f"edit_{idx}"):
                st.session_state.edit_index = idx
                st.session_state.delete_index = None
                st.rerun()
            if r[8].button("🗑️", key=f"delete_{idx}"):
                st.session_state.delete_index = idx
                st.session_state.edit_index = None
                st.rerun()
            st.markdown("<hr style='margin:4px 0;opacity:0.2;'>", unsafe_allow_html=True)
