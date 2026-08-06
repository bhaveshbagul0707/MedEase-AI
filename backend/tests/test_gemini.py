import asyncio

from app.services.gemini_provider import GeminiProvider


async def main():
    provider = GeminiProvider()

    response = await provider.generate_response(
        "Explain diabetes in two simple sentences."
    )

    print(response)


asyncio.run(main())