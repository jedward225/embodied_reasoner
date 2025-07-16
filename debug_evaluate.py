#!/usr/bin/env python3
"""Debug version of evaluate.py to understand what's happening."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 DEBUG: Starting evaluation debug...")

# Check MODE
print("🔍 DEBUG: Checking MODE...")
MODE = "API"  # This is what it's set to
print(f"🔍 DEBUG: MODE = {MODE}")

# Check imports
print("🔍 DEBUG: Testing imports...")
try:
    from ai2thor_engine.RocAgent import RocAgent
    print("✅ DEBUG: RocAgent imported successfully")
except Exception as e:
    print(f"❌ DEBUG: RocAgent import failed: {e}")

try:
    from utils import *
    print("✅ DEBUG: utils imported successfully")
except Exception as e:
    print(f"❌ DEBUG: utils import failed: {e}")

try:
    from prompt import *
    print("✅ DEBUG: prompt imported successfully")
except Exception as e:
    print(f"❌ DEBUG: prompt import failed: {e}")

# Check argument parsing
print("🔍 DEBUG: Testing argument parsing...")
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--input_path", type=str, default="./data/test_809.json", help="input file path")
parser.add_argument("--model_name", type=str, default="Qwen2.5-VL-3B-Instruct", help="")
parser.add_argument("--batch_size", type=int, default=200, help="")
parser.add_argument("--port", type=int, default=10000, help="")
parser.add_argument("--cur_count", type=int, default=1, help="")
parser.add_argument("--total_count", type=int, default=4, help="")

args = parser.parse_args(["--input_path", "../data/test_mini.json", "--model_name", "debug_test", "--cur_count", "1", "--total_count", "1"])
print(f"✅ DEBUG: Args parsed: {args}")

# Check data loading
print("🔍 DEBUG: Testing data loading...")
try:
    from evaluate import load_data
    data = load_data(args)
    print(f"✅ DEBUG: Data loaded: {len(data)} items")
    print(f"✅ DEBUG: First item: {data[0] if data else 'No data'}")
except Exception as e:
    print(f"❌ DEBUG: Data loading failed: {e}")
    import traceback
    traceback.print_exc()

# Check what happens in main execution
print("🔍 DEBUG: Checking main execution logic...")
print(f"🔍 DEBUG: MODE={MODE}")

if MODE == "LOCAL":
    print("🔍 DEBUG: Would enter LOCAL mode")
elif MODE == "API":
    print("🔍 DEBUG: Entering API mode")
    match_item_model = "Qwen/Qwen2.5-72B-Instruct"
    print(f"🔍 DEBUG: Set match_item_model = {match_item_model}")
    print("❌ DEBUG: API mode has no evaluation logic! This is why it exits!")
else:
    print(f"🔍 DEBUG: Unknown mode: {MODE}")

print("🔍 DEBUG: Script would exit here because API mode is incomplete!")