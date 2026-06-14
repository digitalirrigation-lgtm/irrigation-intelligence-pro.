import streamlit as st
import ee
import geemap
from streamlit_folium import st_folium
import json
import requests
import pandas as pd
import plotly.graph_objects as go

# --- 1. SATELLITE HANDSHAKE FIX ---
auth_success = False
if 'EARTH_ENGINE_KEY' in st.secrets:
    try:
        # Load secret and handle the backslash problem
        raw_key = st.secrets['EARTH_ENGINE_KEY']
        info = json.loads(raw_key, strict=False)
        # Ensure newlines are correct in the private key
        info['private_key'] = info['private_key'].replace('\\n', '\n')
        
        credentials = ee.ServiceAccountCredentials(info['client_email'], key_data=json.dumps(info))
        ee.Initialize(credentials, project='irrigation-intelligence-pro')
        auth_success = True
        st.sidebar.success("Satellite Handshake: SUCCESS ✅")
    except Exception as e:
        st.sidebar.error(f"Handshake Error: {e}")

# --- 2. MULTI-LANGUAGE DICTIONARY ---
languages = {
    "English": {"title": "Global Irrigation Intelligence", "t1": "☀️ Weather (7-Day)", "t2": "📅 12-Month Plan", "t3": "🏛️ 20yr Past", "t4": "🚀 20yr Future", "t5": "🛰️ Map"},
    "Amharic (አማርኛ)": {"title": "የአለም አቀፍ የመስኖ መረጃ", "t1": "☀️ የአየር ሁኔታ", "t2": "📅 የ12 ወራት እቅድ", "t3": "🏛️ የ20 ዓመት ታሪክ", "t4": "🚀 የ20 ዓመት ትንበያ", "t5": "🛰️ ሳተላይት ካርታ"},
    "Oromo (Afaan Oromoo)": {"title": "Odeeffannoo Jallisii", "t1": "☀️ Haala Qilleensaa", "t2": "📅 Karoora Waggaa", "t3": "🏛️ Seenaa Waggaa 20", "t4": "🚀 Saadaasha Mustaqbalka", "t5": "🛰️ Kaartaa"},
    "Somali (Soomaali)": {"title": "Sirdoonka Waraabka", "t1": "☀️ Hawada", "t2": "📅 Qorshaha Sannadka", "t3": "🏛️ Taariikhda 20 Sano", "t4": "🚀 Mustaqbalka 20 Sano", "t5": "🛰️ Khariidadda"}
}

# --- 3. UI CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Master Irrigation")
lang = st.sidebar.selectbox("🌐 Language Selection", list(languages.keys()))
t = languages[lang]
st.title(t['title'])

st.sidebar.header("📍 Location")
city = st.sidebar.text_input("Farm Name", "Ziway Project")
lat = st.sidebar.number_input("Latitude", value=7.9000, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=38.7000, format="%.4f")

# --- 4. DATA TABS (SEPARATED AS REQUESTED) ---
tabs = st.tabs([t['t1'], t['t2'], t['t3'], t['t4'], t['t5']])

# TAB 1: WEATHER (DAILY & WEEKLY)
with tabs[0]:
    st.subheader("☀️ Daily & Weekly Weather")
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probab
