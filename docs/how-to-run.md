# Chạy DocAI ở local

## Cài đặt

Tại thư mục gốc:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Khởi động API

```powershell
uvicorn docai.shared.api:app --reload --host 127.0.0.1 --port 8000
```

`GET /health` kiểm tra service. `POST /parse/classic` và `POST /parse/vlm`
hiện trả `501` vì model inference chưa được triển khai.

## Khởi động frontend

Mở terminal khác:

```powershell
cd frontend
npm install
npm run dev
```

Vite proxy `/api` tới FastAPI ở port `8000`.

## CLI scaffold

```powershell
python backend/track-a/scripts/run.py --image path/to/document.jpg
python backend/track-b/scripts/run.py --image path/to/document.jpg --type invoice
```

Hai CLI xác nhận đường dẫn và hiển thị thông tin scaffold. Chúng chưa gọi OCR,
LayoutLM hoặc VLM.

## Test

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```
