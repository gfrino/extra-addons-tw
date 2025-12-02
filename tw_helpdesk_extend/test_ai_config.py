#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify AI configuration and API connectivity.
Run this from Odoo shell or as a standalone test.
"""
import requests
import json

def test_openai_api(api_key, model='gpt-4o'):
    """Test if the OpenAI API key works."""
    print(f"Testing OpenAI API with model: {model}")
    print(f"API Key (first 10 chars): {api_key[:10]}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, API is working!' in JSON format with a key 'message'."}
        ],
        "temperature": 0.1
    }
    
    try:
        print("\nSending request to OpenAI...")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✓ Success! Response: {content}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    # Test with your API key
    API_KEY = "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"
    
    test_openai_api(API_KEY)
