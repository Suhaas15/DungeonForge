#!/usr/bin/env python3
"""
Test script for Stack AI image generation integration
Run this to verify the Stack AI API is working correctly
"""

import requests
import json
import sys

# Stack-AI Image Generation Configuration
STACK_AI_API_URL = "https://api.stack-ai.com/inference/v0/run/74329701-0f1c-429f-94f2-1a8bff522ae5/68f2b40560ba42fb86bdcc9b"
STACK_AI_API_KEY = "2cca805e-ef0f-4c2c-990a-389db4d098d3"

def test_image_generation(summary_text, user_id="test_user"):
    """Test the Stack AI image generation API"""
    print("=" * 80)
    print("Testing Stack AI Image Generation")
    print("=" * 80)
    print(f"\nInput Summary: {summary_text}")
    print(f"User ID: {user_id}\n")
    
    headers = {
        'Authorization': f'Bearer {STACK_AI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "user_id": user_id,
        "in-0": summary_text
    }
    
    print("Sending request to Stack AI API...")
    print(f"URL: {STACK_AI_API_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(STACK_AI_API_URL, headers=headers, json=payload, timeout=90)
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}\n")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print("Response Data (JSON):")
                print(json.dumps(response_data, indent=2))
                print("\n" + "=" * 80)
                print("SUCCESS! API returned 200")
                print("=" * 80)
                
                # Try to extract image URL using the same logic as the backend
                image_url = None
                
                if isinstance(response_data, dict):
                    # Check for outputs dictionary (Stack-AI specific format)
                    if 'outputs' in response_data:
                        outputs = response_data['outputs']
                        
                        # outputs can be either a dict or a list
                        if isinstance(outputs, dict) and 'out-0' in outputs:
                            out_value = outputs['out-0']
                            print(f"\nFound out-0: {out_value}")
                            
                            # The value might be a string representation of a dict
                            if isinstance(out_value, str):
                                # Try to parse as Python literal
                                import ast
                                try:
                                    parsed = ast.literal_eval(out_value)
                                    if isinstance(parsed, dict) and 'image_url' in parsed:
                                        image_url = parsed['image_url']
                                        print(f"Parsed image URL from string dict: {image_url}")
                                except (ValueError, SyntaxError) as e:
                                    print(f"Could not parse out-0 as dict: {e}")
                                    # Maybe it's already a URL
                                    if out_value.startswith('http'):
                                        image_url = out_value
                            
                            # If it's already a dict
                            if isinstance(out_value, dict) and 'image_url' in out_value:
                                image_url = out_value['image_url']
                        
                        # Check if outputs is a list
                        if isinstance(outputs, list) and len(outputs) > 0:
                            output = outputs[0]
                            if isinstance(output, dict):
                                image_url = output.get('image_url') or output.get('url')
                            elif isinstance(output, str):
                                image_url = output
                    
                    # Check direct fields
                    if not image_url:
                        image_url = (response_data.get('image_url') or 
                                   response_data.get('url') or 
                                   response_data.get('output') or 
                                   response_data.get('result') or
                                   response_data.get('image'))
                
                if isinstance(response_data, str):
                    image_url = response_data
                
                if image_url:
                    print(f"\n✅ Extracted Image URL: {image_url}")
                else:
                    print("\n⚠️ Could not extract image URL from response")
                    print("You may need to update the extraction logic in app.py")
                
                return True
                
            except json.JSONDecodeError:
                print("Response is not JSON:")
                print(response.text)
                print("\n⚠️ API returned non-JSON response")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response Body: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test with a sample D&D scene description
    test_summaries = [
        "You enter a mysterious tavern where a hooded figure awaits with a map. The adventure begins.",
        "Dark forest at night with glowing eyes watching from the shadows. Ancient ruins loom ahead.",
        "A dragon perches atop a mountain of gold, its red scales glinting in the torchlight."
    ]
    
    if len(sys.argv) > 1:
        # Use command line argument if provided
        summary = " ".join(sys.argv[1:])
        test_image_generation(summary)
    else:
        # Test with sample summaries
        print("\nTesting with sample D&D scene descriptions...\n")
        for i, summary in enumerate(test_summaries, 1):
            print(f"\n{'='*80}")
            print(f"TEST {i}/{len(test_summaries)}")
            print(f"{'='*80}\n")
            success = test_image_generation(summary, f"test_user_{i}")
            if not success:
                print("\n⚠️ Test failed, stopping here.")
                break
            print("\n")

