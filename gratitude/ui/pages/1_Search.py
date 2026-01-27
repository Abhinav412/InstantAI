import streamlit as st
import requests

API = "http://127.0.0.1:8000/api/search/gratitude"

st.header("🔎 Search Gratitude")

col1, col2, col3 = st.columns(3)
location = col1.text_input("Location")
action = col2.text_input("Action (e.g. helped)")
entity_type = col3.selectbox("Entity Type", ["", "person", "team", "location"])

params = {}
if location:
    params["location"] = location
if action:
    params["action"] = action
if entity_type:
    params["entity_type"] = entity_type

if st.button("Search"):
    res = requests.get(API, params=params).json()
    for entity in res["results"]:
        st.subheader(entity["canonical_profile"].get("descriptors", ["Entity"])[0])
        st.json(entity["canonical_profile"])

        for story in entity["stories"]:
            st.markdown(
                f"- **Action:** {story['actions']} | "
                f"**Location:** {story['location']} | "
                f"**Sentiment:** {story['sentiment']}"
            )
