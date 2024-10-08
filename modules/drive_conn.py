from __future__ import print_function
import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import streamlit as st

# Cargar las credenciales
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDS = None
creds = None
# Cargar el archivo de credenciales
creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)

# Conectar con la API de Google Drive
service = build('drive', 'v3', credentials=creds)

# Listar archivos
results = service.files().list(
    pageSize=10, fields="nextPageToken, files(id, name)").execute()
items = results.get('files', [])

if not items:
    print('No files found.')
else:
    print('Files:')
    for item in items:
        print(f"{item['name']} ({item['id']})")