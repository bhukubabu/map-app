import pandas as pd
import chardet
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
import streamlit as st
from streamlit_folium import st_folium
import streamlit.components.v1 as components
from matplotlib import pyplot as plt

st.title("Check safety status on the map 🗺️")

# Load data and detect encoding
with open("final_lat.csv", "rb") as f:
    encoding = chardet.detect(f.read())["encoding"]
df = pd.read_csv("final_lat.csv", encoding=encoding)

# Get list of unique cities in West Bengal
city_list = df[df['states'] == 'West bengal']['PLACE'].unique()

# Function to create map with crime data
def create_dataframe(loca):
    lat = df[df['PLACE'] == loca]['latitude'].unique()[0]
    lng = df[df['PLACE'] == loca]['longitude'].unique()[0]
    cluster = df[df['PLACE'] == loca]['cluster'].unique()[0]
    level = df[df['PLACE'] == loca]['level'].unique()[0]
    map_center = [lat, lng]
    coords = df[['latitude', 'longitude', 'intse']]

    # Initialize map centered on the selected location
    crime_map = folium.Map(location=map_center, zoom_start=8, control_scale=True)

    # Add a marker for the center location with crime level information
    folium.Marker(
        location=map_center,
        popup=f"Crime Zone Level: {level}",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(crime_map)

    # Set up heatmap gradient
    gradient = {
        0.2: 'blue',   # low intensity
        0.4: 'cyan',   
        0.6: 'lime',   
        0.8: 'orange',
        1.0: 'red'     # high intensity
    }
    
    # Add heatmap to the map based on latitude, longitude, and intensity
    HeatMap(data=coords[['latitude', 'longitude', 'intse']].values, 
            blur=20, radius=8, gradient=gradient, blur_radius=1).add_to(crime_map)
    
    return crime_map, level

# Function to display the map in Streamlit
def user_loc(loca, crime_map):
    st.subheader('Displaying Clustered Locations on Map')
    st.markdown(f"Showing results for {loca}")
    # Use st_folium to directly display the map in the Streamlit app
    st_folium(crime_map, width=800, height=600)

# Function to display crime chart
def display_crime_chart(loca):
    location_data = df[df['PLACE'] == loca]
    crime_counts = location_data['MURDER'].value_counts()
    crime_counts2 = location_data['DOWRY DEATHS'].value_counts()

    # Plotting the bar chart
    fig, ax = plt.subplots()
    crime_counts.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title(f'Murder in {loca}')
    ax.set_xlabel('Crime Type')
    ax.set_ylabel('Count')
    st.pyplot(fig)
    
    crime_counts2.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title(f'Dowry Deaths in {loca}')
    ax.set_xlabel('Crime Type')
    ax.set_ylabel('Count')
    st.pyplot(fig)

# Add an option to select a city
city_list = [" "] + list(city_list)
option = st.selectbox("Select city", city_list)

if option and option != " ":
    crime_map, level = create_dataframe(option)
    user_loc(option, crime_map)
    
    if level == "low":
        st.success("You are in a safe zone.")
    else:
        st.warning("This is a medium crime zone.")
    
    st.markdown("If you want more information about the location, you can ask our chatbot or get the recent news about the place from our news bot. Here are a few plots for your convenience...")
    display_crime_chart(option)
else:
    st.write("Please select a location.")

