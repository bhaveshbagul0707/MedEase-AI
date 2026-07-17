from google import genai
from app.core.config import get_settings

settings = get_settings()

print("API Key:", settings.gemini_api_key[:10] + "...")

client = genai.Client(api_key=settings.gemini_api_key)

for model in client.models.list():
    print(model.name)
    break