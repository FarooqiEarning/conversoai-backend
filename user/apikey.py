import random
import string

def generate_api_key():
    def rand_str(length):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    apiKey= f"mg-{rand_str(13)}-{rand_str(10)}"
    return apiKey