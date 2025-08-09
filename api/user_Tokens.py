from flask import jsonify
from ..supabase import supabase_get

def get_user_tokens(apiKey):    # 2. Query Supabase
    users = supabase_get("User", {"apikey": f"eq.{apiKey}"})
    # Filter users to ensure exact match (Supabase may return partial matches)
    users = [u for u in users if u.get("apikey") == apiKey]
    if not users:
        return jsonify({"type": "text", "response": "Invalid API Key"}), 488
    role = users[0].get("Role")
    if role != "Owner" and role != "Premium User":
        return jsonify({
            "remainingTokens": users[0].get("Tokens", 0)
        })
    else:
        return jsonify({
            "remainingTokens": "Unlimited",
            "User Role": f"{role}"
        })