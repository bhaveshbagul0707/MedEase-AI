import asyncio

from app.services.openrouter_provider import OpenRouterProvider


async def main():
    provider = OpenRouterProvider()

    response = await provider.generate_response(
        "Explain diabetes in two simple sentences."
    )

    print(response)


asyncio.run(main())