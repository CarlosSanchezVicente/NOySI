# IMPORTS
import streamlit as st
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import sqlite3
import io

# READ VARIABLE
DRIVE_TOKEN = st.secrets["tokens"]["ID_DRIVE"]


# Autenticación con Google Drive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # Autentica e inicia un servidor web local para completar el flujo OAuth
drive = GoogleDrive(gauth)