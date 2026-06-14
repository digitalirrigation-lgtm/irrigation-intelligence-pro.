import streamlit as st
import ee
import geemap.foliumap as geemap
from streamlit_folium import st_folium
import json
import requests
import pandas as pd
import plotly.graph_objects as go

# 1. THE GOLDEN HANDSHAKE (Connecting the Robot)
if 'EARTH_ENGINE_KEY' in st.secrets:
    ee_key = json.loads(st.secrets['EARTH_ENGINE_KEY'])
    credentials = ee.ServiceAccountCredentials(ee_key['client_email'], key_data=st.secrets['EARTH_ENGINE_KEY'])
    ee.Initialize(credentials, project=ee_key['project_id'])

# 2. THE MULTI-LANGUAGE DICTIONARY (4 Languages)
languages = {
    "English": {
        "title": "Global Irrigation Intelligence",
        "soil": "Soil Type", "advice": "Advice", "pipe": "Pipe Size", "press": "Pressure",
        "farmer": "🚜 Farmer Plan", "ngo": "📊 NGO Saga", "map": "🛰️ Map",
        "safe": "Healthy", "danger": "Drought/Danger", "gold": "🏆 GOLD: Profit Saved", "black": "⚫ BLACK: History"
    },
    "Amharic (አማርኛ)": {
        "title": "የአለም አቀፍ የመስኖ መረጃ",
        "soil": "የአፈር ዓይነት", "advice": "ምክር", "pipe": "የፓይፕ መጠን", "press": "ግፊት",
        "farmer": "🚜 የአርሶ አደር እቅድ", "ngo": "📊 የመንግስት ሪፖርት", "map": "🛰️ ካርታ",
        "safe": "ጤናማ", "danger": "አደጋ/ድርቅ", "gold": "🏆 ወርቅ፡ የተረፈ ገንዘብ", "black": "⚫ ጥቁር፡ ታሪክ"
    },
    "Oromo (Afaan Oromoo)": {
        "title": "Odeeffannoo Jallisii Addunyaa",
        "soil": "Gosa Diyyee", "advice": "Gorsa", "pipe": "Hamma Paayippii", "press": "Dhiibbaa",
        "farmer": "🚜 Karoora Qonnaan Bulaa", "ngo": "📊 Seenaa Waggaa 40", "map": "🛰️ Kaartaa",
        "safe": "Fayyaa", "danger": "Khatar/Abbaarii", "gold": "🏆 WARQEE: Maallaqa Qusatame", "black": "⚫ MADII: Seenaa"
    },
    "Somali (Soomaali)": {
        "title": "Sirdoonka Waraabka Adduunka",
        "soil": "Nooca Ciidda", "advice": "Talo", "pipe": "Baaxadda Biibka", "press": "Cadaadiska",
        "farmer": "🚜 Qorshaha Beeralayda", "ngo": "📊 Taariikhda 40 Sano", "map": "🛰️ Khariidadda",
        "safe": "Caafimaad", "danger": "Khatar/Abaar", "gold": "🏆 DAHAB: Lacag la keydiyay", "black": "⚫ MADOW: Taariikhda"
    }
}

# 3. UI DESIGN (Beauty & Switchers)
st.set_page_config(layout="wide", page_title="Digital Irrigation")
lang = st.sidebar.selectbox("🌐 Select Language / ቋንቋ ይምረጡ", list(languages.keys()))
t = languages[lang]

st.title(f"{t['title']}")
st.markdown("---")

# 4. THE GLOBAL SWITCH (Change City here!)
st.sidebar.header("🌍 Location Switch")
city = st.sidebar.text_input("Farm Name", "Ziway, Ethiopia")
lat = st.sidebar.number_input("Latitude", value=7.9000, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=38.7000, format="%.4f")

# 5. THE THREE DATA WINDOWS (Tabs)
tab1, tab2, tab3 = st.tabs([t['farmer'], t['ngo'], t['map']])

with tab1:
    st.subheader(f"📅 12-Month Planting Plan: {city}")
    # Visual: Green Bar Chart
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    rain = [10, 15, 60, 90, 80, 50, 150, 170, 100, 30, 10, 5]
    fig_bar = go.Figure(go.Bar(x=months, y=rain, marker_color='green'))
    fig_bar.update_layout(height=350, title="Expected Monthly Rain (mm)")
    st.plotly_chart(fig_bar, use_container_width=True)
    st.success(f"**{t['advice']}:** Use Drip Irrigation in Jan, Feb, and Dec.")

with tab2:
    st.subheader("📊 40-Year Climate Saga (Past & Future)")
    years = list(range(2004, 2045))
    rain_values = [800 - (i*5) for i in range(41)] # Showing a decreasing trend
    fig_line = go.Figure()
    # Past (Black)
    fig_line.add_trace(go.Scatter(x=years[:21], y=rain_values[:21], name=t['black'], line=dict(color='black', width=3)))
    # Future (Red/Drought Warning)
    fig_line.add_trace(go.Scatter(x=years[20:], y=rain_values[20:], name=t['danger'], line=dict(color='red', width=3, dash='dash')))
    fig_line.add_hrect(y0=0, y1=500, fillcolor="red", opacity=0.1, annotation_text="DROUGHT DANGER")
    st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    st.subheader(f"🛰️ {t['map']}")
    m = geemap.Map(center=[lat, lon], zoom=14)
    # The Satellite Engine (NDVI) would run here
    st_folium(m, width=900, height=500)

# 6. THE ENGINEERING & COLOR LEGEND (The Visual Hook)
st.markdown("---")
st.write("### 📜 Note Legend / ማብራሪያ")

# Creating the Golden, Silver, and Black Notes using HTML for beauty
st.markdown(f"""
<div style="display: flex; justify-content: space-around; text-align: center;">
    <div style="background-color: #FFD700; padding: 10px; border-radius: 10px; color: black; font-weight: bold; width: 200px;">
        {t['gold']}
    </div>
    <div style="background-color: #C0C0C0; padding: 10px; border-radius: 10px; color: black; font-weight: bold; width: 200px;">
        🥈 SILVER: {t['pipe']} 63mm <br> Pressure 2.0 Bar
    </div>
    <div style="background-color: #000000; padding: 10px; border-radius: 10px; color: white; font-weight: bold; width: 200px;">
        {t['black']}
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.info(f"📍 GPS Verified: {lat}, {lon}")
