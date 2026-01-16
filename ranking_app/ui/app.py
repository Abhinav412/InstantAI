import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/rank"

st.set_page_config(page_title="Agentic Ranking App", layout="wide")

st.title("🔍 Agentic Ranking Engine")
st.subheader("Context-aware, explainable rankings powered by agents")

query = st.text_input(
    "What do you want to rank?",
    placeholder="e.g. Rank top startup incubators in India"
)

if st.button("Run Ranking"):
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("Running agent pipeline..."):
            response = requests.post(API_URL, json={"query": query})
            try:
                result = response.json()
            except Exception:
                st.error("Backend did not return valid JSON")
                st.text("Status code: " + str(response.status_code))
                st.code(response.text)
                st.stop()
            
            if not result.get("success", False):
                st.error("Ranking failed")
                st.text(result.get("error", "Unknown error"))
                st.stop()

        rankings = result["rankings"]
        explanation = result["explanation"]

        if not rankings:
            st.warning("No rankings found.")
        else:
            st.success("Ranking completed")

            df = pd.DataFrame(rankings)
            df.insert(0, "rank", range(1, len(df) + 1))
            st.subheader("📊 Ranked Results")
            st.dataframe(df, use_container_width=True,hide_index=True)

            st.subheader("🧠 Explanation")
            st.markdown(f"**Summary:** {explanation['summary']}")

            st.markdown("**Top Drivers:**")
            for d in explanation["top_drivers"]:
                st.markdown(f"- **{d['name']}**: {d['reason']}")

            st.markdown(
                f"**Confidence Interpretation:** {explanation['confidence_interpretation']}"
            )
