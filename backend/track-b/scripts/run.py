"""CLI kiểm tra prompt cho pipeline Track B scaffold."""

import argparse
from pathlib import Path

from docai.shared.schema import DocumentType
from docai.track_b import VLMDocumentParser


def main() -> int:
    parser = argparse.ArgumentParser(description="Track B: VLM document pipeline")
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--type", choices=("invoice", "receipt", "contract"), default="invoice")
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error(f"Không tìm thấy file: {args.image}")

    document_type = DocumentType(args.type)
    vlm = VLMDocumentParser()
    print(f"Track B scaffold | input={args.image} | model=NOT SELECTED")
    print(vlm.build_prompt(document_type))
    print("Inference chưa được triển khai.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
