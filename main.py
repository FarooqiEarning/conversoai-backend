from flask import Flask, jsonify, request, send_file
from io import BytesIO
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from api import generate_image, getModels, completeResponse, getImage, createAgent, agentResponse, getAgents, telegram_generate_image
from system import getStatus, regenNewApiKey, checkIsHaveAccessToAdminPanel
from user import get_user_tokens, handle_user_webhook

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"]
    }
}, supports_credentials=True)

# Basic routes
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to Converso AI!",
        "description": (
            "Converso AI is an intelligent conversational platform designed "
            "to provide fast, accurate, and human-like interactions. "
            "It enables businesses and individuals to automate conversations, "
            "answer questions, and create custom AI-powered experiences."
        ),
        "status": "running",
        "version": "1.0.6"
    })

### <--- Converso AI All Rounder --->
@app.route('/tokens', methods=['GET'])
def get_tokens():
    # 1. Extract Bearer token
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer', '').strip()
    if not token:
        return jsonify({"error": "Missing or invalid token"}), 401
    return get_user_tokens(token)  

@app.route('/status', methods=['GET'])
def status():
    return getStatus()

@app.route('/v1/models', methods=['GET'])
def models():
    return getModels()

@app.route('/regen-api_key', methods=['GET'])
def regen_api_key():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({'error': 'Authorization header required'}), 401
    api_key = api_key.replace('Bearer ', '').strip()
    return regenNewApiKey(api_key)

@app.route('/checkIsHaveAccessToAdminPanel')
def check():
    apiKey = request.headers.get('Authorization')
    if not apiKey:
        return jsonify({"error": "Authorization header required"}), 401
    apiKey = apiKey.replace('Bearer ', '').strip()
    return jsonify(checkIsHaveAccessToAdminPanel(apiKey))

@app.route('/user/webhook', methods=['POST'])
def user_webhook():
    print("Received webhook request")
    request_data = request.json
    return handle_user_webhook(request_data)

@app.route('/create-agent', methods=['POST'])
def create_agent():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({'error': 'Authorization header required'}), 401
    api_key = api_key.replace('Bearer ', '').strip()
    data = request.json
    agent_name = data.get("agent_name")
    agent_description = data.get("agent_description")
    if not agent_name or not agent_description:
        return jsonify({'error': 'Agent name and description are required'}), 400
    return createAgent(api_key, agent_name, agent_description)

@app.route('/get-agents', methods=['GET'])
def get_agents():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({'error': 'Authorization header required'}), 401
    api_key = api_key.replace('Bearer ', '').strip()
    return getAgents(api_key)

@app.route('/telegram/images/generations', methods=['POST'])
def telegram_image():
    apiKey = request.headers.get('Authorization')
    apiKey = apiKey.replace("Bearer ", "").strip()
    if not apiKey:
        return jsonify({"type": "text", "response": "API Key is missing"}), 488
    prompt = request.json.get("prompt", "").replace("\n", "")
    model = request.json.get("model") 
    n = request.json.get("n")
    if not prompt:
        return jsonify({"type": "text", "response": "Prompt is required"}), 400
    if not model:
        return jsonify({"type": "text", "response": "Model is required"}), 400
    if not isinstance(n, int):
        return jsonify({"type": "text", "response": "Parameter 'n' must be an integer"}), 400
    if apiKey == "mg-tg-1":
        return telegram_generate_image(prompt, model, n=n)
    else:
        return jsonify({"type": "text", "response": "Invalid API Key"}), 401

### <--- Converso AI API v1 --->
@app.route('/v1/chat/completions', methods=['POST'])
def v1_completion():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({"type": "text", "response": "API Key is missing"}), 488
    api_key = api_key.replace("Bearer ", "").strip()
    print(f"Received API Key: {api_key}")
    data = request.json
    model = data.get("model")
    if not model:
        return jsonify({"type": "text", "response": "Model is required"}), 400
    return completeResponse(api_key, data)

@app.route('/v1/images/generations', methods=['POST'])
def v1_image():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({"type": "text", "response": "API Key is missing"}), 488
    api_key = api_key.replace("Bearer ", "").strip()
    print(f"Received API Key: {api_key}")
    data = request.json
    prompt = data.get("prompt", "").replace("\n", "")
    model = data.get("model")
    n = data.get("n", 1)
    if not prompt:
        return jsonify({"type": "text", "response": "Prompt is required"}), 400
    if not model:
        return jsonify({"type": "text", "response": "Model is required"}), 400
    return generate_image(api_key, prompt, model, n)

@app.route('/v1/agents/<agent_id>/responses', methods=['POST'])
def agent_responses(agent_id):
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({"type": "text", "response": "API Key is missing"}), 488
    api_key = api_key.replace("Bearer ", "").strip()
    print(f"Received API Key: {api_key}")
    data = request.json
    prompt = data.get("prompt", "").replace("\n", "")
    if not prompt:
        return jsonify({"type": "text", "response": "Prompt is required"}), 400
    return agentResponse(api_key, agent_id, prompt)

@app.route('/generated_images/<id>')
def serve(id):
    data = getImage(id)
    return send_file(BytesIO(data), mimetype="image/jpeg")

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify({
        'error': str(e),
        'status_code': code
    }), code

app.run(host='0.0.0.0', port=8080, debug=True)
