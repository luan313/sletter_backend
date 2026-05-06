import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_KEY or not SUPABASE_URL:
    raise ValueError("Variáveis de ambiente do Supabase não encontradas!")

# Usa a service_role key se disponível (bypass RLS), senão usa a anon key
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", SUPABASE_KEY)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)