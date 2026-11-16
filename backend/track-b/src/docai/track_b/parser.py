"""Parser VLM của Track B."""

import json
from pathlib import Path
from typing import Any

from docai.shared.schema import DocumentType, UnifiedDocumentOutput


class VLMDocumentParser:
    """Tạo prompt và kiểm tra response; kết nối model chưa được triển khai."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name
        self.endpoint_url = None

    def build_prompt(self, document_type: DocumentType) -> str:
        if document_type in (DocumentType.INVOICE, DocumentType.RECEIPT):
            request = "seller, invoice_date, total_amount, tax_amount, line_items"
        elif document_type == DocumentType.CONTRACT:
            request = "parties, agreement_date, governing_law, key clauses and page evidence"
        else:
            request = "document type and supported fields"
        return (
            "Extract only information supported by the document. Do not infer missing values. "
            f"Return JSON for document_type={document_type.value} with fields for: {request}. "
            "Each field must include field_name, field_value, confidence, page_number, raw_text, "
            "and bounding_box when available."
        )

    def parse(self, image_input: str | Path | Any, document_type: DocumentType) -> UnifiedDocumentOutput:
        raise NotImplementedError("Track B model inference chưa được triển khai.")

    @staticmethod
    def parse_raw_json_to_output(
        raw_json: str, document_type: DocumentType, latency_ms: float | None = None
    ) -> UnifiedDocumentOutput:
        payload = json.loads(raw_json)
        payload.setdefault("document_type", document_type.value)
        payload.setdefault("pipeline_track", "track_b_vlm")
        if latency_ms is not None:
            payload.setdefault("execution_time_ms", latency_ms)
        return UnifiedDocumentOutput.model_validate(payload)
