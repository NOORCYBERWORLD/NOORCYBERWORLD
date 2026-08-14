import streamlit as st
import pandas as pd
import requests
import json
import uuid

from streamlit_js_eval import streamlit_js_eval
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import quote

st.markdown("""
<style>
.nc-header {
    text-align: center;
    padding: 18px 10px 24px;
    margin-bottom: 15px;
}

.nc-title {
    font-family: Arial, sans-serif;
    font-size: 34px;
    font-weight: 800;
    letter-spacing: 3px;
    color: white;
    margin-bottom: 5px;
}

.nc-main-title {
    font-family: Arial, sans-serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #22d3ee;
    margin-bottom: 8px;
}

.nc-sub {
    font-size: 12px;
    letter-spacing: 1.5px;
    color: #cbd5e1;
}

.nc-status {
    display: inline-block;
    margin-top: 12px;
    padding: 5px 14px;
    border-radius: 20px;
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.35);
    color: #86efac;
    font-size: 11px;
    font-weight: 600;
}
</style>

<div class="nc-header">
    <div class="nc-title">NOOR CYBER WORLD</div>
    <div class="nc-main-title">CUSTOMERS MANAGEMENT SYSTEM</div>
    <div class="nc-sub">DIGITAL SERVICE • CUSTOMER RECORD • SMART MANAGEMENT</div>
    <div class="nc-status">● SYSTEM ONLINE</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# GOOGLE APPS SCRIPT
# ============================================================

WEB_APP_URL = (
    "https://script.google.com/macros/s/AKfycbzpDRn2srFz_HrHgjUs-EpAn3HzUA-gv9Rb5P-apR5uC83JOPYSDjggE8NKl2MC9S3f/exec"
)


# ============================================================
# TIMEZONE
# ============================================================

IST = timezone(
    timedelta(
        hours=5,
        minutes=30
    )
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
    "payment",
    "expiry",
    "_row_number",
    "_source",
    "_local_id"
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
    "Other"
]


# ============================================================
# SORT SERVICES
# ============================================================

DEFAULT_SERVICES = sorted(
    [
        service
        for service in DEFAULT_SERVICES
        if service != "Other"
    ],
    key=lambda x: x.lower()
) + ["Other"]


# ============================================================
# CUSTOM SERVICES
# ============================================================

if "custom_services" not in st.session_state:
    st.session_state.custom_services = []


def get_all_services():
    services = (
        DEFAULT_SERVICES[:-1]
        + st.session_state.custom_services
    )

    services = sorted(
        set(
            service.strip()
            for service in services
            if service and service.strip()
        ),
        key=lambda x: x.lower()
    )

    # Keep Other at the bottom
    services.append("Other")

    return services


SERVICES = get_all_services()


# ============================================================
# SESSION VARIABLES
# ============================================================

if "local_counter" not in st.session_state:
    st.session_state.local_counter = 0

if "selected_date" not in st.session_state:
    st.session_state.selected_date = (
        datetime.now(IST).date()
    )

if "edit_key" not in st.session_state:
    st.session_state.edit_key = None

if "delete_key" not in st.session_state:
    st.session_state.delete_key = None

if "records_cache" not in st.session_state:
    st.session_state.records_cache = pd.DataFrame(
        columns=COLUMNS
    )


# ============================================================
# PROFESSIONAL DESIGN
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&display=swap');

:root {
    --red:#ff3b30;
    --cyan:#22d3ee;
    --blue:#3b82f6;
    --green:#22c55e;
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

[data-testid="stHeader"] {
    background:rgba(0,0,0,0);
}

.block-container {
    max-width:1450px;
    padding-top:1.2rem;
    padding-bottom:3rem;
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
    box-shadow: 0 12px 35px rgba(0,0,0,.22);
}

div[data-testid="stMetricLabel"] { color:#cbd5e1; }
div[data-testid="stMetricValue"] { font-weight:800; }

button[data-baseweb="tab"] {
    font-weight:700 !important;
    font-size:14px !important;
    color:#94a3b8 !important;
    background: rgba(15,23,42,.6) !important;
    border-radius: 12px 12px 0 0 !important;
    padding: 12px 18px !important;
    margin-right: 5px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color:#fff !important;
    background:
        linear-gradient(
            135deg,
            rgba(59,130,246,.28),
            rgba(239,68,68,.18)
        ) !important;
    box-shadow:
        inset 0 -3px 0 var(--cyan),
        0 5px 20px rgba(34,211,238,.12);
}

div[data-testid="stForm"] {
    background: rgba(15,23,42,.72);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 11px !important;
    border: 1px solid rgba(96,165,250,.28) !important;
    background:
        linear-gradient(
            135deg,
            rgba(30,41,59,.95),
            rgba(15,23,42,.95)
        ) !important;
    color:#f8fafc !important;
    font-weight: 700 !important;
    min-height: 42px;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 18px rgba(34,211,238,.16);
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow:hidden;
}

input, textarea, [data-baseweb="select"] > div {
    border-radius: 10px !important;
}

.nc-card {
    background:
        linear-gradient(
            145deg,
            rgba(15,23,42,.86),
            rgba(30,41,59,.62)
        );
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
    margin: 8px 0;
}

.nc-section {
    font-family: 'Orbitron',sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #e2e8f0;
    margin: 8px 0 14px;
}

.small-muted {
    color: #94a3b8;
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


def empty_df():
    return pd.DataFrame(
        columns=COLUMNS
    )


def clean_df(df):
    if df is None or df.empty:
        return empty_df()

    df = df.copy()

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    for col in [
        "name",
        "mobile",
        "service",
        "payment",
        "expiry",
        "_source",
        "_local_id"
    ]:
        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
        )

    raw = (
        df["created_at"]
        .fillna("")
        .astype(str)
    )

    parsed = pd.to_datetime(
        raw,
        errors="coerce"
    )

    df["created_at"] = (
        parsed
        .dt
        .strftime("%Y-%m-%d")
    )

    df.loc[
        parsed.isna(),
        "created_at"
    ] = raw[parsed.isna()]

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    ).fillna(0)

    for i in range(len(df)):
        try:
            df.at[
                df.index[i],
                "_row_number"
            ] = int(
                float(
                    df.at[
                        df.index[i],
                        "_row_number"
                    ]
                )
            )
        except Exception:
            df.at[
                df.index[i],
                "_row_number"
            ] = -1

    return df[COLUMNS]


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
            return (
                empty_df(),
                f"Google Apps Script HTTP {response.status_code}"
            )

        data = response.json()

        if isinstance(data, dict):
            return (
                empty_df(),
                str(
                    data.get(
                        "error",
                        "Unexpected Apps Script response"
                    )
                )
            )

        if not isinstance(data, list):
            return (
                empty_df(),
                "Apps Script did not return a records list."
            )

        df = pd.DataFrame(data)

        if df.empty:
            return (empty_df(), "")

        df["_source"] = "sheet"
        return (clean_df(df), "")

    except Exception as e:
        return (empty_df(), str(e))


def api_post(payload):
    try:
        response = requests.post(
            WEB_APP_URL,
            data=payload,
            timeout=20,
            allow_redirects=True
        )

        try:
            data = response.json()
            return (
                bool(data.get("success")),
                str(data.get("message", data.get("error", "Request failed")))
            )
        except Exception:
            return (False, "Invalid response from Apps Script.")

    except Exception as e:
        return (False, str(e))


# ============================================================
# SAFE BROWSER LOCAL STORAGE
# ============================================================

LOCAL_STORAGE_KEY = "noor_cyber_pending_v3"


def local_storage_get():
    try:
        raw = streamlit_js_eval(
            js_expressions=f"localStorage.getItem('{LOCAL_STORAGE_KEY}')",
            want_output=True,
            key="noor_local_get_v3"
        )
        if raw is None:
            return None
        if raw == "":
            return []
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except Exception:
                return []
        return []
    except Exception:
        return None


def local_storage_set(records):
    try:
        payload = json.dumps(records, ensure_ascii=False)
        expression = (
            f"localStorage.setItem("
            f"{json.dumps(LOCAL_STORAGE_KEY)},"
            f"{json.dumps(payload)}"
            f"); true"
        )
        return streamlit_js_eval(
            js_expressions=expression,
            want_output=True,
            key=f"noor_local_set_{uuid.uuid4().hex}"
        )
    except Exception:
        return None


def local_storage_clear():
    try:
        expression = f"localStorage.removeItem({json.dumps(LOCAL_STORAGE_KEY)}); true"
        return streamlit_js_eval(
            js_expressions=expression,
            want_output=True,
            key=f"noor_local_clear_{uuid.uuid4().hex}"
        )
    except Exception:
        return None


def local_records_df():
    records = local_storage_get()
    if records is None or not records:
        return empty_df()
    try:
        df = pd.DataFrame(records)
        if df.empty:
            return empty_df()
        df["_source"] = "local"
        df["_row_number"] = -1
        return clean_df(df)
    except Exception:
        return empty_df()


def persist_local_df(df):
    if df is None or df.empty:
        local_storage_clear()
        return

    local = df[df["_source"] == "local"].copy()

    if local.empty:
        local_storage_clear()
        return

    keep = [
        "created_at",
        "name",
        "mobile",
        "service",
        "amount",
        "payment",
        "expiry",
        "_local_id"
    ]

    records = local[keep].to_dict(orient="records")
    local_storage_set(records)


def sheet_row(row):
    try:
        return int(float(row["_row_number"]))
    except Exception:
        return -1


# ============================================================
# PDF GENERATOR
# ============================================================

def make_pdf(df):
    def esc(x):
        return (
            str(x)
            .replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )

    lines = [
        "NOOR CYBER WORLD",
        "CUSTOMER RECORDS",
        "=" * 100
    ]

    for _, r in df.iterrows():
        lines.append(
            f"{r.get('created_at','')} | "
            f"{r.get('name','')} | "
            f"{r.get('mobile','')} | "
            f"{r.get('service','')} | "
            f"Rs {r.get('amount',0)} | "
            f"{r.get('payment','')} | "
            f"{r.get('expiry','')}"
        )

    pages = [lines[i:i + 40] for i in range(0, len(lines), 40)] or [[]]
    page_ids = [3 + 2 * i for i in range(len(pages))]
    content_ids = [4 + 2 * i for i in range(len(pages))]
    font_id = 3 + 2 * len(pages)

    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids ["
        + " ".join(f"{x} 0 R" for x in page_ids)
        + f"] /Count {len(pages)} >>"
    ]

    for pi, page in enumerate(pages):
        stream = ["BT", "/F1 7 Tf"]
        y = 560
        for line in page:
            safe = esc(line)[:150].encode("latin-1", "replace").decode("latin-1")
            stream.append(f"1 0 0 1 25 {y} Tm")
            stream.append(f"({safe}) Tj")
            y -= 13
        stream.append("ET")

        text = "\n".join(stream)
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 842 595] "
            f"/Contents {content_ids[pi]} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>"
        )
        objects.append(
            f"<< /Length {len(text.encode('latin-1'))} >>\nstream\n{text}\nendstream"
        )

    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    pdf = b"%PDF-1.4\n"
    offsets = [0]

    for n, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf += f"{n} 0 obj\n{obj}\nendobj\n".encode("latin-1", "replace")

    xref = len(pdf)
    pdf += f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode()

    for off in offsets[1:]:
        pdf += f"{off:010d} 00000 n \n".encode()

    pdf += (
        f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF"
    ).encode()

    return pdf


# ============================================================
# INITIAL LOAD
# ============================================================

if "local_boot_loaded" not in st.session_state:
    local_boot = local_records_df()
    sheet_boot, load_error = fetch_sheet_records()

    st.session_state.records_cache = pd.concat(
        [sheet_boot, local_boot],
        ignore_index=True
    )
    st.session_state.last_load_error = load_error
    st.session_state.local_boot_loaded = True


# ============================================================
# MERGE SHEET + LOCAL SAFELY
# ============================================================

df_all = clean_df(st.session_state.records_cache)

if not df_all.empty and "_local_id" in df_all.columns:
    local_ids = df_all["_local_id"].fillna("").astype(str)
    keep_mask = (local_ids == "") | (~local_ids.duplicated(keep="first"))
    df_all = df_all.loc[keep_mask].reset_index(drop=True)

local_df = df_all[df_all["_source"] == "local"].copy()
sheet_df = df_all[df_all["_source"] == "sheet"].copy()

if not local_df.empty:
    persist_local_df(df_all)


# ============================================================
# TOP ACTION BAR
# ============================================================

a1, a2, a3, a4 = st.columns([1.5, 1.5, 1.5, 2.2])

with a1:
    if st.button("☁️ BACKUP TO SHEET", use_container_width=True):
        if local_df.empty:
            st.info("✅ Everything is already backed up.")
        else:
            failed = []
            progress = st.progress(0)
            total = len(local_df)

            for pos, (_, row) in enumerate(local_df.iterrows(), 1):
                ok, msg = api_post({
                    "action": "add",
                    "created_at": str(row["created_at"]),
                    "name": str(row["name"]),
                    "mobile": str(row["mobile"]),
                    "service": str(row["service"]),
                    "amount": str(row["amount"]),
                    "payment": str(row["payment"]),
                    "expiry": str(row["expiry"]),
                    "local_id": str(row["_local_id"])
                })

                if not ok:
                    failed.append(f"{row['name']}: {msg}")

                progress.progress(pos / total)

            if not failed:
                fresh, err = fetch_sheet_records()
                if not err:
                    st.session_state.records_cache = fresh

                local_storage_clear()
                st.session_state.local_boot_loaded = False
                st.session_state.success_message = (
                    f"☁️ Backup complete — {total} entries safely saved to Google Sheet."
                )
                st.rerun()
            else:
                persist_local_df(df_all)
                st.error("Some entries could not be backed up. Your local copy is safe.")
                st.code("\n".join(failed))

with a2:
    if st.button("🔄 LOAD FROM SHEET", use_container_width=True):
        fresh, err = fetch_sheet_records()
        if err:
            st.error(err)
        else:
            pending_local = (
                st.session_state.records_cache[
                    st.session_state.records_cache["_source"] == "local"
                ].copy()
                if not st.session_state.records_cache.empty
                else empty_df()
            )

            st.session_state.records_cache = pd.concat(
                [fresh, pending_local],
                ignore_index=True
            )
            st.session_state.last_load_error = ""
            st.success("✅ Records loaded from Google Sheet. Pending local entries were kept safe.")
            st.rerun()

with a3:
    st.metric("CUSTOMERS", len(df_all))

with a4:
    st.markdown(
        f"""
        <div class='small-muted' style='text-align:right;padding-top:10px'>
        ⚡ Pending Backup: <b>{len(local_df)}</b> &nbsp; | &nbsp;
        ☁️ Sheet Records: <b>{len(sheet_df)}</b> &nbsp; | &nbsp;
        🔐 Local Safety: <b>ON</b>
        </div>
        """,
        unsafe_allow_html=True
    )

if st.session_state.get("last_load_error"):
    st.warning("Google Sheet could not be loaded. New entries will remain safely in local storage until backup.")
    st.caption(st.session_state.last_load_error)


# ============================================================
# DATE VIEW
# ============================================================

current_date = st.session_state.selected_date.strftime("%Y-%m-%d")

if not df_all.empty:
    date_values = (
        pd.to_datetime(df_all["created_at"], errors="coerce")
        .dt.strftime("%Y-%m-%d")
        .fillna("")
    )
    day_df = df_all[date_values == current_date].copy()
else:
    day_df = empty_df()

prev_col, date_col, next_col = st.columns([1, 5, 1])

with prev_col:
    if st.button("❮ PREVIOUS", use_container_width=True):
        st.session_state.selected_date -= timedelta(days=1)
        st.rerun()

with date_col:
    picked = st.date_input("📅 Working Date", value=st.session_state.selected_date, key="working_date")
    if picked != st.session_state.selected_date:
        st.session_state.selected_date = picked
        st.rerun()

with next_col:
    if st.button("NEXT ❯", use_container_width=True):
        st.session_state.selected_date += timedelta(days=1)
        st.rerun()


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs([
    "📊 DAILY VIEW & ADD ENTRY",
    "🔔 RENEWAL ALERTS",
    "📂 CURRENT RECORDS"
])


# ============================================================
# TAB 1
# ============================================================

with tab1:
    st.markdown(
        f"""
        <div class='nc-section'>
        📋 Entries for {st.session_state.selected_date.strftime('%d-%m-%Y (%A)')}
        </div>
        """,
        unsafe_allow_html=True
    )

    if not day_df.empty:
        cash = int(day_df.loc[day_df["payment"].str.strip().str.lower() == "cash", "amount"].sum())
        online = int(day_df.loc[day_df["payment"].str.strip().str.lower() == "online", "amount"].sum())
    else:
        cash = 0
        online = 0

    m1, m2, m3 = st.columns(3)
    m1.metric("DAY TOTAL", f"₹ {cash + online:,}")
    m2.metric("DAY CASH", f"₹ {cash:,}")
    m3.metric("DAY ONLINE / UPI", f"₹ {online:,}")

    st.markdown("---")

    if day_df.empty:
        st.info("ℹ️ No entries recorded for this date yet.")
    else:
        show_day = day_df.drop(columns=["_row_number", "_source", "_local_id"], errors="ignore").reset_index(drop=True)
        show_day.insert(0, "Status", ["☁️ Sheet" if x == "sheet" else "⚡ Local" for x in day_df["_source"]])
        st.dataframe(show_day, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("<div class='nc-section'>➕ Add Customer Entry</div>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        name = st.text_input("Customer Name*", key="add_name")
        mobile = st.text_input("Mobile Number*", key="add_mobile")
        service = st.selectbox("Search / Select Service*", SERVICES, key="add_service")

        if service == "Other":
            custom_service = st.text_input(
                "Custom Service Name*",
                key="add_custom_service",
                placeholder="Enter new service name..."
            )
        else:
            custom_service = ""

    with right:
        amount = st.number_input("Amount (₹)", min_value=0, step=10, key="add_amount")
        payment = st.radio("Payment Mode", ["Cash", "Online"], horizontal=True, key="add_payment")
        has_expiry = st.checkbox("Requires Renewal / Validity?", key="add_expiry_check")
        validity_unit = st.selectbox("Validity Unit", ["Days", "Months", "Years"], index=1, key="add_validity_unit")
        validity_value = st.number_input("Validity Duration", min_value=1, value=1, key="add_validity_value")

    if st.button("⚡ SAVE ENTRY", type="primary", use_container_width=True):
        if not name.strip() or not mobile.strip():
            st.error("Please enter Customer Name and Mobile Number.")
        else:
            final_service = service
            if service == "Other":
                if not custom_service.strip():
                    st.error("Please enter the custom service name.")
                    st.stop()
                final_service = custom_service.strip()

                if final_service not in st.session_state.custom_services:
                    st.session_state.custom_services.append(final_service)
                    st.session_state.custom_services = sorted(
                        set(st.session_state.custom_services),
                        key=lambda x: x.lower()
                    )

            expiry = "N/A"
            if has_expiry:
                base = st.session_state.selected_date
                if validity_unit == "Days":
                    expiry_date = base + timedelta(days=int(validity_value))
                elif validity_unit == "Months":
                    expiry_date = base + relativedelta(months=int(validity_value))
                else:
                    expiry_date = base + relativedelta(years=int(validity_value))

                expiry = expiry_date.strftime("%Y-%m-%d")

            st.session_state.local_counter += 1

            new_row = {
                "created_at": current_date,
                "name": name.strip(),
                "mobile": mobile.strip(),
                "service": final_service,
                "amount": int(amount),
                "payment": payment,
                "expiry": expiry,
                "_row_number": -st.session_state.local_counter,
                "_source": "local",
                "_local_id": uuid.uuid4().hex
            }

            st.session_state.records_cache = pd.concat(
                [df_all, pd.DataFrame([new_row])],
                ignore_index=True
            )

            persist_local_df(st.session_state.records_cache)
            st.session_state.success_message = (
                f"✅ {name} added successfully. Entry is safely stored locally. Press BACKUP TO SHEET to sync it."
            )
            st.rerun()


# ============================================================
# TAB 2
# ============================================================

with tab2:
    st.markdown("<div class='nc-section'>🔔 Renewal Alerts — Next 15 Days</div>", unsafe_allow_html=True)

    found = False
    today = today_ist()

    if not df_all.empty:
        for _, row in df_all.iterrows():
            try:
                exp = str(row["expiry"]).strip()
                if exp and exp != "N/A":
                    exp_date = datetime.strptime(exp[:10], "%Y-%m-%d").date()
                    days_left = (exp_date - today).days

                    if 0 <= days_left <= 15:
                        found = True
                        formatted = exp_date.strftime("%d-%m-%Y")

                        st.markdown(
                            f"""
                            <div class='nc-card'>
                            <b>🔴 {row['name']}</b><br>
                            {row['service']}<br>
                            Expiry: <b>{formatted}</b> • {days_left} days left
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        msg = (
                            f"Hello {row['name']}, your {row['service']} is expiring on {formatted}. "
                            f"Please visit NOOR CYBER WORLD for renewal."
                        )
                        wa = f"https://wa.me/91{row['mobile']}?text={quote(msg)}"
                        st.link_button("💬 SEND WHATSAPP MESSAGE", wa)

            except Exception:
                continue

    if not found:
        st.success("🎉 No renewals due in the next 15 days.")


# ============================================================
# TAB 3
# ============================================================

with tab3:
    st.markdown("<div class='nc-section'>📂 Current Customer Records</div>", unsafe_allow_html=True)

    if df_all.empty:
        st.info("No customer records available.")
    else:
        export_df = df_all.drop(columns=["_row_number", "_source", "_local_id"], errors="ignore")

        b1, b2 = st.columns(2)
        with b1:
            st.download_button(
                "📥 DOWNLOAD CSV",
                data=export_df.to_csv(index=False).encode("utf-8-sig"),
                file_name="NOOR_CYBER_WORLD_RECORDS.csv",
                mime="text/csv",
                use_container_width=True
            )
        with b2:
            st.download_button(
                "📄 DOWNLOAD PDF",
                data=make_pdf(export_df),
                file_name="NOOR_CYBER_WORLD_RECORDS.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        st.markdown("---")

        # ====================================================
        # EDIT
        # ====================================================
        if st.session_state.edit_key is not None:
            selected = df_all[df_all["_row_number"] == st.session_state.edit_key]

            if not selected.empty:
                row = selected.iloc[0]

                st.markdown("<div class='nc-section'>✏️ Edit Customer</div>", unsafe_allow_html=True)

                e1, e2 = st.columns(2)
                with e1:
                    e_date = st.text_input("Date", str(row["created_at"]), key="e_date")
                    e_name = st.text_input("Customer Name", str(row["name"]), key="e_name")
                    e_mobile = st.text_input("Mobile", str(row["mobile"]), key="e_mobile")
                    e_service = st.text_input("Service", str(row["service"]), key="e_service")

                with e2:
                    e_amount = st.number_input("Amount ₹", min_value=0, value=int(float(row["amount"])), step=10, key="e_amount")
                    e_payment = st.selectbox(
                        "Payment",
                        ["Cash", "Online"],
                        index=1 if str(row["payment"]).lower() == "online" else 0,
                        key="e_payment"
                    )
                    e_expiry = st.text_input("Expiry", str(row["expiry"]), key="e_expiry")

                x1, x2 = st.columns(2)
                with x1:
                    if st.button("💾 SAVE CHANGES", type="primary", use_container_width=True):
                        row_no = sheet_row(row)

                        if row_no < 2:
                            mask = st.session_state.records_cache["_row_number"] == st.session_state.edit_key
                            st.session_state.records_cache.loc[
                                mask,
                                ["created_at", "name", "mobile", "service", "amount", "payment", "expiry"]
                            ] = [e_date, e_name, e_mobile, e_service, e_amount, e_payment, e_expiry]

                            persist_local_df(st.session_state.records_cache)
                            st.session_state.edit_key = None
                            st.session_state.success_message = "✅ Local customer updated and safely stored."
                            st.rerun()
                        else:
                            ok, msg = api_post({
                                "action": "update",
                                "row_number": str(row_no),
                                "created_at": e_date,
                                "name": e_name,
                                "mobile": e_mobile,
                                "service": e_service,
                                "amount": str(e_amount),
                                "payment": e_payment,
                                "expiry": e_expiry
                            })

                            if ok:
                                fresh, err = fetch_sheet_records()
                                if not err:
                                    pending_local = (
                                        st.session_state.records_cache[
                                            st.session_state.records_cache["_source"] == "local"
                                        ].copy()
                                        if not st.session_state.records_cache.empty
                                        else empty_df()
                                    )
                                    st.session_state.records_cache = pd.concat([fresh, pending_local], ignore_index=True)

                                st.session_state.edit_key = None
                                st.session_state.success_message = "✅ Customer updated successfully."
                                st.rerun()
                            else:
                                st.error(msg)

                with x2:
                    if st.button("❌ CANCEL EDIT", use_container_width=True):
                        st.session_state.edit_key = None
                        st.rerun()

                st.markdown("---")

        # ====================================================
        # DELETE
        # ====================================================
        if st.session_state.delete_key is not None:
            selected = df_all[df_all["_row_number"] == st.session_state.delete_key]

            if not selected.empty:
                row = selected.iloc[0]

                st.warning(f"Delete '{row['name']}' ({row['mobile']})?")

                x1, x2 = st.columns(2)
                with x1:
                    if st.button("✅ YES, DELETE", type="primary", use_container_width=True):
                        row_no = sheet_row(row)

                        if row_no < 2:
                            mask = st.session_state.records_cache["_row_number"] == st.session_state.delete_key
                            st.session_state.records_cache = st.session_state.records_cache[~mask].reset_index(drop=True)

                            persist_local_df(st.session_state.records_cache)
                            st.session_state.delete_key = None
                            st.session_state.success_message = "🗑️ Local customer deleted."
                            st.rerun()
                        else:
                            ok, msg = api_post({
                                "action": "delete",
                                "row_number": str(row_no)
                            })

                            if ok:
                                fresh, err = fetch_sheet_records()
                                if not err:
                                    pending_local = (
                                        st.session_state.records_cache[
                                            st.session_state.records_cache["_source"] == "local"
                                        ].copy()
                                        if not st.session_state.records_cache.empty
                                        else empty_df()
                                    )
                                    st.session_state.records_cache = pd.concat([fresh, pending_local], ignore_index=True)

                                st.session_state.delete_key = None
                                st.session_state.success_message = "🗑️ Customer deleted successfully."
                                st.rerun()
                            else:
                                st.error(msg)

                with x2:
                    if st.button("❌ CANCEL", use_container_width=True):
                        st.session_state.delete_key = None
                        st.rerun()

                st.markdown("---")

        # ====================================================
        # RECORD LIST
        # ====================================================
        st.markdown(
            f"""
            <div class='small-muted'>
            ☁️ Sheet: {len(sheet_df)} &nbsp;&nbsp; ⚡ Pending Backup: {len(local_df)}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("")

        for _, row in df_all.iterrows():
            source_icon = "☁️" if row["_source"] == "sheet" else "⚡"

            st.markdown(
                f"""
                <div class='nc-card'>
                <b>{source_icon} {row['name']}</b>
                <span style='color:#94a3b8'> • {row['mobile']}</span><br>
                <span style='color:#cbd5e1'>{row['service']}</span><br>
                <b>₹ {float(row['amount']):,.0f}</b> • {row['payment']} • {row['created_at']} • Expiry: {row['expiry']}
                </div>
                """,
                unsafe_allow_html=True
            )

            q1, q2, _ = st.columns([1, 1, 8])
            key = int(row["_row_number"])

            with q1:
                if st.button("✏️ EDIT", key=f"edit_{key}", use_container_width=True):
                    st.session_state.edit_key = key
                    st.session_state.delete_key = None
                    st.rerun()

            with q2:
                if st.button("🗑️ DELETE", key=f"delete_{key}", use_container_width=True):
                    st.session_state.delete_key = key
                    st.session_state.edit_key = None
                    st.rerun()


# ============================================================
# SUCCESS TOAST
# ============================================================

if "success_message" in st.session_state:
    st.toast(st.session_state.pop("success_message"), icon="✅")
