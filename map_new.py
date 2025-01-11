import pandas as pd
import chardet
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
import streamlit as st
from streamlit_folium import folium_static,st_folium
import streamlit.components.v1 as components
from matplotlib import pyplot as plt


def load_preprocess():
    with open("final_lat.csv", "rb") as f:
        encoding = chardet.detect(f.read())["encoding"]
    df = pd.read_csv("final_lat.csv", encoding=encoding)
    df.dropna(inplace=True)
    to_drop=df[(df['latitude']== 0.0) | (df['longitude']== 0.0)].index
    df.drop(to_drop,inplace=True)
    return df


def save_heatmap(df):
    """Generate and save heatmap as an HTML file."""
    df['intse_normalized'] = df['intse'] / df['intse'].max()
    coords = [
        [row['latitude'], row['longitude'], row['intse_normalized']]
        for _, row in df.iterrows()
        if not pd.isnull(row['intse_normalized']) and row['intse_normalized'] > 0
    ]

    map_center = [df['latitude'].mean(), df['longitude'].mean()]
    crime_map = folium.Map(location=map_center, zoom_start=8, control_scale=True)

    gradient = {
        0.2: 'blue',
        0.4: 'cyan',
        0.6: 'lime',
        0.8: 'orange',
        1.0: 'red',
    }

    HeatMap(data=coords, blur=20, radius=8, gradient=gradient).add_to(crime_map)
    crime_map.save("crime_heatmap.html")
    st.success("Heatmap saved successfully!")


def load_and_display_heatmap(loca, df):
    """Load saved heatmap and add a marker for the selected location."""
    try:
        with open("crime_heatmap.html", "r", encoding="utf-8") as f:
            heatmap_html = f.read()
        
        lat = df[df['PLACE'] == loca]['latitude'].unique()[0]
        lng = df[df['PLACE'] == loca]['longitude'].unique()[0]
        level = df[df['PLACE'] == loca]['level'].unique()[0]

        folium_map = folium.Map(location=[lat, lng], zoom_start=10, control_scale=True)
        folium.Marker(
            location=[lat, lng],
            popup=f"Crime Zone Level: {level}",
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(folium_map)

        st.markdown(f"### Safety Status for {loca}")
        st.components.v1.html(heatmap_html, height=500, width=700)
    except Exception as e:
        st.error(f"Error loading heatmap: {e}")


def display_crime_charts(loca, df):
    """Display bar charts for different crime types."""
    location_data = df[df['PLACE'] == loca]

    # Plot Murder Chart
    fig1, ax1 = plt.subplots()
    location_data['MURDER'].value_counts().plot(kind="bar", ax=ax1, color="skyblue")
    ax1.set_title(f"Murder Count in {loca}")
    ax1.set_xlabel("Crime Type")
    ax1.set_ylabel("Count")
    st.pyplot(fig1)

    # Plot Dowry Deaths Chart
    fig2, ax2 = plt.subplots()
    location_data['DOWRY DEATHS'].value_counts().plot(kind="bar", ax=ax2, color="lightcoral")
    ax2.set_title(f"Dowry Deaths Count in {loca}")
    ax2.set_xlabel("Crime Type")
    ax2.set_ylabel("Count")
    st.pyplot(fig2)


if __name__ == "__main__":
    st.title("Check Safety Status on the Map 🗺️")
    df = load_preprocess()

    # Generate heatmap (run this once)
    if not st.session_state.get("heatmap_generated", False):
        save_heatmap(df)
        st.session_state["heatmap_generated"] = True

    # Dropdown for city selection
    city_list = df[df["states"] == "West bengal"]["PLACE"].unique()
    option = st.selectbox("Select City", city_list)

    if option:
        level = df[df["PLACE"] == option]["level"].unique()[0]
        load_and_display_heatmap(option, df)

        with st.chat_message("assistant"):
            if level == "low":
                st.success("You are in a safe zone. Here are some insights:")
            else:
                st.warning("This is a medium crime zone. Here are some insights:")

        display_crime_charts(option, df)
    else:
        with st.chat_message("assistant"):
            st.error("Please select a location from the dropdown.")

            
        display_crime_chart(option,df)
    else:
        with st.chat_message('assistant'):
            st.error("Please select your location from the above dropdown list")
