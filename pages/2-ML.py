# IMPORTS LIBRARIES
import pandas as pd
import duckdb
import streamlit as st

from config import LOGO_PATH

# CONFIGURATION PAGE (set_page_config debe ser el primer comando de Streamlit)
st.set_page_config(
        page_title='Machine Learning',
        page_icon='🧠'
    )

# AUTHENTICATION STATUS
st.logo(str(LOGO_PATH), size="medium")
if not st.session_state.get('authentication_status', False):
    st.info('Please Login from the Home page and try again.')
    st.stop()

# CONFIGURATION PAGE
#st.title('Data analysis and plot the experiment')
#st.sidebar.success('Select the parameters:')
st.sidebar.markdown("### Select the parameters:")
