"""Các stage Classic của Track A, giữ trong một module gọn."""

from pathlib import Path
from typing import Any


class LayoutDetector:
    """Khung phát hiện layout; model chưa được chọn hoặc nạp."""

    def __init__(self, model_path: str = "", conf_threshold: float = 0.25) -> None:
        self.model_path = model_path or None
        self.conf_threshold = conf_threshold
        self.model = None

    def detect(self, image_input: str | Path | Any) -> list[dict[str, Any]]:
        raise NotImplementedError("Track A layout inference chưa được triển khai.")

    @staticmethod
    def filter_regions_by_type(
        detections: list[dict[str, Any]], region_type: str
    ) -> list[dict[str, Any]]:
        return [item for item in detections if item.get("label") == region_type]


class OCRExtractor:
    """Khung OCR; engine chưa được nạp."""

    def __init__(self, lang: str = "vi") -> None:
        self.lang = lang
        self.ocr_engine = None

    def extract_text_and_boxes(
        self, image_input: str | Path | Any,
        layout_regions: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError("Track A OCR inference chưa được triển khai.")

    @staticmethod
    def convert_polygon_to_box(polygon: list[list[float]]) -> list[float]:
        if not polygon:
            raise ValueError("Polygon phải có ít nhất một điểm.")
        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]
        return [min(xs), min(ys), max(xs), max(ys)]


class LayoutLMv3Extractor:
    """Khung KIE cho Track A; checkpoint production chưa được chọn."""

    def __init__(self, model_checkpoint: str | None = None) -> None:
        self.model_checkpoint = model_checkpoint
        self.processor = None
        self.model = None

    def extract_fields(
        self, image_input: str | Path | Any,
        tokens: list[str], boxes_1000: list[list[int]],
    ) -> list[dict[str, Any]]:
        raise NotImplementedError("Track A KIE inference chưa được triển khai.")
