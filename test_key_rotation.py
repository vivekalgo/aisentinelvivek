
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from api_key_manager import GeminiAPIKeyManager

class TestKeyRotation(unittest.TestCase):
    def setUp(self):
        self.api_keys = ["KEY_1", "KEY_2", "KEY_3"]
        self.manager = GeminiAPIKeyManager(self.api_keys)

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_rotation_on_quota_error(self, mock_configure, mock_model_class):
        print("\n--- Testing API Key Rotation ---")
        
        # Setup mock model instance
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        # Define side effects for generate_content
        # First 2 calls raise 429 error, 3rd call succeeds
        error_429 = Exception("429: Resource has been exhausted (e.g. check quota).")
        success_response = MagicMock()
        success_response.text = "Success!"
        
        mock_model.generate_content.side_effect = [error_429, error_429, success_response]
        
        # Execute
        response = self.manager.generate_with_rotation("test prompt")
        
        # Verify
        self.assertIsNotNone(response)
        self.assertEqual(response.text, "Success!")
        self.assertEqual(mock_configure.call_count, 3)
        
        print("\n[VERIFIED] System successfully rotated through 2 failed keys and succeeded on the 3rd key.")

if __name__ == '__main__':
    unittest.main()
