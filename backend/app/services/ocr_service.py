from __future__ import annotations

from abc import ABC, abstractmethod


class OCRService(ABC):
    @abstractmethod
    def ocr_image(self, image_bytes: bytes) -> str:
        raise NotImplementedError


class DummyOCRService(OCRService):
    def ocr_image(self, image_bytes: bytes) -> str:
        # In production, implement Tesseract or other OCR. For now, return an empty string.
        return ""
