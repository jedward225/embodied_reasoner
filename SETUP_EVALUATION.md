# 🚀 Setup Guide for Running Enhanced Evaluation

## The Issue
The evaluation script needs a VLM (Vision Language Model) server running at `http://127.0.0.1:10000/chat` to work properly. This is required for both the original and enhanced evaluation scripts.

## Solution: Start VLM Server First

### Step 1: Start the VLM Server
Open a **separate terminal** and run:

```bash
cd /home/jed/embodied_reasoner

# Start the VLM server (replace with your actual model path)
python inference/local_deploy.py --frame "hf" --model_type "qwen2_5_vl" --model_name "Qwen/Qwen2.5-VL-3B-Instruct" --port 10000
```

**Note**: You need to replace `"Qwen/Qwen2.5-VL-3B-Instruct"` with the actual path to your model.

### Step 2: Wait for Server to Start
You should see output like:
```
* Running on http://127.0.0.1:10000
* Debug mode: off
```

### Step 3: Run Enhanced Evaluation
In your **original terminal**, run:

```bash
# For enhanced evaluation with spatial reasoning
python evaluate/evaluate_enhanced.py

# OR for original evaluation  
python evaluate/evaluate.py
```

## Alternative: Modify Evaluation for Local Mode

If you don't want to run a separate server, you can modify the evaluation script to use local mode instead of API mode:

### Option 1: Change MODE in evaluate_enhanced.py
```python
# In evaluate/evaluate_enhanced.py, change line 12:
MODE = "LOCAL"  # instead of "API"
```

### Option 2: Run with Local Mode Flag
```bash
# If the script supports command line arguments for mode
python evaluate/evaluate_enhanced.py --mode LOCAL
```

## Quick Verification

To test if your VLM server is working:

```bash
# Test the server endpoint
curl -X POST http://127.0.0.1:10000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

## Enhanced Evaluation Differences

Once you have the VLM server running, the enhanced evaluation will provide:

1. **Smart Object Selection**: When there are multiple books, cups, etc., it will choose based on spatial cues
2. **Better Navigation**: Improved positioning based on object geometry
3. **Bilingual Support**: Works with Chinese instructions like "左边的书"
4. **Fallback Safety**: If enhancements fail, falls back to original behavior

## Common Issues

### Server Connection Refused
- Make sure the VLM server is running on port 10000
- Check if another process is using port 10000: `netstat -ln | grep 10000`

### Model Loading Issues
- Ensure the model path in `local_deploy.py` is correct
- Check if you have enough GPU memory for the model
- Verify model files are downloaded and accessible

### Import Errors
- Make sure you're in the correct conda environment: `conda activate er_eval`
- Verify all dependencies are installed

## Success Indicators

When everything is working correctly, you should see:
1. VLM server starts without errors
2. Evaluation begins processing tasks
3. For enhanced evaluation: `[Spatial Enhancement] Spatial enhancement modules loaded successfully`
4. Tasks progress through the pipeline without connection errors

## Performance Monitoring

For the enhanced evaluation, you can monitor spatial reasoning usage:
```python
# The enhanced agent will log statistics like:
# [Spatial Enhancement] Ambiguity detected: I see 3 books, which one?
# [Spatial Enhancement] Enhancement navigation failed: falling back to original
```

This helps you understand how often the spatial enhancements are being used and their effectiveness.