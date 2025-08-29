from flask import jsonify
import requests
from .apikey import generate_api_key
import os
from supabase import supabase_get, supabase_insert
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

def handle_user_webhook(data):
    try:
        user_data = data.get("data", {})

        user_id = user_data.get("id")
        username = user_data.get("username")
        first_name = user_data.get("first_name")
        last_name = user_data.get("last_name")
        full_name = f"{first_name} {last_name}".strip()

        # Extract primary email
        primary_email_id = user_data.get("primary_email_address_id")
        email = None
        for item in user_data.get("email_addresses", []):
            if item.get("id") == primary_email_id:
                email = item.get("email_address")
                break

        # Fallback: get first email if primary not matched
        if not email and user_data.get("email_addresses"):
            email = user_data["email_addresses"][0].get("email_address")

        print("User Webhook Received:")
        print(f"- ID: {user_id}")
        print(f"- Name: {full_name}")
        print(f"- Email: {email}")

        # Check if API key exists
        api_key_data = supabase_get("User", {"id": f"eq.{user_id}"})
        if api_key_data:
            api_key = api_key_data[0]["apikey"]
        else:
            api_key = generate_api_key()
            supabase_insert("User", {
                "id": user_id,
                "apikey": api_key,
                "email": email
            })
        
        url = f"https://api.clerk.com/v1/users/{user_id}/metadata"
        headers = {
            "Authorization": f"Bearer {CLERK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        json = {
            "public_metadata": {
                "apiKey": api_key
            }
        }
        res = requests.patch(url, json=json, headers=headers)
        print("Status Code:", res.status_code)

        return jsonify({
            "status": "success",
            "user": {
                "id": user_id,
                "username": username,
                "full_name": full_name,
                "email": email
            }
        }), 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

