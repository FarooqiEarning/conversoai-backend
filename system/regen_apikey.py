import requests
from flask import jsonify
import os
from supabase import supabase_get
from user import generate_api_key

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase_headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json"
    }
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

def regenNewApiKey(oldApiKey):
    # Setp 1: Get User id
    users= users = supabase_get("User", {"apikey": f"eq.{oldApiKey}"})
    user=[u for u in users if u.get("apikey") == oldApiKey]
    id=user[0].get("id")
    # Step 2: Generate new API key
    new_api_key = generate_api_key()

    # Step 3: Update Api_Users with new API key
    update_response = requests.patch(
        f"{SUPABASE_URL}/rest/v1/User?id=eq.{id}",
        headers=supabase_headers,
        json={"apikey": new_api_key}
    )
    if update_response.status_code != 204:
        return jsonify({"error": "Failed to update API key"}), 500
    
    url = f"https://api.clerk.com/v1/users/{id}/metadata"
    headers = {
        "Authorization": f"Bearer {CLERK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    json = {
        "public_metadata": {
            "apiKey": new_api_key
        }
    }
    res = requests.patch(url, json=json, headers=headers)
    print("Status Code:", res.status_code)
    return jsonify({
        "message": "API key regenerated successfully",
        "newApiKey": new_api_key
    })