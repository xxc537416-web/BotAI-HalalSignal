# app.py - BotAI with simple password protection (password pre-set)
# Requirements: pandas, streamlit, numpy
# Save and run: streamlit run app.py

import os
import streamlit as st
import pandas as pd
import hashlib

# -----------------------
# CONFIG: your password (pre-set fallback)
# -----------------------
# You gave: xx5xx5xx5xx5
FALLBACK_PASSWORD = "xx5xx5xx5xx5"   # <-- your provided password (change later if needed)

# Use environment variable if available (recommended)
PASSWORD = os.getenv("ST_APP_PASSWORD", FALLBACK_PASSWORD)

# If you want to store a SHA256 hash in ST_APP_PASSWORD, set USE_HASHED = True and
# provide the hex digest in environment variable. By default we use plain text.
USE_HASHED = False

def verify_password(input_password: str) -> bool:
    if USE_HASHED:
        hashed_input = hashlib.sha256(input_password.encode()).hexdigest()
        return hashed_input == PASSWORD
    else:
        return input_password == PASSWORD

# -----------------------
# SESSION: simple login/logout
# -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def do_login():
    st.session_state.logged_in = True

def do_logout():
    st.session_state.logged_in = False

# -----------------------
# LOGIN UI
# -----------------------
st.set_page_config(page_title="BotAI - Halal Signal (Protected)", layout="wide")

if not st.session_state.logged_in:
    st.title("BotAI - লগইন করুন 🔐")
    st.markdown("অ্যাক্সেস পেতে পাসওয়ার্ড দিন। (প্রশাসক ছাড়া কেউ প্রবেশ পারবে না)")
    pw = st.text_input("পাসওয়ার্ড", type="password")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("লগইন"):
            if verify_password(pw):
                do_login()
                st.experimental_rerun()
            else:
                st.error("পাসওয়ার্ড ভুল — আবার চেষ্টা করুন।")
    with col2:
        st.write("")  # empty column to align
    st.caption("উল্লেখ্য: নিরাপদভাবে পরিবেশন (production) করতে Streamlit Cloud private apps বা OAuth ব্যবহার করাই ভালো।")
    st.stop()

# -----------------------
# MAIN APP (after login)
# -----------------------
st.sidebar.button("লগআউট", on_click=do_logout)
st.title("ডিএসই হালাল এআই সিগনাল জেনারেটর 🎯 — BotAI (Protected)")
st.warning("এই সিস্টেম শিক্ষামূলক ও ডেমো-উপযোগী; বিনিয়োগ পরামর্শ নয়।")

# --- Dummy DataFrame with 10+ stocks ---
data = {
    'Code': ['A1','B2','C3','D4','E5','F6','G7','H8','I9','J10'],
    'Close Price':[120,85,60,200,45,150,90,70,110,130],
    '50MA':[100,80,65,180,50,140,85,65,100,120],
    'RSI':[35,75,40,50,65,38,72,45,30,55],
    'MACD_Line':[1.2,-0.5,0.8,0.6,0.3,1.0,-0.2,0.5,1.5,0.7],
    'Signal_Line':[0.8,-0.3,0.6,0.5,0.4,0.9,-0.1,0.4,1.2,0.6],
    'Volume':[1500,1200,1800,2000,900,1600,1100,1300,1700,1900],
    'Avg_Volume':[1000,1000,1500,1800,800,1500,1000,1200,1600,1800],
    'EPS_Growth':[12,8,15,9,5,11,7,10,14,12],
    'Debt_Ratio':[20,40,30,25,10,35,15,50,28,32],
    'Non_Comp_Income_Ratio':[2,6,4,1,3,2,0,7,4,5],
    'Liquid_Assets_Ratio':[40,60,35,20,45,50,30,55,48,42],
    'Sector':['Pharma','Bank','Conventional Finance','Pharma','Insurance','Pharma','Bank','Pharma','Conventional Finance','Pharma']
}
df = pd.DataFrame(data)

# --- Halal Filter ---
def halal_filter(row):
    return (row['Debt_Ratio']<=33 and row['Non_Comp_Income_Ratio']<=5
            and row['Liquid_Assets_Ratio']<=49 and row['Sector'] not in ['Bank','Insurance'])

# --- Signal Generation ---
def generate_signal(row):
    if not row['Halal']:
        return 'Excluded (Non-Halal)','-','-','Failed Shariah Filter'
    if (row['Close Price']>row['50MA'] and row['RSI']<=40 and 
        row['MACD_Line']>row['Signal_Line'] and row['Volume']>1.5*row['Avg_Volume']
        and row['EPS_Growth']>=10):
        return 'STRONG BUY','▲','Short-Term','Halal ✅ | Price>50MA | RSI low | MACD>Signal | Volume spike | EPS growth'
    elif row['Close Price']<row['50MA'] and row['RSI']>=70:
        return 'SELL','▼','Short-Term','Halal ✅ | Price<50MA | RSI high'
    else:
        return 'HOLD','→','Short-Term','Halal ✅ | Conditions for BUY/SELL not met'

# --- Streamlit Selector for Time Frame (UI only, dummy data currently) ---
time_frame = st.selectbox("সময় ফ্রেম নির্বাচন করুন", ['1 Minute', '1 Day', '1 Month'])
st.subheader(f"Signals for {time_frame}")

# Apply Halal Filter and Signal
df['Halal'] = df.apply(halal_filter, axis=1)
df[['Signal Type','Direction','Time Horizon','AI Reason']] = df.apply(generate_signal, axis=1, result_type='expand')

# Final Table
final_df = df[['Code','Close Price','Signal Type','Direction','Time Horizon','AI Reason']]
final_df = final_df.rename(columns={'Close Price':'Close Price (৳)'})
st.subheader("চূড়ান্ত সিগনাল টেবিল")
st.dataframe(final_df.style.format({"Close Price (৳)": "{:,.2f}"}), use_container_width=True)

st.markdown("---")
st.caption("নোট: প্রোডাকশনে শক্তিশালী অথেনটিকেশনের জন্য Streamlit Cloud private app, OAuth বা ওয়েব সার্ভারে Basic Auth ব্যবহার করুন।")
