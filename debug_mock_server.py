#!/usr/bin/env python3
"""Debug version of mock VLM server with better error handling."""

import socket
import sys
from flask import Flask, request, jsonify

def check_port_available(port):
    """Check if port is available."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0  # 0 means port is in use
    except:
        return True

def create_app():
    """Create Flask app with endpoints."""
    app = Flask(__name__)
    
    @app.route("/chat", methods=["POST"])
    def chat():
        """Mock chat endpoint."""
        try:
            data = request.json
            print(f"📨 Received request: {data}")
            
            response = {
                "output_text": "navigate to object",
                "output_len": 18
            }
            
            print(f"📤 Sending response: {response}")
            return jsonify(response)
            
        except Exception as e:
            print(f"❌ Chat error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/generate", methods=["POST"])
    def generate():
        """Mock generate endpoint."""
        return chat()
    
    @app.route("/health", methods=["GET"])
    def health():
        """Health check."""
        return jsonify({"status": "healthy"})
    
    return app

def main():
    """Main function to start server."""
    port = 10000
    
    print("🔍 Checking environment...")
    print(f"Python version: {sys.version}")
    
    # Check if port is available
    if not check_port_available(port):
        print(f"❌ Port {port} is already in use!")
        print("💡 Try: pkill -f flask")
        return False
    
    print(f"✅ Port {port} is available")
    
    # Create app
    app = create_app()
    
    print("🤖 Starting Debug Mock VLM Server...")
    print("=" * 50)
    print(f"🌐 Server: http://127.0.0.1:{port}")
    print("📋 Endpoints: /chat, /generate, /health")
    print("=" * 50)
    
    try:
        # Start server with explicit settings
        app.run(
            host='127.0.0.1',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()