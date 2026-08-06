from pathlib import Path

from app.models.chat import Message
from app.models.enums import MessageRole, StudyMode
from app.services.openrouter_provider import OpenRouterProvider


class AIEngine:
    def __init__(self):
        self.provider = OpenRouterProvider()
        self.prompt_dir = Path(__file__).parent / "prompts"

    def _load_prompt(self, study_mode: StudyMode) -> str:
        prompt_files = {
            StudyMode.LEARN: "learn.txt",
            StudyMode.EXAM: "exam.txt",
            StudyMode.VIVA: "viva.txt",
            StudyMode.REVISION: "revision.txt",
            StudyMode.CLINICAL: "clinical.txt",
        }

        filename = prompt_files.get(study_mode)

        if filename is None:
            raise ValueError(f"Unsupported study mode: {study_mode}")

        prompt_path = self.prompt_dir / filename
        return prompt_path.read_text(encoding="utf-8")

    async def generate_response(
        self,
        *,
        study_mode: StudyMode,
        question: str,
        program: str,
        year: int,
        conversation_history: list[Message] | None = None,
    ) -> str:
        template = self._load_prompt(study_mode)

        # The template becomes the instruction for how MedAssist should answer.
        system_prompt = template.format(
            question="the student's current question",
            program=program,
            year=year,
            mode=study_mode.value,
        )

        messages: list[dict[str, str]] = []

        if conversation_history:
            for message in conversation_history[-10:]:
                if message.role == MessageRole.USER:
                    role = "user"
                elif message.role == MessageRole.ASSISTANT:
                    role = "assistant"
                else:
                    continue

                messages.append(
                    {
                        "role": role,
                        "content": message.content,
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        return await self.provider.generate_response(
            system_prompt=system_prompt,
            messages=messages,
        )