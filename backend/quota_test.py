from google import genai
from google.genai import types

from app.core.config import get_settings

settings = get_settings()

client = genai.Client(api_key=settings.gemini_api_key)

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Hello",
        config=types.GenerateContentConfig(
            max_output_tokens=20,
            temperature=0,
        ),
    )

    print(response.text)

except Exception as e:
    print(type(e).__name__)
    print(e)