import requests
from flask import jsonify
import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase_headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

def getModels():
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/Models",
        headers=supabase_headers
    )
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch models"}), 500

    models = response.json()
    selected_fields = ['access', 'id', 'name', 'provider', 'tokens', 'type', 'n']

    filtered_models = []
    for model in models:
        if not isinstance(model, dict):
            continue

        model_data = {field: model.get(field) for field in selected_fields}

        if model_data.get('type') == 'img':
            try:
                max_images = int(model.get('n', 0))
            except (ValueError, TypeError):
                max_images = 0

            model_data['maximum_images'] = max_images
            model_data.pop('n', None)
        else:
            model_data.pop('n', None)

        filtered_models.append(model_data)

    return jsonify(filtered_models)