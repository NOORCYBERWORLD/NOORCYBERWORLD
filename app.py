import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Page Config
st.set_page_config(page_title="NOOR CYBER WORLD", page_icon="🖥️", layout="wide")

# App Header
st.title("🖥️ NOOR CYBER WORLD")
st.caption("Center Management & Automatic Renewal Reminder System")

# Session State for Dynamic Services List (Auto-Add Feature)
if "services_list" not in st.session_state:
    st.session_state.services_list = [
        "Aadhaar Card Download / Update",
        "PAN Card New / Correction",
        "Voter ID Card Apply / Correction",
        "Ration Card Services",
        "Ayushman Bharat Card",
        "E-Shram Card",
        "Income Certificate (आय प्रमाण पत्र)",
        "Caste Certificate (जाति प्रमाण पत्र)",
        "Domicile Certificate (निवास प्रमाण पत्र)",
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
        "Other (अन्य)"
    ]

# Session State for Data Storage
if "records" not in st.session_state:
    st.session_state.records = [
        {"नाम": "रहीम शेख", "मोबाइल": "9800000000", "सर्विस": "Driving License (LL/DL) & RC Services", "अमाउंट": 1500, "पेमेंट": "Online", "एक्सपायरी": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")},
        {"नाम": "अमित शर्मा", "मोबाइल": "9700000000", "सर्विस": "Shop Act License / FSSAI Food License", "अमाउंट": 500, "पेमेंट": "Cash", "एक्सपायरी": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")}
    ]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ New Entry", "🔔 Renewal Alerts", "⚙️ Manage Entries (Edit/Delete)"])

# TAB 1: DASHBOARD
with tab1:
    st.subheader("आज का ओवरव्यू")
    df = pd.DataFrame(st.session_state.records)
    total_cash = int(df[df["पेमेंट"] == "Cash"]["अमाउंट"].sum()) if not df.empty else 0
    total_online = int(df[df["पेमेंट"] == "Online"]["अमाउंट"].sum()) if not df.empty else 0
    col1, col2, col3 = st.columns(3)
    col1.metric("कुल कलेक्शन", f"₹ {total_cash + total_online}")
    col2.metric("कैश", f"₹ {total_cash}")
    col3.metric("ऑनलाइन", f"₹ {total_online}")
    st.dataframe(df, use_container_width=True)

# TAB 2: NEW ENTRY
with tab2:
    st.subheader("नई एंट्री")
    with st.form("entry_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input("ग्राहक का नाम*")
            mobile = st.text_input("मोबाइल नंबर*")
            selected_service = st.selectbox("सर्विस चुनें या नाम टाइप करके खोजें (Search Service)*", st.session_state.services_list)
            
            # Show Textbox if 'Other (अन्य)' is selected
            custom_service_name = ""
            if selected_service == "Other (अन्य)":
                custom_service_name = st.text_input("सर्विस का नाम दर्ज करें (यह लिस्ट में Auto Add हो जाएगा)*")

        with col_b:
            amount = st.number_input("अमाउंट (₹)", min_value=0, step=10)
            pay_mode = st.radio("पेमेंट मोड", ["Cash", "Online"])
            has_expiry = st.checkbox("क्या रिन्यूअल होता है?")
            expiry_date = st.date_input("एक्सपायरी डेट") if has_expiry else None
            
        if st.form_submit_button("💾 डेटा सेव करें"):
            if name and mobile:
                # Final service selection logic
                final_service = selected_service
                if selected_service == "Other (अन्य)":
                    if custom_service_name.strip():
                        final_service = custom_service_name.strip()
                        # Auto Add to Master Services List before 'Other (अन्य)'
                        if final_service not in st.session_state.services_list:
                            st.session_state.services_list.insert(-1, final_service)
                    else:
                        st.error("कृपया अन्य सर्विस का नाम लिखें!")
                        st.stop()
                
                st.session_state.records.append({
                    "नाम": name, 
                    "मोबाइल": mobile, 
                    "सर्विस": final_service, 
                    "अमाउंट": amount, 
                    "पेमेंट": pay_mode, 
                    "एक्सपायरी": expiry_date.strftime("%Y-%m-%d") if expiry_date else "N/A"
                })
                st.success(f"✅ नई एंट्री ({final_service}) सेव हो गई!")
                st.rerun()
            else:
                st.error("कृपया नाम और मोबाइल नंबर भरें!")

# TAB 3: ALERTS
with tab3:
    st.subheader("⚠️ रिन्यूअल अलर्ट्स (अगले 15 दिन)")
    today = datetime.now().date()
    alerts_found = False
    for item in st.session_state.records:
        if item["एक्सपायरी"] != "N/A":
            exp_d = datetime.strptime(item["एक्सपायरी"], "%Y-%m-%d").date()
            days_left = (exp_d - today).days
            if 0 <= days_left <= 15:
                alerts_found = True
                msg = f"नमस्ते {item['नाम']}, आपका {item['सर्विस']} दिनांक {item['एक्सपायरी']} को समाप्त हो रहा है। नवीनीकरण के लिए आज ही NOOR CYBER WORLD आएं।"
                wa_link = f"https://wa.me/91{item['मोबाइल']}?text={msg.replace(' ', '%20')}"
                st.warning(f"🔴 **{item['नाम']}** - {item['सर्विस']} (एक्सपायरी: {item['एक्सपायरी']} | {days_left} दिन शेष)")
                st.markdown(f"[💬 ग्राहक को WhatsApp मैसेज भेजें]({wa_link})")
    if not alerts_found:
        st.info("🎉 अगले 15 दिनों में कोई रिन्यूअल ड्यू नहीं है।")

# TAB 4: EDIT/DELETE
with tab4:
    st.subheader("⚙️ एंट्री एडिट (Edit) या डिलीट (Delete) करें")
    if not st.session_state.records:
        st.info("अभी कोई डेटा उपलब्ध नहीं है।")
    else:
        options = [f"{i+1}. {r['नाम']} - {r['सर्विस']} (₹{r['अमाउंट']})" for i, r in enumerate(st.session_state.records)]
        idx = st.selectbox("जिस एंट्री में बदलाव करना है, उसे चुनें:", range(len(options)), format_func=lambda x: options[x])
        
        curr_rec = st.session_state.records[idx]
        st.markdown("---")
        
        if st.button("🗑️ चुनी हुई एंट्री डिलीट करें", type="primary"):
            st.session_state.records.pop(idx)
            st.success("🗑️ एंट्री डिलीट कर दी गई!")
            st.rerun()
            
        st.markdown("---")
        st.markdown("#### ✏️ चुनी हुई एंट्री एडिट करें:")
        
        with st.form("edit_entry_form"):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                e_name = st.text_input("ग्राहक का नाम", value=curr_rec["नाम"])
                e_mobile = st.text_input("मोबाइल नंबर", value=curr_rec["मोबाइल"])
                
                # Check service index
                s_idx = st.session_state.services_list.index(curr_rec["सर्विस"]) if curr_rec["सर्विस"] in st.session_state.services_list else len(st.session_state.services_list)-1
                e_service = st.selectbox("सर्विस", st.session_state.services_list, index=s_idx)
                
            with col_e2:
                e_amount = st.number_input("अमाउंट (₹)", value=int(curr_rec["अमाउंट"]), step=10)
                e_pay = st.radio("पेमेंट Mode", ["Cash", "Online"], index=0 if curr_rec["पेमेंट"] == "Cash" else 1)
                
            if st.form_submit_button("🔄 अपडेट सेव करें"):
                st.session_state.records[idx]["नाम"] = e_name
                st.session_state.records[idx]["मोबाइल"] = e_mobile
                st.session_state.records[idx]["सर्विस"] = e_service
                st.session_state.records[idx]["अमाउंट"] = e_amount
                st.session_state.records[idx]["पेमेंट"] = e_pay
                st.success("✅ बदलाव सुरक्षित कर दिए गए हैं!")
                st.rerun()
