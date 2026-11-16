# Track A Classic

**Owner:** Thành viên A — AI/ML/DL.

Thư mục này giữ toàn bộ phần việc Track A. Layout detection, OCR, KIE, mapping
Invoice/Contract và runner nằm trong `src/`; CLI nằm trong `scripts/`. Model và
checkpoint chưa được chọn, inference hiện ở trạng thái `SCAFFOLD`.

- Mã nguồn: `src/docai/track_a/pipeline.py`
- CLI: `scripts/run.py`
- Task: [`docs/tasks/track-a-classic.md`](../../docs/tasks/track-a-classic.md)
- Contract chung: [`backend/shared/src/docai/shared/schema.py`](../shared/src/docai/shared/schema.py)
- Frontend mirror: [`frontend/src/types/document.ts`](../../frontend/src/types/document.ts)
- Lịch sử của owner: [`CHANGELOG.md`](CHANGELOG.md)

Phối hợp với Track B và shared/Product Engineering trước khi đổi schema hoặc
API. Research cần diagnostic theo stage khi pipeline có runtime.

Static syntax check, chỉ chạy khi task cho phép:

```powershell
python -m compileall backend/track-a/src backend/track-a/scripts
```
