import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="Booking Analyzer", 
    page_icon="📊"
)

# Title
st.title("📊 Booking Analyzer")

# File upload
uploaded_file = st.file_uploader("Upload Excel/CSV file", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        st.success("File loaded successfully!")
        st.dataframe(df.head())
        
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload a file")
