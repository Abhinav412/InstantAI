import streamlit as st
import requests

BASE = "http://127.0.0.1:8000/api/analytics"

st.header("📊 Analytics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Entities")
    res = requests.get(f"{BASE}/top-entities").json()
    st.table(res["results"])

with col2:
    st.subheader("Top Locations")
    res = requests.get(f"{BASE}/top-locations").json()
    st.table(res["results"])

st.subheader("Top Actions")
res = requests.get(f"{BASE}/top-actions").json()
st.table(res["results"])
