import requests
from threading import Thread
from flask import jsonify
from ..supabase import models_details
from ..user import check_and_get, cut_tokens

def completeResponse(api_key, data):
    user_data = check_and_get(api_key)
    id = user_data.get("id")
    role = user_data.get("role")
    tokens = user_data.get("tokens", 0)

    model=data.get("model")
    model_data = models_details(model)
    token_cost = model_data.get("tokens", 0)
    model_i = model_data.get("back_id")
    model_type = model_data.get("access")
    url = model_data.get("back_provider")
    key = model_data.get("key")

    header ={"Authorization": f"Bearer {key}"}
    data['model']=model_i 

    completion = requests.post(url, headers=header, json=data)
    completion_dict = completion.json()
    if 'id' in completion_dict and isinstance(completion_dict['id'], str):
        completion_dict['id'] = completion_dict['id'].replace('ddc-a4f', 'mg')
    completion_dict.pop('usage', None)
    completion_dict['model_type'] = model_type
    completion_dict['model'] = model

    Thread(target=cut_tokens, args=(id, role, tokens, token_cost)).start()

    return  jsonify(completion_dict)