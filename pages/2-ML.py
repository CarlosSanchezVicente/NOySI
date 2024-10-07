# IMPORTS LIBRARIES
import pandas as pd
import duckdb
import streamlit as st 

# AUTHENTICATION STATUS
st.logo('./img/NoySI.png', size="medium")
if not st.session_state['authentication_status']:
    st.info('Please Login from the Home page and try again.')
    st.stop()

# CONFIGURATION PAGE
#st.title('Data analysis and plot the experiment')
st.set_page_config(
        page_title='Machine Learning',
        page_icon='🧠'
    )
#st.sidebar.success('Select the parameters:')
st.sidebar.markdown("### Select the parameters:")