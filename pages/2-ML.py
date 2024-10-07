# IMPORTS LIBRARIES
import pandas as pd
import duckdb
import streamlit as st 

# AUTHENTICATION STATUS
if not st.session_state['authentication_status']:
    st.info('Please Login from the Home page and try again.')
    st.stop()