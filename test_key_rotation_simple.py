
import sys
import os
import time
from unittest.mock import MagicMock

# Add backend to path
current_dir = os.getcwd()
backend_dir = os.path.join(current_dir, 'backend')
sys.path.append(backend_dir)

print(f"Added {backend_dir} to path")

try:
    import google.generativeai as genai
    print("[OK] google.generativeai imported successfully")
except ImportError:
    print("[ERROR] google.generativeai not found. Installing...")
    os.system(f"{sys.executable} -m pip install google-generativeai")
    import google.generativeai as genai

from api_key_manager import GeminiAPIKeyManager

def test_rotation():
    print("\n--- Testing API Key Rotation Logic ---")
    
    # Mock keys
    api_keys = ["KEY_1", "KEY_2", "KEY_3"]
    manager = GeminiAPIKeyManager(api_keys)
    print(f"Initialized manager with keys: {api_keys}")
    
    # Mock the generative model
    mock_model = MagicMock()
    
    # Define side effects: 
    # 1. 429 Quota Error
    # 2. 429 Quota Error
    # 3. Success
    error_429 = Exception("429: Resource has been exhausted (e.g. check quota).")
    
    success_response = MagicMock()
    success_response.text = "Success!"
    
    # We need to patch the actual method on the class or instance
    # Here we will monkey-patch the genai.GenerativeModel to return our mock
    original_model_cls = genai.GenerativeModel
    
    def side_effect(*args, **kwargs):
        # Determine which call this is
        call_count = getattr(side_effect, 'call_count', 0)
        side_effect.call_count = call_count + 1
        
        print(f"  -> Mock API Call #{side_effect.call_count}")
        
        if side_effect.call_count <= 2:
            print("     [Simulating 429 Error]")
            raise error_429
        else:
            print("     [Simulating Success]")
            return success_response

    mock_model.generate_content = side_effect
    
    # Mock the class to return our mock_model
    genai.GenerativeModel = MagicMock(return_value=mock_model)
    
    # Mock configure to track key usage
    def mock_configure(api_key):
        print(f"  -> genai.configure() called with key: {api_key}")
        
    genai.configure = mock_configure
    
    try:
        print("\nStarting generation request...")
        response = manager.generate_with_rotation("test prompt")
        
        if response and response.text == "Success!":
            print("\n[SUCCESS] Test passed! The manager rotated through failed keys and succeeded.")
        else:
            print("\n[FAILED] Response was not as expected.")
            
    except Exception as e:
        print(f"\n[FAILED] Exception occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Restore original
        genai.GenerativeModel = original_model_cls

if __name__ == "__main__":
    test_rotation()
