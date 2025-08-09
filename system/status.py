import requests
import os
from flask import jsonify

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase_headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json"
    }

def getStatus():
    # Fetch the latest row from Data table (order by created_at desc, limit 1)
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/Data?id=eq.1",
        headers=supabase_headers,
    )
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch status"}), 500
    data = response.json()
    if not data or not isinstance(data, list) or not data[0]:
        return jsonify({"error": "No status data found"}), 404
    row = data[0]
    # Convert status to number if possible
    status_value = row.get('status')
    try:
        status_value = int(status_value)
    except (TypeError, ValueError):
        status_value = None
    return jsonify({
        'status': status_value,
        'message': row.get('message'),
        'version': row.get('version'),
        'documentation': row.get('documentation'),
        'Owner': row.get('Owner'),
        'Contact': row.get('Contact'),
        'Down_Models': row.get('Down_Models')
    })