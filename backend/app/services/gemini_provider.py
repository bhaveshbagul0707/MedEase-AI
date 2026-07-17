from google import genai

from app.core.config import get_settings

settings = get_settings()


class GeminiProvider:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_response(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )

            return response.text or "No response generated."

        except Exception as e:
            return f"Gemini Error: {e}"