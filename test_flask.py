#!/usr/bin/env python3
"""Test if Flask can start properly."""

try:
    from flask import Flask
    print("✅ Flask is available")
    
    app = Flask(__name__)
    
    @app.route("/test")
    def test():
        return "Server is working!"
    
    print("✅ Flask app created successfully")
    print("🔧 Trying to start server on port 10000...")
    
    # Try to start the server
    app.run(host="127.0.0.1", port=10000, debug=False)
    
except ImportError as e:
    print(f"❌ Flask not installed: {e}")
    print("💡 Install with: pip install flask")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()