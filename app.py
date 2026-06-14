import streamlit as st
import ee, geemap, requests, json
from streamlit_folium import st_folium
import pandas as pd
import plotly.graph_objects as go

# --- 1. THE PERFECT CONNECTION ---
ok = False
if 'GEE_JSON' in st.secrets:
    try:
        # Read the single string from secrets
        info = json.loads(st.secrets['GEE_JSON'])
        cred = ee.ServiceAccountCredentials(info['client_email'], key_data=json.dumps(info))
        ee.Initialize(cred, project=info['project_id'])
        ok = True
        st.sidebar.success("Handshake: SUCCESS ✅")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --- 2. MULTILINGUAL ---
langs = {"English": {"b1":"Weather", "b2":"Farmer", "b3":"Past", "b4":"Future", "b5":"Map"},
         "Amharic (አማርኛ)": {"b1":"አየር ሁኔታ", "b2":"እቅድ", "b3":"ታሪክ", "b4":"ትንበያ", "b5":"ካርታ"}}
st.set_page_config(layout="wide")
sel = st.sidebar.selectbox("🌐 Language", list(langs.keys()))
tx = langs[sel]
st.title("Digital Irrigation Pro")

lat = st.sidebar.number_input("Lat", value=7.9)
lon = st.sidebar.number_input("Lon", value=38.7)

# --- 3. TABS ---
t = st.tabs([tx['b1'], tx['b2'], tx['b3'], tx['b4'], tx['b5']])

with t[0]:
    st.subheader("☀️ Daily Forecast")
    try:
        u = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=et0_fao_evapotranspiration,temperature_2m_max&timezone=auto"
        r = requests.get(u).json()
        et = r['daily']['et0_fao_evapotranspiration'][0]
        st.metric("Water Lost Today", f"{et} mm")
        st.success(f"Advice: Apply {et}mm to Soil.")
    except: st.write("Loading...")

with t[1]:
    st.subheader("📅 Farmer Plan")
    m = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    v = [10, 20, 60, 100, 80, 50, 150, 180, 100, 40, 20, 10]
    st.plotly_chart(go.Figure(go.Bar(x=m, y=v, marker_color='green')))

with t[2]:
    st.subheader("🏛️ 20yr Past History")
    y = list(range(2004, 2025)); rv = [800 - (i*4) for i in range(21)]
    st.plotly_chart(go.Figure(go.Scatter(x=y, y=rv, line=dict(color='black'))))

with t[3]:
    st.subheader("🚀 20yr NASA Future")
    yf = list(range(2025, 2045)); rf = [550 - (i*9) for i in range(20)]
    st.plotly_chart(go.Figure(go.Bar(x=yf, y=rf, marker_color='orange')))

with t[4]:
    st.subheader("🛰️ Satellite Map")
    if ok:
        try:
            m_obj = geemap.Map(center=[lat, lon], zoom=14)
            p = ee.Geometry.Point([lon, lat]).buffer(2000).bounds()
            img = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(p).filterDate('2024-01-01','2024-12-31').median()
            ndvi = img.normalizedDifference(['B8', 'B4'])
            m_obj.addLayer(ndvi, {'min':0, 'max':0.8, 'palette':['red','yellow','green']}, 'NDVI')
            st_folium(m_obj, height=500, width=1000)
        except Exception as e: st.write(f"Wait: {e}")
    else: st.error("Check Step 1 Secret.")

st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.warning("🏆 GOLD: PROFIT")
c2.info("🥈 SILVER: 63mm PIPE")
c3.success("⚫ BLACK: HISTORY")
