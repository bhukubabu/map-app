import pandas as pd
import chardet
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
import streamlit as st
from streamlit_folium import folium_static,st_folium
import streamlit.components.v1 as components
from matplotlib import pyplot as plt



def create_dataframe(loca):
        
    lat = df[df['PLACE'] == loca]['latitude'].unique()[0]
    lng = df[df['PLACE'] == loca]['longitude'].unique()[0]
    cluster = df[df['PLACE'] == loca]['cluster'].unique()[0]
    level = df[df['PLACE'] == loca]['level'].unique()[0]
    map_center = [lat, lng]
    coords=list(map(list,zip(df['latitude'], df['longitude'],df['intse'])))
    # Initialize map centered on the selected location
    crime_map = folium.Map(location=map_center, zoom_start=8, control_scale=True)
    # Add a marker for the center location with crime level information
    folium.Marker(
        location=map_center,
        popup=f"Crime Zone Level: {level}",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(crime_map)
    gradient = {
        0.2: 'blue',   # low intensity
        0.4: 'cyan',   
        0.6: 'lime',   
        0.8: 'orange',
        1.0: 'red'     # high intensity
    }
    # heatmap to the map based on latitude, longitude, and intensity
    #HeatMap(data=coords, blur=20, radius=8,gradient=gradient,blurr=1).add_to(crime_map)
    #crime_map.save("crime_map.html")
    map_html=crime_map._repr_html_()
    try:    
            """Display the map in Streamlit."""
            with st.container(height=400):
                st.markdown(f"Showing results for {loca}")
                #d=st_folium(crime_map,width=650)
                components.html(map_html, height=350, width=550)
            
    except Exception as e:
            st.error(f"{e}")

def user_loc(loca, map_html):
    """Display the map in Streamlit."""
    with st.expander(f"Showing results for {loca}",expanded=True):
        components.html(map_html, height=600, width=550)

def display_crime_chart(loca):
    """Display a bar chart of crime types for the selected location."""
    location_data = df[df['PLACE'] == loca]

    # Group by crime type and count occurrences
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
    ax.set_title(f'DOWRY DEATHS in {loca}')
    ax.set_xlabel('Crime Type')
    ax.set_ylabel('Count')
    st.pyplot(fig)



st.title("Check safety status on the map 🗺️")
with open("final_lat.csv", "rb") as f:
    encoding = chardet.detect(f.read())["encoding"]
df = pd.read_csv("final_lat.csv", encoding=encoding)
df.dropna(inplace=True)
city_list = df[df['states'] == 'West bengal']['PLACE'].unique()

city_list_ = list(city_list)
option = st.selectbox("Select city", city_list_,index=None)

if option and option.index != None:
    create_dataframe(option)
    #user_loc(option, crime_map)
    level = df[df['PLACE'] == option]['level'].unique()[0]
    if level=="low":
        st.success("You are in safe zone")
    else:
        st.warning("Its a medium crime zone")
    st.markdown("If you want more information about the location you can ask our chat bot or get the recent news about the place from our news bot. Hre are few plots for your convinence....")
    display_crime_chart(option)
else:
    st.write("Please select a location.")

print("Map has been saved as crime_clusters_map.html")
