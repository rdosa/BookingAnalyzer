import streamlit as st
import pandas as pd

st.title("📊 ACV/TCV Booking Analyzer")
st.write("Magyar Telekom - Cisco CX CSM Team")

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Data preview:")
    st.dataframe(df)
