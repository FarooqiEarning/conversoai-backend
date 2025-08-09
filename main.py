from flask import Flask, jsonify, request, redirect
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from api import get_user_tokens, generate_image, getModels, completeResponse, getImage

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"]
    }
}, supports_credentials=True)

# Basic routes
@app.route('/')
def home():
    return redirect('https://conversoai.stylefort.store/docs')

### <--- Converso AI All Rounder --->
@app.route('/tokens', methods=['GET'])
def get_tokens():
    # 1. Extract Bearer token
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer', '').strip()
    if not token:
        return jsonify({"error": "Missing or invalid token"}), 401
    return get_user_tokens(token)  

@app.route('/v1/models', methods=['GET'])
def models():
    return getModels() 

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

@app.route('/generated_images/<path:id>')
def serve(id):
    return getImage(id)

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
