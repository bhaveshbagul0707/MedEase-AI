import asyncio

from app.models.enums import StudyMode
from app.services.ai_engine import AIEngine


async def main():
    engine = AIEngine()

    response = await engine.generate_response(
        study_mode=StudyMode.LEARN,
        question="What is Diabetes?",
        program="MBBS",
        year=2,
    )

    print(response)


asyncio.run(main())