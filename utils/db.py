import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def get_supabase():
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
