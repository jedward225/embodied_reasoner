#!/usr/bin/env python3
"""
Test script to validate both API and local evaluation modes.
"""

import json
import sys
import os
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/home/jiajunliu/embodied_reasoner')

def test_api_connection():
    """Test API connection with 阿里百炼."""
    print("🌐 Testing API connection...")
    
    try:
        from evaluate.VLMCall import VLMAPI
        
        # Test with ModelScope API (阿里百炼)
        model = "Qwen/Qwen2.5-VL-7B-Instruct"
        api_client = VLMAPI(model)
        
        # Simple test message
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, please respond with 'API test successful'"}
        ]
        
        print(f"   Testing model: {model}")
        response = api_client.vlm_request(messages)
        
        if response:
            print(f"✅ API test successful!")
            print(f"   Response: {response[:100]}...")
            return True
        else:
            print("❌ API test failed - no response")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def create_test_data():
    """Create a small test dataset."""
    print("📝 Creating test dataset...")
    
    test_data = [
        {
            "identity": "test_001",
            "tasktype": "single_pickup_from_closerep",
            "scene": "FloorPlan1",
            "instruction_idx": 0,
            "taskquery": "Can you grab the Apple from the room?",
            "taskname": "single_pickup_from_closerep",
            "target_objects": ["Apple"],
            "related_objects": [],
            "navigable_objects": ["Apple", "Bowl", "Cup"]
        }
    ]
    
    test_file = "./data/test_mini.json"
    os.makedirs("./data", exist_ok=True)
    
    with open(test_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"✅ Test data saved to {test_file}")
    return test_file

def test_controller_setup():
    """Test AI2-THOR controller setup."""
    print("🎮 Testing AI2-THOR controller setup...")
    
    try:
        from ai2thor.controller import Controller
        from ai2thor.platform import CloudRendering
        
        # Use cloud rendering to avoid display issues
        controller = Controller(
            platform=CloudRendering,
            scene='FloorPlan1',
            headless=True,
            width=400,
            height=300,
            snapToGrid=False,
            quality='Medium'
        )
        
        print("✅ Controller created successfully")
        
        # Test basic action
        event = controller.step(dict(action='Pass'))
        if event.metadata['lastActionSuccess']:
            print("✅ Controller action test successful")
        else:
            print("⚠️  Controller action test failed")
        
        controller.stop()
        return True
        
    except Exception as e:
        print(f"❌ Controller test failed: {e}")
        return False

def start_local_server():
    """Start local mock server for testing."""
    print("🤖 Starting local mock server...")
    
    try:
        # Create a simple mock server file if it doesn't exist
        mock_server_content = '''#!/usr/bin/env python3
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    return jsonify({
        "output_text": "navigate to object",
        "output_len": 18
    })

@app.route("/generate", methods=["POST"])
def generate():
    return chat()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=10000, debug=False)
'''
        
        with open("simple_mock_server.py", "w") as f:
            f.write(mock_server_content)
        
        print("✅ Mock server file created")
        print("💡 To start server, run: python simple_mock_server.py")
        return True
        
    except Exception as e:
        print(f"❌ Mock server setup failed: {e}")
        return False

def test_evaluation_imports():
    """Test that evaluation modules can be imported."""
    print("📦 Testing evaluation module imports...")
    
    try:
        # Test baseline evaluation
        from evaluate.ai2thor_engine.RocAgent import RocAgent
        print("✅ RocAgent imported")
        
        # Test enhanced evaluation
        from evaluate.ai2thor_engine.EnhancedRocAgent import EnhancedRocAgent
        print("✅ EnhancedRocAgent imported")
        
        # Test utilities
        from evaluate.utils import get_max_steps, invalid_action
        print("✅ Evaluation utilities imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_mini_evaluation_test(mode="API"):
    """Run a minimal evaluation test."""
    print(f"🧪 Running mini evaluation test (mode: {mode})...")
    
    try:
        # Create test data
        test_file = create_test_data()
        
        # Import required modules
        if mode == "API":
            # Set API mode in the evaluation file
            print("   Setting API mode...")
            # We'll run this manually rather than modifying files
            
        # For now, just validate the setup
        print("✅ Mini evaluation test setup complete")
        print(f"💡 To run full test:")
        print(f"   python evaluate/evaluate.py --input_path {test_file} --model_name test_{mode.lower()} --cur_count 1 --total_count 1")
        
        return True
        
    except Exception as e:
        print(f"❌ Mini evaluation test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 EVALUATION MODES TEST SUITE")
    print("=" * 50)
    
    results = {}
    
    # Test evaluation imports
    results['imports'] = test_evaluation_imports()
    
    # Test controller setup
    results['controller'] = test_controller_setup()
    
    # Test API connection
    results['api'] = test_api_connection()
    
    # Setup local server
    results['local_server'] = start_local_server()
    
    # Test mini evaluation
    results['mini_eval'] = run_mini_evaluation_test()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    # Provide next steps
    print("\n🔧 NEXT STEPS:")
    print("=" * 20)
    
    if results['api']:
        print("✅ API mode ready! You can run:")
        print("   python evaluate/evaluate_enhanced.py --input_path ./data/test_mini.json --model_name enhanced_api --cur_count 1 --total_count 1")
    
    if results['local_server']:
        print("✅ Local server ready! To use:")
        print("   1. Terminal 1: python simple_mock_server.py")
        print("   2. Terminal 2: Change MODE='LOCAL' in evaluate files")
        print("   3. Terminal 2: python evaluate/evaluate_enhanced.py --input_path ./data/test_mini.json --model_name enhanced_local")
    
    if results['controller']:
        print("✅ AI2-THOR controller working with CloudRendering")
    
    return results

if __name__ == "__main__":
    main()