import streamlit as st

st.title("Authentication")

if st.button("Authenticate"):
    st.login("google")
