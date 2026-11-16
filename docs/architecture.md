# Kiến trúc DocAI

DocAI giữ một package Python nhỏ để thử nghiệm hai pipeline trích xuất tài
liệu. Invoice và Contract cùng đi qua một schema; model inference hiện chưa
được triển khai.

## Luồng xử lý

```text
React → FastAPI → Track A hoặc Track B
                 → UnifiedDocumentOutput → React
```

- **Track A** chia việc thành layout, OCR và KIE.
- **Track B** tạo prompt cho VLM, parse response và kiểm tra schema.
- Hai track dùng cùng [`backend/shared/src/docai/shared/schema.py`](../backend/shared/src/docai/shared/schema.py), được
  mirror trong `frontend/src/types/document.ts`.

## Cây thư mục

```text
backend/
  shared/src/docai/shared/       # API, config, schema dùng chung
  track-a/
    src/docai/track_a/            # Code thuộc Thành viên A
    scripts/run.py                # CLI riêng của A
    README.md
    CHANGELOG.md
  track-b/
    src/docai/track_b/            # Code thuộc Thành viên B
    scripts/run.py                # CLI riêng của B
    README.md
    CHANGELOG.md
tests/
frontend/
docs/
```

`backend/track-a/` thuộc Thành viên A; `backend/track-b/` thuộc Thành viên B.
Hai thư mục dùng cùng tên con `src/` và `scripts/` để sau này có thể ghép theo
loại nội dung. `backend/shared/` chứa package và contract dùng chung; tests,
frontend, docs và cấu hình root cũng dùng chung. Mỗi owner có đúng một
`CHANGELOG.md` tại thư mục của mình. Script chỉ nhận argument và gọi package.

## Contract dữ liệu

`UnifiedDocumentOutput` có document type, danh sách fields, confidence,
risk flags, thời gian tùy chọn, pipeline track và metadata. Schema kiểm tra
hình dạng dữ liệu, không xác nhận nội dung có đúng với tài liệu hay không.
Khi đổi schema, cập nhật đồng thời TypeScript type ở frontend.

## Trạng thái hiện tại

- `GET /health` hoạt động qua `docai.shared.api`.
- `POST /parse/classic` và `POST /parse/vlm` giữ route và trả `501` cho tới
  khi inference tương ứng được triển khai.
- Layout/OCR/KIE và VLM adapter hiện là scaffold.
- Model/checkpoint chưa được chọn; không cài framework model lớn hoặc tải
  weights cho tới khi có lựa chọn cụ thể.

## Điểm cần owner thống nhất

Task Track B mô tả việc dùng một risk layer chung. Code hiện chỉ có
`risk_flags` trong shared schema, chưa có risk layer runtime. B6 là yêu cầu
tương lai; không thêm hoặc giả định risk engine trong lần tổ chức thư mục này.

## Ownership và roadmap

Phân công tổng thể, dependency graph, execution gates và các task dùng chung
nằm ở [`docs/tasks/track-b-vlm.md`](tasks/track-b-vlm.md). Kế hoạch Track A nằm
riêng tại [`docs/tasks/track-a-classic.md`](tasks/track-a-classic.md).
