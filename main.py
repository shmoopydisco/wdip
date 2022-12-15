from pathlib import Path

import folium
import streamlit as st
from folium.plugins import Draw, MousePosition
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

CURRENT_PARKING_FILENAME = "current_parking.txt"
STREAMLIT_SHARE_WRITE_PATH = "/home/appuser"


def get_location_file_path():
    current_parking_file = Path(CURRENT_PARKING_FILENAME)

    # streamlit share allow writes here
    if Path(STREAMLIT_SHARE_WRITE_PATH).exists():
        current_parking_file = Path(STREAMLIT_SHARE_WRITE_PATH) / CURRENT_PARKING_FILENAME

    return current_parking_file


def get_location_and_save_to_file():
    user_location = get_geolocation(component_key="get_geolocation")
    current_location = "13, 37"  # default
    if user_location:
        current_location = f"{str(user_location['coords']['latitude'])}, {str(user_location['coords']['longitude'])}"
        st.write(f"Current location: {current_location}")
        f = get_location_file_path()
        f.write_text(current_location)
        st.success('Location saved!')

    return current_location

def get_marked_location_and_save_to_file(st_data):
    try:
        lon = st_data["all_drawings"][0]["geometry"]["coordinates"][0]
        lat = st_data["all_drawings"][0]["geometry"]["coordinates"][1]
        f = get_location_file_path()
        f.write_text(f"{lat}, {lon}")
        st.success('Location saved!')
    except TypeError:
        st.error("No location marked!")


def main_form():
    st.set_page_config(page_title="WDIP", page_icon="🚗")
    current_parking_file = get_location_file_path()

    try:
        current_parking = current_parking_file.read_text()
    except FileNotFoundError:
        current_parking_file.touch()
        current_parking = ""

    if not current_parking:
        current_parking = get_location_and_save_to_file()

    try:
        geolocator = Nominatim(user_agent="wdip")
        location_name = geolocator.reverse(current_parking)
    except ValueError:
        location_name = "Unknown"

    st.title(f"I Parked In:")
    st.subheader(location_name)
    st.write(current_parking)
    lat, lon = current_parking.split(",")
    
    m = folium.Map(location=[float(lat), float(lon)], zoom_start=16)
    folium.Marker(
        [float(lat), float(lon)], popup="Current Parking", tooltip="Liberty Bell"
    ).add_to(m)

    fmtr = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
    MousePosition(position='topright', separator=' | ', prefix="Mouse:", lat_formatter=fmtr, lng_formatter=fmtr).add_to(m)

    Draw(draw_options={"polyline": False, "polygon": False, "rectangle": False, "circle": False, "circlemarker": False, "MarkerOptions": {"repeatMode":False}}).add_to(m)

    # call to render Folium map in Streamlit
    st_data = st_folium(m, width=725)

    col1, col2 = st.columns(2)
    with col1:
        st.button('Save current location', type='primary', on_click=get_location_and_save_to_file)
    with col2:
        if st.button('Save marked location', type='primary'):
            try:
                lon = st_data["all_drawings"][0]["geometry"]["coordinates"][0]
                lat = st_data["all_drawings"][0]["geometry"]["coordinates"][1]
                f = get_location_file_path()
                f.write_text(f"{lat}, {lon}")
                st.success('Location saved!')
            except TypeError:
                st.error("No location marked!")
        


if __name__ == "__main__":
    main_form()
