import streamlit as st
import requests

API = "http://127.0.0.1:8000/api/entity-resolution/states"
REVIEW = "http://127.0.0.1:8000/api/review/submit"

st.header("🧠 Review Queue")

states = requests.get(API).json().get("results", [])

if not states:
    st.success("No entities require review.")
else:
    for s in states:
        st.subheader(f"Entity {s['entity_id']}")
        st.json(s["signals"])

        col1, col2 = st.columns(2)
        if col1.button("Confirm Entity", key=f"confirm-{s['entity_id']}"):
            requests.post(REVIEW, json={
                "entity_id": s["entity_id"],
                "action": "confirm_entity"
            })
            st.success("Confirmed")

        if col2.button("Approve Split", key=f"split-{s['entity_id']}"):
            requests.post(REVIEW, json={
                "entity_id": s["entity_id"],
                "action": "approve_split"
            })
            st.warning("Marked for split")
