import json
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

CURRENT_PARKING_FILENAME = "current_parking.txt"
PATHS_JSON_FILENAME = "paths.json"
LAT, LON = st.secrets['lat'], st.secrets['lon']


def get_map_deck(street_to_highlight):
    paths_json = json.loads(Path(PATHS_JSON_FILENAME).read_text())
    paths_json = [
        street for street in paths_json if street["name"] == street_to_highlight
    ]
    df = pd.DataFrame(paths_json)

    view_state = pdk.ViewState(latitude=LAT, longitude=LON, zoom=17)
    layer = pdk.Layer(
        type="PathLayer",
        data=df,
        pickable=True,
        get_color="color",
        width_scale=2,
        width_min_pixels=2,
        get_path="path",
        get_width=2,
    )

    deck = pdk.Deck(
        layers=[layer],
        map_style="mapbox://styles/mapbox/streets-v11",
        initial_view_state=view_state,
        tooltip={"text": "{name}"},
    )

    return deck


def main_form():
    st.set_page_config(page_title="WDIP", page_icon="🚗")
    current_parking_file = Path(CURRENT_PARKING_FILENAME)
    try:
        current_parking = current_parking_file.read_text()
    except FileNotFoundError:
        current_parking_file.touch()
        current_parking = ""

    page_title = st.empty()
    map = st.empty()

    parking_options = [
        street["name"]
        for street in iter(json.loads(Path(PATHS_JSON_FILENAME).read_text()))
    ]
    with st.form("Form1"):
        select_result = st.selectbox("Change To", parking_options)
        submitted = st.form_submit_button("Submit")
        if submitted:
            current_parking = select_result
            current_parking_file.write_text(current_parking)

    page_title.title(f"I Parked In: {current_parking}")
    map.pydeck_chart(get_map_deck(current_parking))


if __name__ == "__main__":
    main_form()
