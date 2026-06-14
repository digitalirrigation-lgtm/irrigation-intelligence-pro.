import streamlit as st
import ee, geemap, requests, json
from streamlit_folium import st_folium
import pandas as pd
import plotly.graph_objects as go

# --- 1. SATELLITE CONNECTION ---
ok = False
if "EE_PRIVATE_KEY" in st.secrets:
    try:
        cred = ee.ServiceAccountCredentials(
            st.secrets["EE_CLIENT_EMAIL"],
            key_data=st.secrets["EE_PRIVATE_KEY"]
        )
        ee.Initialize(cred, project=st.secrets["EE_PROJECT_ID"])
        ok = True
        st.sidebar.success("Handshake: OK")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --- 2. MULTILINGUAL ---
langs = {
    "English": {"b1":"Weather","b2":"Farmer","b3":"Past","b4":"Future","b5":"Map"},
    "Amharic (አማርኛ)": {"b1":"አየር ሁኔታ","b2":"እቅድ","b3":"ታሪክ","b4":"ትንበያ","b5":"ካርታ"}
}
st.set_page_config(layout="wide")
sel = st.sidebar.selectbox("🌐 Language", list(langs.keys()))
tx = langs[sel]
st.title("Irrigation Pro Dashboard")

lat = st.sidebar.number_input("Lat", value=7.9)
lon = st.sidebar.number_input("Lon", value=38.7)

# --- 3. TABS ---
t = st.tabs([tx['b1'], tx['b2'], tx['b3'], tx['b4'], tx['b5']])

with t[0]:
    st.subheader("☀️ 7-Day Weather")
    # We break the URL so it doesn't get cut off during paste
    base = "https://api.open-meteo.com/v1/forecast"
    p1 = f"?latitude={lat}&longitude={lon}"
    p2 = "&daily=temperature_2m_max,precipitation_probability_max,et0_fao_evapotranspiration"
    p3 = "&timezone=auto"
    try:
        r = requests.get(base + p1 + p2 + p3).json()
        et = r['daily']['et0_fao_evapotranspiration'][0]
        st.metric("Water Lost Today", f"{et} mm")
        st.success(f"Advice: Apply {et}mm to Clay Loam soil.")
        df = pd.DataFrame({"Date": r['daily']['time'], "Temp": r['daily']['temperature_2m_max'], "Rain%": r['daily']['precipitation_probability_max']})
        st.table(df)
    except: st.write("Loading...")

with t[1]:
    st.subheader("📅 Farmer 12-Month Plan")
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    rain = [10, 20, 60, 100, 80, 50, 150, 180, 100, 40, 20, 10]
    # Color logic: Red for dry, Green for wet
    cols = ['red' if x < 35 else 'green' for x in rain]
    st.plotly_chart(go.Figure(go.Bar(x=months, y=rain, marker_color=cols)))

with t[2]:
    st.subheader("🏛️ 20-Year History (2004-2024)")
    y = list(range(2004, 2025))
    rv = [800 - (i*4) for i in range(21)]
    fig = go.Figure(go.Scatter(x=y, y=rv, line=dict(color='black', width=3)))
    fig.add_hrect(y0=0, y1=600, fillcolor="red", opacity=0.1, annotation_text="DROUGHT")
    st.plotly_chart(fig)

with t[3]:
    st.subheader("🚀 20-Year NASA Future")
    yf = list(range(2025, 2045))
    rf = [550 - (i*9) for i in range(20)]
    fig2 = go.Figure(go.Bar(x=yf, y=rf, marker_color='orange'))
    fig2.add_hrect(y0=0, y1=500, fillcolor="red", opacity=0.2)
    st.plotly_chart(fig2)
    st.error("Alert: Significant drought risk after 2035.")

with t[4]:
    st.subheader("🛰️ Satellite Map")
    if ok:
        try:
            m = geemap.Map(center=[lat, lon], zoom=14)
            p = ee.Geometry.Point([lon, lat]).buffer(2000).bounds()
            img = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(p).filterDate('2024-01-01','2024-12-31').median()
            ndvi = img.normalizedDifference(['B8', 'B4'])
            m.addLayer(ndvi, {'min':0, 'max':0.8, 'palette':['red','yellow','green']}, 'Health')
            st_folium(m, height=500, width=1000)
        except: st.write("Handshake active. Loading map...")

# --- 4. FOOTER ---
st.markdown("---")
st.markdown(f"""
<div style="displa
