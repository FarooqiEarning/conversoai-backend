from supabase import supabase_insert

def save_generated_image(prompt, user_id, creation_time, model_id, images):
    table = "generated_images"

    # Base fields
    raw_data = {
        "prompt": prompt,
        "user_id": user_id,
        "creation_time": creation_time,
        "model": model_id
    }

    # Add images dynamically
    for i, img in enumerate(images, start=1):
        raw_data[f"image{i}"] = img

    resp = supabase_insert(table, raw_data)
    print(f"Image saved to database: {resp}")
    return resp