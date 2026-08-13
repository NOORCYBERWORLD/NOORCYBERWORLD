import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Page Config
st.set_page_config(page_title="NOOR CYBER WORLD", page_icon="🖥️", layout="wide")

# App Header
st.title("🖥️ NOOR CYBER WORLD")
st.caption("Center Management & Automatic Renewal Reminder System")

# Session State for Data Storage
if "records" not in st.session_state:
    st.session_state.records = [
        {
            "नाम": "रहीम शेख",
            "मोबाइल": "9800000000",
            "सर्विस": "Vehicle Insurance",
            "अमाउंट": 1500,
            "पेमेंट": "Online",
            "एक्सपायरी": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        },
        {
            "नाम": "अमित शर्मा",
            "मोबाइल": "9700000000",
            "सर्विस": "Food License",
            "अमाउंट": 500,
            "पेमेंट": "Cash",
            "एक्सपायरी": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        }
    ]

# Navigation
menu = ["📊 Dashboard", "➕ New Entry", "🔔 Renewal Alerts (15 Days)", "💰 Cashbook Report"]
choice = st.sidebar.selectbox("नेविगेशन मेनू", menu)

# 1. DASHBOARD
if choice == "📊 Dashboard":
    st.subheader("आज का ओवरव्यू (Daily Overview)")
    df = pd.DataFrame(st.session_state.records)
    
    total_cash = int(df[df["पेमेंट"] == "Cash"]["अमाउंट"].sum()) if not df.empty else 0
    total_online = int(df[df["पेमेंट"] == "Online"]["अमाउंट"].sum()) if not df.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("कुल कलेक्शन (Total)", f"₹ {total_cash + total_online}")
    col2.metric("कैश कलेक्शन (Cash)", f"₹ {total_cash}")
    col3.metric("ऑनलाइन/UPI (Online)", f"₹ {total_online}")
    
    st.markdown("---")
    st.subheader("📋 हाल ही में की गई एंट्रीज़")
    st.dataframe(df, use_container_width=True)

# 2. NEW ENTRY
elif choice == "➕ New Entry":
    st.subheader("ग्राहक एवं नई सर्विस एंट्री")
    with st.form("entry_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input("ग्राहक का नाम (Customer Name)*")
            mobile = st.text_input("मोबाइल नंबर (Mobile Number)*")
            service = st.selectbox("सर्विस चुनें", ["PAN Card", "Vehicle Insurance", "DL/RC", "Food License", "Passport", "Income Certificate", "Aadhaar Work", "Other"])
        
        with col_b:
            amount = st.number_input("फीस / बिल (₹)*", min_value=0, step=10)
            pay_mode = st.radio("पेमेंट मोड", ["Cash", "Online"])
            has_expiry = st.checkbox("क्या इसका रिन्यूअल होता है? (जैसे Insurance, DL)")
            expiry_date = None
            if has_expiry:
                expiry_date = st.date_input("एक्सपायरी डेट (Expiry Date)")

        submitted = st.form_submit_button("💾 डेटा सुरक्षित सेव करें")
        
        if submitted:
            if name and mobile:
                exp_str = expiry_date.strftime("%Y-%m-%d") if expiry_date else "N/A"
                new_data = {
                    "नाम": name,
                    "मोबाइल": mobile,
                    "सर्विस": service,
                    "अमाउंट": amount,
                    "पेमेंट": pay_mode,
                    "एक्सपायरी": exp_str
                }
                st.session_state.records.append(new_data)
                st.success(f"✅ {name} की डेटा एंट्री सेव हो गई!")
            else:
                st.error("कृपया नाम और मोबाइल नंबर ज़रूर भरें!")

# 3. RENEWAL ALERTS
elif choice == "🔔 Renewal Alerts (15 Days)":
    st.subheader("⚠️ अगले 15 दिनों में एक्सपायर होने वाले डॉक्यूमेंट्स")
    
    today = datetime.now().date()
    alerts = []
    
    for item in st.session_state.records:
        if item["एक्सपायरी"] != "N/A":
            exp_d = datetime.strptime(item["एक्सपायरी"], "%Y-%m-%d").date()
            days_left = (exp_d - today).days
            if 0 <= days_left <= 15:
                msg = f"नमस्ते {item['नाम']}, आपका {item['सर्विस']} दिनांक {item['एक्सपायरी']} को एक्सपायर हो रहा है। रिन्यू कराने के लिए आज ही NOOR CYBER WORLD पर आएं।"
                whatsapp_url = f"https://wa.me/91{item['मोबाइल']}?text={msg.replace(' ', '%20')}"
                alerts.append({
                    "नाम": item["नाम"],
                    "मोबाइल": item["मोबाइल"],
                    "सर्विस": item["सर्विस"],
                    "एक्सपायरी": item["एक्सपायरी"],
                    "दिन बचे": f"{days_left} दिन",
                    "link": whatsapp_url
                })
                
    if alerts:
        st.warning(f"कुल {len(alerts)} ग्राहकों के रिन्यूअल अगले 15 दिनों में ड्यू हैं!")
        for alert in alerts:
            with st.expander(f"🔴 {alert['नाम']} - {alert['सर्विस']} ({alert['दिन बचे']})"):
                st.write(f"**मोबाइल:** {alert['मोबाइल']}")
                st.write(f"**एक्सपायरी:** {alert['एक्सपायरी']}")
                st.markdown(f"[💬 ग्राहक को WhatsApp मैसेज भेजें]({alert['link']})")
    else:
        st.info("🎉 अगले 15 दिनों में कोई रिन्यूअल ड्यू नहीं है।")

# 4. CASHBOOK REPORT
elif choice == "💰 Cashbook Report":
    st.subheader("दैनिक हिसाब-किताब (Cashbook)")
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df, use_container_width=True)
