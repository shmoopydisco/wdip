from pathlib import Path

import pandas as pd
import streamlit as st
from geopy.geocoders import Nominatim
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
    current_location = ""
    if user_location:
        current_location = f"{str(user_location['coords']['latitude'])}, {str(user_location['coords']['longitude'])}"
        st.write(f"Current location: {current_location}")
        f = get_location_file_path()
        f.write_text(current_location)
        st.success('Location saved!')

    return current_location


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


    geolocator = Nominatim(user_agent="wdip")
    location_name = geolocator.reverse(current_parking)

    st.title(f"I Parked In:")
    st.subheader(location_name)
    
    lat, lon = current_parking.split(",")
    df = pd.DataFrame({"lat": float(lat), "lon": float(lon)}, index=[0])
    st.map(data=df, zoom=16)

    st.button('Save current location', type='primary', on_click=get_location_and_save_to_file)
        


if __name__ == "__main__":
    main_form()
