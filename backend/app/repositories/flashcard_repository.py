from app.repositories.base import BaseRepository
from app.models.flashcard import Flashcard


class FlashcardRepository(BaseRepository[Flashcard]):
    def __init__(self, db):
        super().__init__(Flashcard, db)
