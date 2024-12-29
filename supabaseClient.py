# import os
# from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st

# load_dotenv()

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
