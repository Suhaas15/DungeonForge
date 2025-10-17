#!/usr/bin/env python3
"""
Test script for Stack-AI Image Generation API
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Stack-AI Configuration
API_URL = os.getenv('STACK_AI_API_URL')
API_KEY = os.getenv('STACK_AI_API_KEY')

def query(payload):
    """
    Send a request to Stack-AI API
    
    Args:
        payload: dict with 'user_id' and 'in-0' (scene description)
    
    Returns:
        JSON response from API
    """
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    print(f"🔄 Sending request to Stack-AI...")
    print(f"📝 Scene description: {payload.get('in-0', '')[:100]}...")
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success!")
            return response.json()
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return None

# Test the API
if __name__ == "__main__":
    print("=" * 60)
    print("Stack-AI Image Generation API Test")
    print("=" * 60)
    
    if not API_URL or not API_KEY:
        print("❌ Error: STACK_AI_API_URL or STACK_AI_API_KEY not found in .env")
        exit(1)
    
    print(f"🔑 API URL: {API_URL[:50]}...")
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print()
    
    # Test payload
    test_payload = {
        "user_id": "test_user_123",
        "in-0": "A medieval fantasy tavern with adventurers gathered around a wooden table, dimly lit by candlelight, mysterious hooded figure in the corner"
    }
    
    # Make the API call
    result = query(test_payload)
    
    if result:
        print("\n" + "=" * 60)
        print("📦 API Response:")
        print("=" * 60)
        import json
        print(json.dumps(result, indent=2))
        
        # Try to extract image URL
        if isinstance(result, dict):
            # Check for outputs dictionary (Stack-AI specific format)
            if 'outputs' in result:
                outputs = result['outputs']
                
                if isinstance(outputs, dict) and 'out-0' in outputs:
                    out_value = outputs['out-0']
                    print(f"\n🖼️  out-0 value: {out_value}")
                    
                    # Try to parse if it's a string representation
                    if isinstance(out_value, str):
                        import ast
                        try:
                            parsed = ast.literal_eval(out_value)
                            if isinstance(parsed, dict) and 'image_url' in parsed:
                                image_url = parsed['image_url']
                                print(f"\n✅ Image URL extracted: {image_url}")
                        except:
                            if out_value.startswith('http'):
                                print(f"\n✅ Image URL: {out_value}")
    else:
        print("\n❌ Failed to get response from Stack-AI API")

