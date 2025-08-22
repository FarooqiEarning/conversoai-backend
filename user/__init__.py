from supabase import supabase_get, supabase_update
from flask import jsonify
import random
import string

def check_and_get(apikey):
    users = supabase_get("User", {"apikey": f"eq.{apikey}"})
    # Filter users to ensure exact match (Supabase may return partial matches)
    users = [u for u in users if u.get("apikey") == apikey]
    if not users:
        return jsonify({"type": "text", "response": "Invalid API Key"}), 488
    user = users[0]
    id=user.get("id")
    role=user.get("Role")
    tokens = user.get("Tokens", 0)
    data = {
        "id": id,
        "role": role,
        "tokens": tokens
    }
    return data

def cut_tokens(id, role, totalTokens, usedTokens):
    if role != "Owner" and role != "Premium User":
        supabase_update("User", {"id": f"eq.{id}"}, {"Tokens": totalTokens - usedTokens})

def generate_api_key():
    def rand_str(length):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    apiKey= f"mg-{rand_str(13)}-{rand_str(10)}"
    return apiKey