import os
from flask import jsonify
import requests
from random import choice

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase_headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

def supabase_get(table, params):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.get(url, headers=supabase_headers, params=params)
    if resp.status_code == 200:
        return resp.json()
    return []

def supabase_update(table, params, update_data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.patch(url, headers=supabase_headers, params=params, json=update_data)
    return resp.status_code == 200

def models_details(type, model):
    params = {
        "id": f"eq.{model}", "type": f"eq.{type}"
    }
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/Models",
        headers=supabase_headers,
        params=params
    )
    models_list = response.json()
    if not models_list or not isinstance(models_list, list):
        return jsonify({"error": "Model not found"}), 404
    models = models_list[0]
    back_provider_url = os.getenv(models.get("back_provider"))
    if type == "img":
        back_provider_url = f"{back_provider_url}/images/generations"
    elif type == "text":
        back_provider_url = f"{back_provider_url}/chat/completions"
    params = {
        "provider": f"eq.{models.get("back_provider")}",
    }
    keys = requests.get(
        f"{SUPABASE_URL}/rest/v1/apiKeys",
        headers=supabase_headers,
        params=params
    ).json()
    key = choice(keys)
    key = key.get("key")

    model_data = {
        "id": models.get("id"),
        "key": key,
        "tokens": models.get("tokens"),
        "name": models.get("name"),
        "access": models.get("access"),
        "n": models.get("n"),
        "back_id": models.get("back_id"),
        "back_provider": back_provider_url
    }
    print(f"Model Data: {model_data}")
    return model_data