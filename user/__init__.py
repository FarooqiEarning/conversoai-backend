from supabase import supabase_get, supabase_update
from flask import jsonify
from .user_Tokens import get_user_tokens
from .new_user_registory import handle_user_webhook
from .apikey import generate_api_key

def check_and_get(apikey):
    params = {
        "apikey": f"eq.{apikey}"
    }
    user_data = supabase_get("User", params)
    user_data = [u for u in user_data if u.get("apikey") == apikey]
    if not user_data:
        return {"type": "text", "response": "Invalid API Key"}, 401
    user = user_data[0]
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