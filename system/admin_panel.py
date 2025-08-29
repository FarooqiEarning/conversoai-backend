from supabase import supabase_get

def checkIsHaveAccessToAdminPanel(apiKey):
    params = {
        "apikey": f"eq.{apiKey}"
    }
    user_data = supabase_get("User", params)
    user_data = [u for u in user_data if u.get("apikey") == apiKey]
    if not user_data:
        return {"error": "User not found"}
    if user_data[0].get("Role") != "Owner" and user_data[0].get("Role") != "Admin":
        return {"access": False}
    return {"access": True}