from flask import jsonify
import requests
from datetime import datetime
import datetime
from supabase import models_details

# Function to generate image
def generate_image(prompt, model, n=1):
    model_info = models_details("img", model)
    model_id = model_info.get("back_id")
    provider_apikey = model_info.get("key")
    provider_url = model_info.get("back_provider")
    print(f"Using provider: {provider_url}, Model ID: {model_id}")

    payload = {
        "prompt": prompt,
        "model": model_id,
        "n": n if n else 1,
        "size": "1024x1024",
        "response_format": "url"
    }

    headers = {
        "Authorization": f"Bearer {provider_apikey}",
        "Content-Type": "application/json"
    }

    try:
        print(f"Request to {provider_url} with payload: {payload}")
        response = requests.post(url=provider_url, json=payload, headers=headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response: {response.json()}")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": "Request to image generation API failed"}, 500

    try:
        data = response.json()
        image_urls = [item.get("url") for item in data.get("data", [])]
        if not image_urls:
            print("No image URLs returned from API.")
            return {"error": "No images generated"}, 500
        print(f"Generated {len(image_urls)} image(s): {', '.join(image_urls)}")
        return image_urls if len(image_urls) > 1 else image_urls[0]
    except (KeyError, ValueError) as e:
        print(f"Error parsing API response: {e}")
        return {"error": "Invalid response from image generation API"}, 500


# Main Generate image function
def telegram_generate_image(prompt, model, n=1):
    response_data_list = []
    if n and n > 1:
        start_time = datetime.datetime.now()
        image_urls = generate_image(prompt, model, n=n)
        if not isinstance(image_urls, (list, tuple)) or len(image_urls) < n:
            return jsonify({"error": "Failed to generate enough images"}), 500
        for i in range(n):
            url = image_urls[i]
            elapsed = (datetime.datetime.now() - start_time).seconds
            response_data = {
                "type": "img",
                "url": url,
                "Prompt": prompt,
                "Creation Time": elapsed
            }
            response_data_list.append(response_data)
    else:
        start_time = datetime.datetime.now()
        image_urls = generate_image(prompt, model, n=n)
        if isinstance(image_urls, str):
            url = image_urls
        elif isinstance(image_urls, (list, tuple)) and len(image_urls) > 0:
            url = image_urls[0]
        else:
            return jsonify({"error": "Failed to generate image"}), 500
        elapsed = (datetime.datetime.now() - start_time).seconds
        response_data_list = {
            "type": "img",
            "url": url,
            "Prompt": prompt,
            "Creation Time": elapsed
        }
    print(response_data_list)
    return jsonify(response_data_list)