import pandas as pd
#from sklearn.preprocessing import StandardScaler
import chardet
import folium
from folium.plugins import HeatMap
import streamlit as st
from streamlit_folium import st_folium
import streamlit.components.v1 as components
import matplotlib.pyplot as plt

# Detect file encoding and load data
with open("final_lat.csv", "rb") as f:
    encoding = chardet.detect(f.read())["encoding"]
df = pd.read_csv("final_lat.csv", encoding=encoding)

# Get unique places in West Bengal
city_list = df[df['states'] == 'West bengal']['PLACE'].unique()

def create_dataframe(loca):
    """Create a crime heatmap centered on the specified location."""
    # Retrieve latitude, longitude, cluster, and level for the specified location
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

    # Define a color gradient for the heatmap
    gradient = {
        0.2: 'blue',   # low intensity
        0.4: 'cyan',   
        0.6: 'lime',   
        0.8: 'orange',
        1.0: 'red'     # high intensity
    }

    # Add heatmap to the map with the specified gradient
    HeatMap(
        data=coords[['latitude', 'longitude', 'intse']].values, 
        blur=20, 
        radius=8, 
        gradient=gradient
    ).add_to(crime_map)

    return crime_map

def display_crime_chart(loca):
    """Display a bar chart of crime types for the selected location."""
    # Filter data for the selected location
    location_data = df[df['PLACE'] == loca]

    # Group by crime type and count occurrences
    crime_counts = location_data['crime_type'].value_counts()

    # Plotting the bar chart
    fig, ax = plt.subplots()
    crime_counts.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title(f'Crime Types in {loca}')
    ax.set_xlabel('Crime Type')
    ax.set_ylabel('Count')
    st.pyplot(fig)

def user_loc(loca, map_html):
    """Display the map in Streamlit."""
    st.subheader('Displaying Clustered Locations on Map')
    st.markdown(f"Showing results for {loca}")
    components.html(map_html, height=600, width=800)

# Streamlit dropdown for city selection
city_list = [" "] + list(city_list)  # Add a blank option at the beginning
option = st.selectbox("Select city", city_list)

if option and option != " ":
    # Generate and display the crime map
    crime_map = create_dataframe(option)
    crime_map.save("crime_map.html")
    with open("crime_map.html", "r") as f:
        map_html = f.read()
    user_loc(option, map_html)

    # Display bar chart of crime types
    st.subheader('Crime Type Distribution')
    #display_crime_chart(option)
else:
    st.write("Please select a location.")

print("Map has been saved as crime_clusters_map.html")
