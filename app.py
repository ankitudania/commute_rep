import streamlit as st
import pandas as pd
import io
import googlemaps
from datetime import datetime
import os

# API_KEY = os.environ['GCPKEY']
# gmaps = googlemaps.Client(key=API_KEY)
gcpkey = ""
# GCPKEY

def calculate_distance_duration(destination, address, modeoftravel):
    
    now = datetime.now()
    gmaps = googlemaps.Client(key=gcpkey)
    #Converting the source and destination to geocodes
    sourcegeo = gmaps.geocode(address)
    destgeo = gmaps.geocode(destination)
    #Here valid values for modes are -> Valid values are "driving", "walking", "transit" or "bicycling"
    result = gmaps.distance_matrix(origins=address,
                                   destinations=destination,
                                   mode=modeoftravel.lower(),
                                   departure_time=now)

    if result['rows'][0]['elements'][0]['status'] == 'OK':
        distance = result['rows'][0]['elements'][0]['distance']['text']
        duration = result['rows'][0]['elements'][0]['duration']['text']
        return distance, duration
    else:
        return None, None


def process_file(file, destination, mode):
    try:
        if file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        elif file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            st.error("Invalid file format. Please upload an Excel or CSV file.")
            return None

        if "Address" not in df.columns:
            st.error("Invalid file. The file must contain an 'Address' column.")
            return None

        df["Distance"] = df["Address"].apply(
            lambda x: calculate_distance_duration(destination, x, mode)[0]
        )
        df["Duration"] = df["Address"].apply(
            lambda x: calculate_distance_duration(destination, x, mode)[1]
        )
        
        return df
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
        return None


st.title("Distance Commute App")
gmapsAPI = st.text_input("GoogleMapsAPI")
destination = st.text_input("Destination")
modeoftravel = st.selectbox("Mode of travel", 
                      ('Driving', 'Walking', 'Transit', 'Bicycling'))
uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "csv"])

if st.button("Process File"):
    if not destination:
        st.warning("Please enter a destination.")
    elif not modeoftravel:
        st.warning("Please select a mode of travel")
    elif uploaded_file is None:
        st.warning("Please upload a file.")
    else:
        gcpkey = gmapsAPI
        result_df = process_file(uploaded_file, destination, modeoftravel)
        if result_df is not None:
            st.success("File processed successfully!")
            st.dataframe(result_df)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                result_df.to_excel(writer, index=False)
            processed_file = output.getvalue()
            st.download_button(
                label="Download processed file",
                data=processed_file,
                file_name="processed_file.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )