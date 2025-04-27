import streamlit as st
import pandas as pd
from utils import analyze_risk_nearby, get_lat_lon_from_address, call_gpt_suggestion
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Chicago Travel Safety Assistant", layout="centered")

st.title("🚨 Chicago Travel Safety Assistant")
st.markdown("Enter an address in Chicago to get safety insights based on real crime data.")

# --- Step 1: User inputs API Keys ---
with st.sidebar:
    st.header("🔐 API Configuration")
    GOOGLE_API_KEY = st.text_input("Enter your Google Maps API Key:", type="password")
    OPENAI_API_KEY = st.text_input("Enter your OpenAI GPT-4 API Key:", type="password")

if GOOGLE_API_KEY and OPENAI_API_KEY:

    # --- Step 2: User inputs Address ---
    address = st.text_input("📍 Enter Address", "233 S Wacker Dr, Chicago, IL")

    if address:
        lat, lon = get_lat_lon_from_address(address, GOOGLE_API_KEY)
        if lat and lon:
            with st.spinner("Analyzing nearby crimes and community safety..."):
                results = analyze_risk_nearby(address, lat, lon)

            if results:
                st.subheader("🗺️ Map Location")
                
                m = folium.Map(location=[lat, lon], zoom_start=15)
                folium.Marker(
                [lat, lon],
                popup="Input Address",
                icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)
                
                folium.Circle(
                location=[lat, lon],
                radius=500,
                color="blue",
                fill=True,
                fill_opacity=0.1
                ).add_to(m)

                st_folium(m, width=700, height=450)

                st.subheader("📊 Risk Summary (within 500m)")
                st.markdown(f"<h4>🔎 Total Crimes: {results['C']}</h4>", unsafe_allow_html=True)
                st.markdown(f"<h4>🔪 Violent Crime Ratio: {results['S']*100:.1f}%</h4>", unsafe_allow_html=True)
                st.markdown(f"<h4>🌙 Nighttime Crime Ratio: {results['T']*100:.1f}%</h4>", unsafe_allow_html=True)
                st.markdown(f"<h4>🚔 Arrest Rate: {results['A']*100:.1f}%</h4>", unsafe_allow_html=True)
                st.markdown(f"<h4>📍 Local CRS Score: {results['CRS']:.2f}</h4>", unsafe_allow_html=True)
                st.markdown(f"<h4>🏙️ Community CRS Score: {results['Community_CRS']:.2f}</h4>", unsafe_allow_html=True)
                st.markdown(f"<h4>🌎 Community Area: {results['Area_Name']}</h4>", unsafe_allow_html=True)

                if st.button("📋 Get Travel Advice from GPT-4"):
                     with st.spinner("Generating advice..."):
                        prompt_text = results["report_text"]
                        advice = call_gpt_suggestion(prompt_text, OPENAI_API_KEY)

                        st.subheader("✍️ GPT-4 Travel Advice")
                        st.write(advice)
        
     # --- Download the ouput ---                   
                        
                        summary_text = f"""📍 Address: {address}

                📊 Risk Summary (within 500m):
                - Total Crimes: {results['C']}
                - Violent Crime Ratio: {results['S']*100:.1f}%
                - Nighttime Crime Ratio: {results['T']*100:.1f}%
                - Arrest Rate: {results['A']*100:.1f}%
                - Local CRS Score: {results['CRS']:.2f}
                - Community CRS Score: {results['Community_CRS']:.2f}
                - Community Area: {results['Area_Name']}

                🧠 GPT-4 Travel Advice:
                {advice}
                """

        
                        st.download_button(
                            label="📥 Download Full Report",
                            data=summary_text,
                            file_name="travel_safety_report.txt",
                            mime="text/plain"
                        )

        else:
            st.error("Unable to get location from address. Please try a valid Chicago address.")
       


else:        
    st.warning("Please input both API keys to start.")



