"""CLI kiểm tra đầu vào cho pipeline Track A scaffold."""

import argparse
from pathlib import Path

from docai.track_a import LayoutDetector, LayoutLMv3Extractor, OCRExtractor


def main() -> int:
    parser = argparse.ArgumentParser(description="Track A: Classic document pipeline")
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--lang", choices=("vi", "en"), default="vi")
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error(f"Không tìm thấy file: {args.image}")

    print(f"Track A scaffold | input={args.image} | lang={args.lang}")
    print(f"Các stage: {LayoutDetector.__name__}, {OCRExtractor.__name__}, {LayoutLMv3Extractor.__name__}")
    print("Inference chưa được triển khai.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
