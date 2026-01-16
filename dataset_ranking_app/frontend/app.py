import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(layout="wide")
st.title("Universal Dataset Ranking Engine")

uploaded = st.file_uploader("Upload CSV", type=["csv"])

if uploaded:
    file_bytes = uploaded.getvalue()

    df = pd.read_csv(
        io.BytesIO(file_bytes),
        encoding_errors="ignore"
    )

    st.subheader("Dataset Preview")
    st.dataframe(df.head(50), use_container_width=True)

    query = st.text_input(
        "Ranking query",
        placeholder="Rank patient id based on length of stay"
    )

    if st.button("Run Ranking"):
        response = requests.post(
            "http://localhost:8000/rank",
            params={"query": query},
            files={
                "file": (
                    uploaded.name,
                    file_bytes,
                    "text/csv"
                )
            }
        )

        if response.status_code != 200:
            st.error(response.text)
            st.stop()

        result = response.json()
        rankings = result.get("rankings", [])
        entity_col = result.get("entity_column")

        if not rankings:
            st.error("Backend returned no rankings")
            st.stop()

        table = pd.DataFrame([
            {
                "Rank": i + 1,
                entity_col: r[entity_col],
                "Score": round(r["score"], 4)
            }
            for i, r in enumerate(rankings)
        ])

        st.subheader("Ranked Results")
        st.dataframe(table, use_container_width=True)
