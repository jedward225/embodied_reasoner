#!/usr/bin/env python3
"""Mock VLM Server for testing spatial enhancement without full model setup."""

from flask import Flask, request, jsonify
import json
import random

app = Flask(__name__)

# Simple response templates for different task types
RESPONSE_TEMPLATES = {
    "navigate": [
        "navigate to {object}",
        "go to {object}",
        "move to {object}"
    ],
    "pickup": [
        "pick up {object}",
        "grab {object}",
        "take {object}"
    ],
    "put": [
        "put {object} in {container}",
        "place {object} on {container}",
        "move {object} to {container}"
    ],
    "observe": [
        "observe",
        "look around",
        "examine scene"
    ],
    "open": [
        "open {object}",
        "open the {object}"
    ],
    "close": [
        "close {object}",
        "close the {object}"
    ],
    "toggle": [
        "toggle {object}",
        "switch {object}"
    ]
}

def generate_mock_response(messages):
    """Generate a simple mock response based on the input."""
    
    # Extract the last user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, str):
                user_message = content
            elif isinstance(content, list):
                # Extract text from multimodal content
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        user_message = item.get("text", "")
                        break
            break
    
    print(f"🤖 Processing user message: {user_message[:100]}...")
    
    # Simple keyword-based response generation
    user_lower = user_message.lower()
    
    if "book" in user_lower:
        if "left" in user_lower or "左" in user_lower:
            return "navigate to Book"  # Will test spatial reasoning
        elif "right" in user_lower or "右" in user_lower:
            return "navigate to Book"
        elif "table" in user_lower or "桌" in user_lower:
            return "navigate to Book"
        else:
            return "navigate to Book"  # Generic response
    
    elif "cup" in user_lower:
        return random.choice(RESPONSE_TEMPLATES["navigate"]).format(object="Cup")
    
    elif "grab" in user_lower or "pick" in user_lower or "拿" in user_lower:
        # Extract object after pick/grab
        for obj in ["book", "cup", "apple", "plate", "knife"]:
            if obj in user_lower:
                return random.choice(RESPONSE_TEMPLATES["pickup"]).format(object=obj.title())
        return "pick up object"
    
    elif "put" in user_lower or "place" in user_lower or "放" in user_lower:
        return random.choice(RESPONSE_TEMPLATES["put"]).format(object="object", container="container")
    
    elif "open" in user_lower or "打开" in user_lower:
        return random.choice(RESPONSE_TEMPLATES["open"]).format(object="object")
    
    elif "close" in user_lower or "关" in user_lower:
        return random.choice(RESPONSE_TEMPLATES["close"]).format(object="object")
    
    elif "observe" in user_lower or "look" in user_lower or "观察" in user_lower:
        return random.choice(RESPONSE_TEMPLATES["observe"])
    
    elif "toggle" in user_lower or "switch" in user_lower:
        return random.choice(RESPONSE_TEMPLATES["toggle"]).format(object="object")
    
    else:
        # Default navigation response
        return "navigate to object"

@app.route("/chat", methods=["POST"])
def chat():
    """Mock chat endpoint that mimics VLM behavior."""
    try:
        data = request.json
        messages = data.get("messages", [])
        
        # Generate mock response
        response_text = generate_mock_response(messages)
        
        response = {
            "output_text": response_text,
            "output_len": len(response_text)
        }
        
        print(f"📤 Mock VLM response: {response_text}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Mock VLM error: {e}")
        return jsonify({
            "output_text": "navigate to object",
            "output_len": 18
        }), 500

@app.route("/generate", methods=["POST"])
def generate():
    """Mock generate endpoint (same as chat for simplicity)."""
    return chat()

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "server": "mock_vlm"})

if __name__ == "__main__":
    print("🤖 Starting Mock VLM Server...")
    print("=" * 50)
    print("🎯 Purpose: Test spatial enhancement without full VLM setup")
    print("🌐 Server: http://127.0.0.1:10000")
    print("📋 Endpoints: /chat, /generate, /health")
    print("💡 This server provides simple responses for testing")
    print("🧠 Spatial enhancement will work on top of these responses")
    print("=" * 50)
    print("✅ Ready to test enhanced evaluation!")
    print()
    
    try:
        app.run(host="127.0.0.1", port=10000, debug=False, use_reloader=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print("\n❌ Port 10000 is already in use!")
            print("💡 Kill any existing servers and try again")
            print("💡 Or use: pkill -f 'port.*10000'")
        else:
            print(f"\n❌ Server error: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")