import streamlit as st
import ee
import geemap.foliumap as geemap
from streamlit_folium import st_folium
import requests
import pandas as pd
import plotly.graph_objects as go

# --- 1. PERMANENT HANDSHAKE SOLUTION ---
auth_success = False
if "EE_PRIVATE_KEY" in st.secrets:
    try:
        # Connect using individual secret parts
        credentials = ee.ServiceAccountCredentials(
            st.secrets["EE_CLIENT_EMAIL"],
            key_data=st.secrets["EE_PRIVATE_KEY"]
        )
        ee.Initialize(credentials, project=st.secrets["EE_PROJECT_ID"])
        auth_success = True
        st.sidebar.success("🛰️ Satellite Handshake: OK")
    except Exception as e:
        st.sidebar.error(f"Handshake Failed: {e}")

# --- 2. MULTI-LANGUAGE ---
langs = {
    "English": {"t":"Global Irrigation Intelligence", "b1":"☀️ Weather", "b2":"📅 12-Month", "b3":"🏛️ Past 20yr", "b4":"🚀 Future NASA", "b5":"🛰️ Map"},
    "Amharic (አማርኛ)": {"t":"የርቀት መስኖ መረጃ", "b1":"☀️ የአየር ሁኔታ", "b2":"📅 የ12 ወራት", "b3":"🏛️ የ20 ዓመት ታሪክ", "b4":"🚀 የወደፊት ትንበያ", "b5":"🛰️ የሳተላይት ካርታ"},
    "Oromo (Afaan Oromoo)": {"t":"Odeeffannoo Jallisii", "b1":"☀️ Haala Qilleensaa", "b2":"📅 Karoora Waggaa", "b3":"🏛️ Seenaa Waggaa 20", "b4":"🚀 Raaggaa Fulduuraa", "b5":"🛰️ Kaartaa"},
    "Somali (Soomaali)": {"t":"Sirdoonka Waraabka", "b1":"☀️ Hawada", "b2":"📅 Qorshaha Sannadka", "b3":"🏛️ Taariikhda 20 Sano", "b4":"🚀 Saadaasha Mustaqbalka", "b5":"🛰️ Khariidadda"}
}

st.set_page_config(layout="wide", page_title="Irrigation Pro")
sel_lang = st.sidebar.selectbox("🌐 Language", list(langs.keys()))
tx = langs[sel_lang]
st.title(tx['t'])

# --- 3. LOCATION & SOIL ---
lat = st.sidebar.number_input("Latitude", value=7.9000, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=38.7000, format="%.4f")
soil_type = "CLAY LOAM (Detected)" # Default

# --- 4. TABS (SEPARATED) ---
t = st.tabs([tx['b1'], tx['b2'], tx['b3'], tx['b4'], tx['b5']])

# TAB 1: WEATHER
with t[0]:
    st.subheader("☀️ Daily & Weekly Weather")
    try:
        u = f"https://api.ope
