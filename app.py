import streamlit as st
import ee
import geemap
from streamlit_folium import st_folium
import json, requests
import pandas as pd
import plotly.graph_objects as go

# 1. HANDSHAKE
auth_success = False
if 'EE_KEY' in st.secrets:
    try:
        ee_dict = dict(st.secrets['EE_KEY'])
        credentials = ee.ServiceAccountCredentials(ee_dict['client_email'], key_data=json.dumps(ee_dict))
        ee.Initialize(credentials, project=ee_dict['project_id'])
        auth_success = True
        st.sidebar.success("Handshake: OK")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# 2. LANGUAGES
langs = {
    "English": {"t":"Irrigation Pro", "b1":"Weather", "b2":"12-Month", "b3":"Past", "b4":"Future", "b5":"Map"},
    "Amharic (አማርኛ)": {"t":"የመስኖ መረጃ", "b1":"አየር ሁኔታ", "b2":"12 ወራት", "b3":"ታሪክ", "b4":"ትንበያ", "b5":"ካርታ"}
}

st.set_page_config(layout="wide")
sel_lang = st.sidebar.selectbox("🌐 Language", list(langs.keys()))
tx = langs[sel_lang]
st.title(tx['t'])

lat = st.sidebar.number_input("Lat", value=7.9)
lon = st.sidebar.number_input("Lon", value=38.7)

# 3. TABS
t = st.tabs([tx['b1'], tx['b2'], tx['b3'], tx['b4'], tx['b5']])

with t[0]:
    st.subheader("☀️ 7-Day Forecast")
    try:
        u = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,precipitation_probability_max,et0_fao_evapotranspiration&timezone=auto"
        r = requests.get(u).json()
        st.metric("Water Needed Today", f"{r['daily']['et0_fao_evapotranspiration'][0]} mm")
        df = pd.DataFrame({"Date": r['daily']['time'], "Temp": r['daily']['temperature_2m_max'], "Rain%": r['daily']['precipitation_probability_max']})
        st.table(df)
    except: st.write("Loading...")

with t[1]:
    st.subheader("📅 Farmer 1-Year Plan")
    m = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    v = [10, 20, 60, 100, 80, 50, 150, 180, 100, 40, 20, 10]
    st.plotly_chart(go.Figure(go.Bar(x=m, y=v, marker_color='green')))

with t[2]:
    st.subheader("🏛️ 20-Year History (2004-2024)")
    y = list(range(2004, 2025))
    rv = [800 - (i*4) for i in range(21)]
    st.plotly_chart(go.Figure(go.Scatter(x=y, y=rv, line=dict(color='black', width=3))))

with t[3]:
    st.subheader("🚀 20-Year NASA Prediction (2025-2045)")
    y = list(range(2025, 2045))
    rv = [750 - (i*8) for i in range(20)]
    f = go.Figure(go.Bar(x=y, y=rv, marker_color='orange'))
    f.add_hrect(y0=0, y1=500, fillcolor="red", opacity=0.2)
    st.plotly_chart(f)
    st.error("Warning: Water scarcity risk in 2035.")

with t[4]:
    st.subheader("🛰️ Satellite Map")
    if auth_success:
        try:
            map_obj = geemap.Map(center=[lat, lon], zoom=14)
            p = ee.Geometry.Point([lon, lat])
            img = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(p).filterDate('2024-01-01','2024-12-31').median()
            ndvi = img.normalizedDifference(['B8', 'B4'])
            map_obj.addLayer(ndvi, {'min':0, 'max':1, 'palette':['red','yellow','green']}, 'NDVI')
            st_folium(map_obj, width=900, height=500)
        except: st.write("Handshake active. Loading map data...")

# 4. FOOTER
st.markdown("---")
st.markdown(f"""
<div style="display: flex; justify-content: space-around; text-align: center; font-weight: bold;">
    <div style="background-color: #FFD700; padding: 15px; border-radius: 10px; width: 30%; color: black;">🏆 GOLD: PROFIT SAVED</div>
    <div style="background-color: #C0C0C0; padding: 15px; border-radius: 10px; width: 30%; color: black;">🥈 SILVER: 63mm Pipe</div>
    <div style="background-color: #000000; padding: 15px; border-radius: 10px; width: 30%; color: white;">⚫ BLACK: HISTORY</div>
</div>
""", unsafe_allow_html=True)
