# Track B VLM

**Owner:** Thành viên B — VLM/integration.

Thư mục này giữ toàn bộ phần việc Track B. Chuẩn bị input tài liệu, prompt,
adapter, parse/validate, evidence mapping và runner nằm trong `src/`; CLI nằm
trong `scripts/`. Model chưa được chọn, inference hiện ở trạng thái
`SCAFFOLD`.

- Mã nguồn: `src/docai/track_b/parser.py`
- CLI: `scripts/run.py`
- Task: [`docs/tasks/track-b-vlm.md`](../../docs/tasks/track-b-vlm.md)
- Contract chung: [`backend/shared/src/docai/shared/schema.py`](../shared/src/docai/shared/schema.py)
- Frontend mirror: [`frontend/src/types/document.ts`](../../frontend/src/types/document.ts)
- Lịch sử của owner: [`CHANGELOG.md`](CHANGELOG.md)

Phối hợp với Track A và shared/Product Engineering trước khi đổi schema hoặc
API. Research cần prompt/model metadata và mapping raw-to-validated khi có
inference.

Static syntax check, chỉ chạy khi task cho phép:

```powershell
python -m compileall backend/track-b/src backend/track-b/scripts
```
