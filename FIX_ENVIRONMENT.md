# 🛠️ Fix Environment Setup for Enhanced Evaluation

## Current Issues
1. PyTorch not installed in your `er_eval` environment
2. Outdated transformers library missing Qwen2.5-VL support
3. Need to set up proper model path

## Solution Steps

### Step 1: Install Required Dependencies

```bash
# Make sure you're in the right environment
conda activate er_eval

# Install PyTorch (choose the right CUDA version for your system)
# For CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CPU only (if no GPU):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Step 2: Update Transformers Library

```bash
# Update transformers to support Qwen2.5-VL
pip install transformers>=4.37.0
# Or install the latest version:
pip install --upgrade transformers

# Install additional requirements
pip install accelerate
pip install qwen-vl-utils  # If available
```

### Step 3: Check What Models You Have

```bash
# Check if you have any Qwen models downloaded
ls ~/.cache/huggingface/hub/ | grep -i qwen

# Or check if models are in your project directory
find /home/jiajunliu -name "*qwen*" -type d 2>/dev/null | head -10
```

### Step 4: Alternative - Use a Simpler Setup

If the full VLM setup is complex, you can test the spatial enhancement with a **mock VLM server**:

```python
# Create a simple mock server for testing
cat > mock_vlm_server.py << 'EOF'
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    """Mock VLM server that returns simple responses"""
    data = request.json
    
    # Simple mock response
    response = {
        "output_text": "navigate to Book",  # Simple action
        "output_len": 13
    }
    
    print(f"Mock VLM received: {data}")
    print(f"Mock VLM responding: {response}")
    
    return jsonify(response)

@app.route("/generate", methods=["POST"])
def generate():
    return chat()

if __name__ == "__main__":
    print("🤖 Starting Mock VLM Server on port 10000...")
    print("This is a simple mock for testing spatial enhancement")
    app.run(host="127.0.0.1", port=10000, debug=False)
EOF

# Run the mock server
python mock_vlm_server.py
```

## Quick Test Setup

### Option A: Use Mock Server (Recommended for Testing)

**Terminal 1** (Start mock server):
```bash
python mock_vlm_server.py
```

**Terminal 2** (Run enhanced evaluation):
```bash
python evaluate/evaluate_enhanced.py
```

### Option B: Fix Real VLM Server

**Terminal 1** (Check environment):
```bash
conda activate er_eval
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

**Terminal 2** (If everything works, start real server):
```bash
# Replace with actual model path - common locations:
# - ~/.cache/huggingface/hub/models--Qwen--Qwen2.5-VL-3B-Instruct
# - /path/to/downloaded/models/Qwen2.5-VL-3B-Instruct

python inference/local_deploy.py --frame "hf" --model_type "qwen2_5_vl" \
  --model_name "Qwen/Qwen2.5-VL-3B-Instruct" --port 10000
```

## Test Spatial Enhancement

Once you have either server running, test the spatial enhancement:

```bash
# This should now work and show spatial reasoning in action
python evaluate/evaluate_enhanced.py

# Look for these log messages:
# [Spatial Enhancement] Spatial enhancement modules loaded successfully
# [Spatial Enhancement] Ambiguity detected: I see 3 books, which one?
```

## Verify Installation

```bash
# Test imports
python -c "
try:
    import torch
    print(f'✅ PyTorch: {torch.__version__}')
    print(f'✅ CUDA available: {torch.cuda.is_available()}')
except:
    print('❌ PyTorch not installed')

try:
    import transformers
    print(f'✅ Transformers: {transformers.__version__}')
except:
    print('❌ Transformers not installed')

try:
    from evaluate.ai2thor_engine.EnhancedRocAgent import EnhancedRocAgent
    print('✅ Enhanced agent available')
except Exception as e:
    print(f'❌ Enhanced agent error: {e}')
"
```

## Expected Output

When everything works, you should see:
```
✅ PyTorch: 2.x.x
✅ CUDA available: True
✅ Transformers: 4.37.x
✅ Enhanced agent available
```

And the evaluation will start processing tasks with spatial reasoning capabilities!