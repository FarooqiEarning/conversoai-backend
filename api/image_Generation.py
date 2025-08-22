from flask import jsonify
import requests
import random
import time
import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from supabase import models_details
from user import check_and_get, cut_tokens
from db.info import save_generated_image
from threading import Thread
from vercel_blob import put

def generate_image_back(prompt, model, n, provider_url, provider_apikey):
    payload = {
        "prompt": prompt,
        "model": model,
        "n": n,
        "size": "1024x1024",
        "response_format": "url"
    }
    headers = {
        "Authorization": f"Bearer {provider_apikey}",
        "Content-Type": "application/json"
    }
    response = requests.post(provider_url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        image_urls = [item.get('url') for item in data.get('data', [])]
        print("Images generated successfully")
        for url in image_urls:
            print(f" - {url}")
        return image_urls

# Main Generate image function
def generate_image(api_key ,prompt, model, IN_num=1):
    model_data = models_details("img", model)
    token_cost = model_data.get("tokens", 0)
    back_id = model_data.get("back_id")
    provider_apikey = model_data.get("key")
    provider_url = model_data.get("back_provider")
    access = model_data.get("access")
    n = model_data.get("n")
    model_name = model_data.get("name")

    if n < IN_num:
        return jsonify({"type": "text", "response": f"{model_name} can generate up to {n} images per request."}), 400
    
    upload_urls = []
    images = []
    # Verify API key
    user_data = check_and_get(api_key)
    id = user_data.get("id")
    role = user_data.get("role")
    tokens = user_data.get("tokens", 0)

    start_time = datetime.datetime.now()
    request_time = int(time.time())
    image_url = generate_image_back(prompt, back_id, IN_num, provider_url, provider_apikey)

    # Parallelized per image processing (download, watermark, upload)
    from concurrent.futures import ThreadPoolExecutor

    def process_image(img_url):
        # Download image data before watermarking or uploading
        try:
            image_data = requests.get(img_url).content

            # Check is model free
            processed_data = image_data
            if access == 'free':
                img = Image.open(BytesIO(image_data)).convert("RGBA")
                watermark = Image.new("RGBA", img.size, (255,255,255,0))
                draw = ImageDraw.Draw(watermark)

                # Set font (optional: adjust path to your font or use default)
                try:
                    font = ImageFont.truetype("arial.ttf", 36)
                except:
                    font = ImageFont.load_default()

                # Calculate text size and position
                text = "Converso AI"
                x = 20
                y = 20

                # Draw watermark text
                draw.text((x, y), text, font=font, fill=(255, 255, 255, 200))

                # Merge watermark with image
                watermarked = Image.alpha_composite(img, watermark)

                # Save to bytes
                buffer = BytesIO()
                watermarked.convert("RGB").save(buffer, format="JPEG")
                buffer.seek(0)
                processed_data = buffer.read()

            # Create a unique filename for each image
            random_num1 = random.randint(10**6, 10**7 - 1)
            random_num2 = random.randint(10**6, 10**7 - 1)
            filename = f"{request_time}{random_num1}{random_num2}"
            
            # Upload to Vercel Blob
            put(filename, processed_data, {"access": "public", "contentType": "image/jpeg"})
            blob_url = f"https://api.stylefort.store/generated_images/{filename}"
            images.append(blob_url)
            return {"url": blob_url}
        except Exception as e:
            print(f"Error processing image: {e}")
            return {"error": str(e)}

    # Use ThreadPoolExecutor to process images in parallel
    with ThreadPoolExecutor(max_workers=min(8, IN_num)) as executor:
        upload_urls = list(executor.map(process_image, image_url))

    # Update tokens
    if role != "Owner" and role != "Premium User":
        Thread(target=cut_tokens, args=(id, role, tokens, token_cost)).start()

        elapsed = (datetime.datetime.now() - start_time).seconds

        response_data = {
            "type": "img",
            "Remaining Tokens": tokens - token_cost,
            "Prompt": prompt,
            "data": upload_urls,
            "Creation Time": elapsed
        }
    else:
        elapsed = (datetime.datetime.now() - start_time).seconds

        response_data = {
            "type": "img",
            "Prompt": prompt,
            "data": upload_urls,
            "Creation Time": elapsed
        }
    print(response_data)
    Thread(target=save_generated_image, args=(prompt, id, elapsed, model, images)).start()
    return jsonify(response_data)

def getImage(id):
    url=f"https://9f7onqvz26sb8xlk.public.blob.vercel-storage.com/{id}"
    data = requests.get(url).content
    return data