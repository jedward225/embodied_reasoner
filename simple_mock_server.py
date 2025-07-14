#!/usr/bin/env python3
"""Simple mock VLM server using built-in Python HTTP server."""

import json
import socketserver
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

class MockVLMHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for mock VLM responses."""
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path in ['/chat', '/generate']:
            try:
                # Read request data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                # Generate simple response
                response_text = self.generate_response(request_data)
                response = {
                    "output_text": response_text,
                    "output_len": len(response_text)
                }
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
                print(f"📤 Responded to {parsed_path.path}: {response_text}")
                
            except Exception as e:
                print(f"❌ Error processing request: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'{"error": "Internal server error"}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')
    
    def generate_response(self, request_data):
        """Generate a simple mock response."""
        messages = request_data.get('messages', [])
        
        # Extract last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if isinstance(content, str):
                    user_message = content
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            user_message = item.get('text', '')
                            break
                break
        
        print(f"🤖 Processing: {user_message[:50]}...")
        
        # Simple keyword-based responses
        user_lower = user_message.lower()
        
        if 'book' in user_lower:
            return "navigate to Book"
        elif 'cup' in user_lower:
            return "navigate to Cup"
        elif 'apple' in user_lower:
            return "navigate to Apple"
        elif 'pick' in user_lower or 'grab' in user_lower:
            return "pick up object"
        elif 'put' in user_lower or 'place' in user_lower:
            return "put object in container"
        elif 'open' in user_lower:
            return "open object"
        elif 'close' in user_lower:
            return "close object"
        elif 'observe' in user_lower or 'look' in user_lower:
            return "observe"
        else:
            return "navigate to object"
    
    def log_message(self, format, *args):
        """Suppress default HTTP server logs."""
        pass

def start_server():
    """Start the mock VLM server."""
    port = 10000
    
    try:
        with socketserver.TCPServer(("127.0.0.1", port), MockVLMHandler) as httpd:
            print("🤖 Simple Mock VLM Server Starting...")
            print("=" * 50)
            print(f"🌐 Server: http://127.0.0.1:{port}")
            print("📋 Endpoints: /chat, /generate")
            print("💡 No external dependencies required!")
            print("=" * 50)
            print("✅ Server is ready! Test with enhanced evaluation.")
            print("📝 Press Ctrl+C to stop")
            print()
            
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use!")
            print("💡 Stop other servers or use a different port")
        else:
            print(f"❌ Server error: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    start_server()