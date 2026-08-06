from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    RateLimitError,
)

from app.core.config import get_settings

settings = get_settings()


class AIProviderError(Exception):
    """Raised when the AI provider cannot generate a response."""


class OpenRouterProvider:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=60.0,
        )

    async def generate_response(
        self,
        *,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="openrouter/free",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    *messages,
                ],
            )

            content = response.choices[0].message.content

            if not content or not content.strip():
                raise AIProviderError(
                    "AI provider returned an empty response"
                )

            return content.strip()

        except RateLimitError as exc:
            raise AIProviderError(
                "AI service is busy right now. Please try again shortly."
            ) from exc

        except APITimeoutError as exc:
            raise AIProviderError(
                "AI service took too long to respond. Please try again."
            ) from exc

        except APIConnectionError as exc:
            raise AIProviderError(
                "Unable to connect to the AI service."
            ) from exc

        except APIStatusError as exc:
            raise AIProviderError(
                f"AI service returned an error ({exc.status_code})."
            ) from exc