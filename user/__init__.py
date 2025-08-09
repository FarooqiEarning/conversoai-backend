from ..supabase import supabase_get, supabase_update
from flask import jsonify

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