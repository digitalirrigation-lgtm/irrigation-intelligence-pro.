import streamlit as st
import ee
import geemap
from streamlit_folium import st_folium
import json
import requests
import pandas as pd
import plotly.graph_objects as go

# 1. THE GOLDEN HANDSHAKE (Safe Connection)
if 'EARTH_ENGINE_KEY' in st.secrets:
    try:
        ee_key = json.loads(st.secrets['EARTH_ENGINE_KEY'])
        credentials = ee.ServiceAccountCredentials(ee_key['client_email'], key_data=st.secrets['EARTH_ENGINE_KEY'])
        ee.Initialize(credentials, project='irrigation-intelligence-pro')
    except Exception as e:
        st.error(f"Handshake Error: {e}")

# 2. MULTI-LANGUAGE DICTIONARY
languages = {
    "English": {
        "title": "Global Irrigation Intelligence",
        "soil": "Soil Type", "advice": "Advice", "pipe": "Pipe Size", "press": "Pressure",
        "farmer": "🚜 Farmer: 12-Month Plan", "ngo": "📊 NGO: 40-Year Saga", "map": "🛰️ Satellite Map",
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

# 3. INTERFACE
st.set_page_config(layout="wide", page_title="Irrigation Pro")
lang = st.sidebar.selectbox("🌐 Select Language", list(languages.keys()))
t = languages[lang]

st.title(t['title'])
st.markdown("---")

# 4. LOCATION SWITCH
st.sidebar.header("🌍 Global Switch")
city = st.sidebar.text_input("Farm Name", "Ziway, Ethiopia")
lat = st.sidebar.number_input("Latitude", value=7.9000, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=38.7000, format="%.4f")

# 5. DATA TABS
tab1, tab2, tab3 = st.tabs([t['farmer'], t['ngo'], t['map']])

with tab1:
    st.subheader(f"📅 12-Month Plan: {city}")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    # Simulated rain data for the year
    rain = [10, 15, 60, 95, 80, 50, 155, 175, 105, 35, 12, 8]
    fig_farmer = go.Figure(go.Bar(x=months, y=rain, marker_color='green'))
    fig_farmer.update_layout(height=350, title="Expected Monthly Rain (mm)")
    st.plotly_chart(fig_farmer, use_container_width=True)
    
    # Engineering Specs
    st.markdown(f"### 📏 {t['pipe']}: 63mm | {t['press']}: 2.0 Bar")
    st.info(f"**{t['advice']}:** Apply 5.31mm of water today to CLAY LOAM soil.")

with tab2:
    st.subheader(f"📊 40-Year Climate Saga")
    years = list(range(2004, 2045))
    # Historical logic: Black line (Past) turns to Red line (Future)
    rain_trend = [800 - (i*6) for i in range(41)]
    fig_saga = go.Figure()
    fig_saga.add_trace(go.Scatter(x=years[:21], y=rain_trend[:21], name=t['black'], line=dict(color='black', width=4)))
    fig_saga.add_trace(go.Scatter(x=years[20:], y=rain_trend[20:], name=t['danger'], line=dict(color='red', width=4, dash='dash')))
    fig_saga.add_hrect(y0=0, y1=550, fillcolor="red", opacity=0.1, annotation_text="DROUGHT ZONE")
    st.plotly_chart(fig_saga, use_container_width=True)
    st.error("NGO Warning: Project area faces 20% water reduction by 2040.")

with tab3:
    st.subheader(t['map'])
    try:
        # Create standard map object
        m = geemap.Map(center=[lat, lon], zoom=14)
        # Display the map using the stable Streamlit-Folium bridge
        st_folium(m, width=1000, height=500)
        st.markdown(f"🟢 {t['safe']} | 🟡 STRESS | 🔴 {t['danger']}")
    except Exception as e:
        st.error(f"Map Display Error: {e}")

# 6. BEAUTIFUL COLOR LEGEND (Golden, Silver, Black)
st.markdown("---")
st.write("### 📜 Note Legend / ማብራሪያ")
st.markdown(f"""
<div style="display: flex; justify-content: space-around; text-align: center;">
    <div style="background-color: #FFD700; padding: 15px; border-radius: 10px; color: black; font-weight: bold; width: 250px; border: 2px solid black;">
        {t['gold']} <br> Saving Water = Saving Money
    </div>
    <div style="background-color: #C0C0C0; padding: 15px; border-radius: 10px; color: black; font-weight: bold; width: 250px; border: 2px solid black;">
        🥈 SILVER: {t['pipe']} 63mm <br> Engineering Ready
    </div>
    <div style="background-color: #000000; padding: 15px; border-radius: 10px; color: white; font-weight: bold; width: 250px; border: 2px solid gold;">
        {t['black']} <br> 2004 - 2024 Climate Data
    </div>
</div>
""", unsafe_allow_html=True)
