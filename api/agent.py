import requests
from threading import Thread
from flask import jsonify
from supabase import providerApiKey, supabase_insert, supabase_update, supabase_get
import os
from user import check_and_get, cut_tokens

def createAgent(api_key, agent_name, agent_description):
    user_data = check_and_get(api_key)
    table = "Agents"
    insert_data = {
        "user_id": user_data.get("id"),
        "agent_name": agent_name,
        "agent_description": agent_description,
        "agent_messages": [
    {
        "role": "system",
        "content": (
            f"You are an AI agent **{agent_name}**. "
            f"{agent_description}. "
            "You are Trained & Hosted by Converso AI in Pakistan. "
            "Converso AI Website: https://conversoai.stylefort.store"
        )
    }
]
    }
    add = supabase_insert(table, insert_data)
    agent_id = add[0].get("id")
    return jsonify({"status": "Agent created successfully", "agent_id": agent_id}), 200

def getAgents(api_key):
    user_data = check_and_get(api_key)
    user_id = user_data.get("id")
    agents = supabase_get("Agents", {"user_id": f"eq.{user_id}"})
    if not isinstance(agents, list):
        agents = []
    for agent in agents:
        agent.pop("agent_messages", None)
        agent.pop("user_id", None)
    return jsonify({"agents": agents}), 200

def agentResponse(api_key, agent_id, prompt):
    """
    Handle user interaction with an AI agent:
    - Verify API key and agent ownership
    - Append user message and request completion from provider
    - Save updated conversation and deduct tokens in background
    - Return AI response as JSON
    """

    # --- Authenticate user ---
    user_data = check_and_get(api_key)
    user_id, role, tokens = (
        user_data.get("id"),
        user_data.get("role"),
        user_data.get("tokens", 0)
    )

    # --- Fetch and validate agent ---
    agent_list = supabase_get("Agents", {"id": f"eq.{agent_id}"})
    if not isinstance(agent_list, list) or not agent_list:
        return jsonify({"error": "Agent not found"}), 404

    agent_data = agent_list[0]
    if agent_data.get("user_id") != user_id:
        return jsonify({"error": "You do not own this agent"}), 404

    # --- Build conversation history ---
    messages = agent_data.get("agent_messages", [])
    messages.append({"role": "user", "content": prompt})
    if len(messages) > 11:  # keep system + last 10
        messages = [messages[0]] + messages[-10:]

    payload = {"model": "provider-3/gpt-4", "messages": messages}

    # --- Call provider API ---
    provider = "a4f"
    url = f"{os.getenv(provider)}/chat/completions"
    headers = {"Authorization": f"Bearer {providerApiKey(provider)}"}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        response = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": "Provider request failed"}), 502
    except ValueError:
        return jsonify({"error": "Invalid JSON response from provider"}), 502

    # --- Normalize response ---
    response.pop("usage", None)
    response.pop("model", None)
    response.pop("id", None)
    response.pop("object", None)
    response.pop("created", None)
    response["agent_id"] = agent_id

    # Extract assistant reply
    assistant_reply = (
        response.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    if assistant_reply:
        messages.append({"role": "assistant", "content": assistant_reply})

    # --- Background persistence & token deduction ---
    def background_tasks():
        params = {"id": f"eq.{agent_id}"}
        update = {"agent_messages": messages}
        supabase_update("Agents", params, update)
        cut_tokens(user_id, role, tokens, 5)

    Thread(target=background_tasks, daemon=True).start()

    return jsonify(response)