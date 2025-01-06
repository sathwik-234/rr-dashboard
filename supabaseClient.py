from dotenv import load_dotenv
import os
from supabase import create_client, Client
import streamlit as st


load_dotenv()
# url = os.getenv("SUPABASE_URL")
# key = os.getenv("SUPABASE_KEY")
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
