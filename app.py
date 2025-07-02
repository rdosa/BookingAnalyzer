import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Booking Analyzer", page_icon="📊")
st.title("📊 Booking Analyzer")

uploaded_file = st.file_uploader("Upload booking data", type=['xlsx', 'csv'])

if uploaded_file:
    # File reading
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    st.success("✅ File loaded successfully!")
    
    # Basic info
    st.subheader("📋 Data Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Rows", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("File Size", f"{uploaded_file.size} bytes")
    
    # Show data
    st.subheader("📊 Data Preview")
    st.dataframe(df.head())
    
    # Column analysis
    st.subheader("🔍 Column Analysis")
    st.write("**Available columns:**")
    for col in df.columns:
        st.write(f"- {col}")
        
else:
    st.info("📤 Please upload a CSV or Excel file to start analysis")
