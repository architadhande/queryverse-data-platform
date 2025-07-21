import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://localhost:8000"

st.title("QueryVerse Basic")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if uploaded_file is not None:
    files = {"file": uploaded_file}
    res = requests.post(f"{API_URL}/upload_csv/", files=files).json()
    st.write(f"Columns: {res.get('columns')}")
    st.write(f"Rows: {res.get('rows')}")

    sql = st.text_area("Enter SQL Query", "SELECT * FROM data LIMIT 10")
    if st.button("Run Query"):
        query_res = requests.get(f"{API_URL}/query/", params={"sql": sql}).json()
        if "error" in query_res:
            st.error(query_res["error"])
        else:
            df = pd.DataFrame(query_res["rows"])
            st.dataframe(df)
            if not df.empty:
                fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                st.plotly_chart(fig)
