import os
from core.config import settings
from dotenv import load_dotenv

load_dotenv()

def test_config_loading():
    print("="*40)
    print("TEST: CONFIGURATION & ENVIRONMENT")
    print("="*40)
    
    api_key = settings.google_api_key
    print(f"[+] GOOGLE_API_KEY Loaded: {'Yes (Length: ' + str(len(api_key)) + ')' if api_key else 'NO!'}")
    assert api_key != "", "GOOGLE_API_KEY is missing or empty!"
    
    print(f"[+] Model Name: {settings.model_name}")
    assert settings.model_name.startswith("gemini"), f"Model name {settings.model_name} doesn't look like Gemini."
    
    print(f"[+] Environment: {settings.app_env}")
    assert settings.app_env in ["development", "production"], "Invalid APP_ENV"
    
    print(f"[+] Log Level: {settings.log_level}")
    
    print("\n✅ Configuration loaded successfully.")

if __name__ == "__main__":
    test_config_loading()
