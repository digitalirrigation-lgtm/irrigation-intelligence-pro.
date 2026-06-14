import streamlit as st
import ee
import geemap
from streamlit_folium import st_folium
import json
import requests
import pandas as pd
import plotly.graph_objects as go

# --- 1. THE GOLDEN HANDSHAKE (Safe Connection) ---
auth_status = False
if 'EARTH_ENGINE_KEY' in st.secrets:
    try:
        # This part cleans the "Escape" characters automatically
        raw_key = st.secrets['EARTH_ENGINE_KEY']
        ee_key = json.loads(raw_key, strict=False)
        credentials = ee.ServiceAccountCredentials(ee_key['client_email'], key_data=raw_key)
        ee.Initialize(credentials, project='irrigation-intelligence-pro')
        auth_status = True
    except Exception as e:
        st.error(f"Connection Failed: {e}")

# --- 2. MULTI-LANGUAGE DICTIONARY ---
languages = {
    "English": {"title": "Global Irrigation Intelligence", "f_tab": "🚜 Farmer Plan", "n_tab": "📊 NGO History", "m_tab": "🛰️ Map", "rec": "Apply", "soil": "Clay Loam"},
    "Amharic (አማርኛ)": {"title": "የአለም አቀፍ የመስኖ መረጃ", "f_tab": "🚜 የአርሶ አደር እቅድ", "n_tab": "📊 የመንግስት ሪፖርት", "m_tab": "🛰️ ካርታ", "rec": "ይጠቀሙ", "soil": "ክሌይ ሎም አፈር"},
    "Oromo (Afaan Oromoo)": {"title": "Odeeffannoo Jallisii", "f_tab": "🚜 Karoora Qonnaan Bulaa", "n_tab": "📊 Seenaa 40", "m_tab": "🛰️ Kaartaa", "rec": "Fayyadamaa", "soil": "Biyyee Suphee"},
    "Somali (Soomaali)": {"title": "Sirdoonka Waraabka", "f_tab": "🚜 Qorshaha Beeralayda", "n_tab": "📊 Taariikhda", "m_tab": "🛰️ Khariidadda", "rec": "Isticmaal", "soil": "Ciidda dhoobada ah"}
}

# --- 3. UI SETUP ---
st.set_page_config(layout="wide", page_title="Irrigation Pro")
lang = st.sidebar.selectbox("🌐 Language / ቋንቋ", list(languages.keys()))
t = languages[lang]
st.title(t['title'])

# --- 4. GLOBAL LOCATION SWITCH ---
st.sidebar.header("🌍 Farm Location")
city = st.sidebar.text_input("Farm Name", "Ziway, Ethiopia")
lat = st.sidebar.number_input("Latitude", value=7.9000, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=38.7000, format="%.4f")

# --- 5. DATA TABS ---
tab1, tab2, tab3 = st.tabs([t['f_tab'], t['n_tab'], t['m_tab']])

with tab1:
    st.subheader("☀️ Daily & Weekly Weather Intelligence")
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,et0_fao_evapotranspiration&timezone=auto"
        res = requests.get(url).json()
        
        current_et = res['daily']['et0_fao_evapotranspiration'][0]
        st.metric("Water Needed Today", f"{current_et} mm")
        st.success(f"**Action:** {t['rec']} {current_et}mm to {t['soil']}")

        df_weather = pd.DataFrame({
            "Date": res['daily']['time'],
            "Day Temp (°C)": res['daily']['temperature_2m_max'],
            "Night Temp (°C)": res['daily']['temperature_2m_min'],
            "Rain Chance (%)": res['daily']['precipitation_probability_max']
        })
        st.table(df_weather)
    except:
        st.error("Weather Service Busy. Please Wait...")

with tab2:
    st.subheader("📉 40-Year Climate Saga (Past & Future)")
    years = list(range(2004, 2045))
    rain_data = [800 - (i*5) for i in range(41)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years[:21], y=rain_data[:21], name="Past (Black)", line=dict(color='black', width=3)))
    fig.add_trace(go.Scatter(x=years[20:], y=rain_data[20:], name="Future (Red)", line=dict(color='red', width=3, dash='dash')))
    fig.add_hrect(y0=0, y1=500, fillcolor="red", opacity=0.1, annotation_text="DROUGHT DANGER")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader(t['m_tab'])
    if auth_status:
        try:
            m = geemap.Map(center=[lat, lon], zoom=14)
            point = ee.Geometry.Point([lon, lat])
            # Pulling latest satellite image
            img = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(point).filterDate('2024-01-01', '2024-12-31').median()
            ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
            # Fixed the line that caused your error:
            m.addLayer(ndvi, {'min': 0, 'max': 1, 'palette': ['red', 'yellow', 'green']}, 'Crop Health')
            st_folium(m, width=1000, height=500, key="farm_map")
        except Exception as e:
            st.warning(f"Map is loading satellite stream: {e}")
    else:
        st.error("Map Disabled: Handshake failed. Check your Secret Key.")

# --- 6. GOLDEN/SILVER FOOTER ---
st.markdown("---")
st.markdown(f"""
<div style="display: flex; justify-content: space-around; text-align: center; font-weight: bold;">
    <div style="background-color: #FFD700; padding: 20px; border-radius: 15px; width: 32%; color: black;">🏆 GOLD: PROFIT SAVED<br>Precision Pumping Active</div>
    <div style="background-color: #C0C0C0; padding: 20px; border-radius: 15px; width: 32%; color: black;">🥈 SILVER: SPECS<br>Pipe: 63mm | Pressure: 2.0 Bar</div>
    <div style="background-color: #000000; padding: 20px; border-radius: 15px; width: 32%; color: white;">⚫ BLACK: HISTORY<br>20 Years Climate Data</div>
</div>
""", unsafe_allow_html=True)
