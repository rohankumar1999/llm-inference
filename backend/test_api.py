"""
Test script for the LLM Inference API
Run this to verify the backend is working correctly
"""

import asyncio
import httpx

API_URL = "http://localhost:8000"


async def test_api():
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("🧪 Testing LLM Inference API\n")
        
        # Test 1: Root endpoint
        print("1. Testing root endpoint...")
        response = await client.get(f"{API_URL}/")
        assert response.status_code == 200
        data = response.json()
        print(f"   ✓ API is running")
        print(f"   Available models: {', '.join(data['models'])}")
        print()
        
        # Test 2: List models
        print("2. Testing /models endpoint...")
        response = await client.get(f"{API_URL}/models")
        assert response.status_code == 200
        models = response.json()["models"]
        print(f"   ✓ Found {len(models)} models")
        for model in models:
            status = "running" if model["running"] else "stopped"
            print(f"   - {model['name']}: {status}")
        print()
        
        # Test 3: Generate text (will start container if needed)
        print("3. Testing text generation with GPT-2...")
        print("   Note: First run will download model weights (~500MB)")
        print("   This may take a few minutes...")
        
        try:
            response = await client.post(
                f"{API_URL}/generate",
                json={
                    "model_id": "gpt-2",
                    "prompt": "Hello, I am a language model",
                    "max_new_tokens": 50,
                    "temperature": 0.7,
                    "top_p": 0.95,
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✓ Generation successful!")
                print(f"   Model: {result['model_id']}")
                print(f"   Response: {result['generated_text'][:100]}...")
            else:
                print(f"   ✗ Generation failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        print()
        print("✅ API tests complete!")


if __name__ == "__main__":
    try:
        asyncio.run(test_api())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure the backend server is running (python main.py)")

