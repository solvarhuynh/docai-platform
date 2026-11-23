<p align="center">
  <img src="frontend/banner.svg" alt="DocAI — Dual-Track Document Information Extraction" width="50%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&amp;logo=python&amp;logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=flat-square&amp;logo=fastapi&amp;logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18_%2B_Vite-61DAFB?style=flat-square&amp;logo=react&amp;logoColor=20232A" alt="React 18 + Vite">
  <img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square" alt="Pydantic v2">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&amp;logo=docker&amp;logoColor=white" alt="Docker Compose">
  <img src="https://img.shields.io/badge/Status-Scaffold-F59E0B?style=flat-square" alt="Status: Scaffold">
</p>

<p align="center"><strong>Nền tảng thử nghiệm trích xuất thông tin tài liệu (Invoice &amp; Contract) theo hai kiến trúc độc lập — Classic Multi-Stage và VLM-Native — dùng chung một API &amp; Output Contract.</strong></p>

<p align="center">
  <a href="#tổng-quan-dự-án">Tổng quan</a> ·
  <a href="#kiến-trúc--hai-track-xử-lý">Hai track xử lý</a> ·
  <a href="#cấu-trúc-repository">Cấu trúc repo</a> ·
  <a href="#chạy-local-quick-start">Chạy local</a> ·
  <a href="#hợp-đồng-api">API contract</a> ·
  <a href="#kiểm-thử--tài-liệu">Kiểm thử &amp; Tài liệu</a>
</p>

---

## Tổng quan dự án

**DocAI** là dự án thử nghiệm và so sánh hai hướng tiếp cận AI để trích xuất dữ liệu có cấu trúc từ **Invoice** (hóa đơn) và **Contract** (hợp đồng). Hệ thống dùng **FastAPI** làm lớp điều phối thống nhất và giao diện **React + TypeScript + Vite** để thao tác trên cùng một schema đầu ra [`UnifiedDocumentOutput`](src/docai/shared/schema.py).

- **Track A — Classic Multi-Stage:** `tài liệu → layout → OCR → KIE → UnifiedDocumentOutput`
- **Track B — VLM-Native:** `tài liệu + prompt → VLM → parse/validate → UnifiedDocumentOutput`

> [!NOTE]
> **Trạng thái hiện tại:** Cả **Track A** và **Track B** đều đang ở mức **scaffold**. Chưa chọn model/checkpoint chính thức và hai route parse (`/parse/classic`, `/parse/vlm`) hiện trả về `501 Not Implemented`. Prompt hoặc schema hợp lệ không được xem là bằng chứng inference đã chạy.

---

## Kiến trúc & Hai track xử lý

```mermaid
flowchart LR
    DOC["Tài liệu đầu vào<br/>(Invoice / Contract)"] --> API["FastAPI Service<br/>src/docai/api.py"]
    API -->|"/parse/classic"| TA["Track A · Classic<br/>Layout → OCR → KIE"]
    API -->|"/parse/vlm"| TB["Track B · VLM<br/>Prompt → VLM → Parser"]
    TA --> SCHEMA["UnifiedDocumentOutput<br/>src/docai/shared/schema.py"]
    TB --> SCHEMA
    SCHEMA --> UI["React + TypeScript UI<br/>frontend/"]
```

| Tiêu chí | Track A — Classic | Track B — VLM |
| --- | --- | --- |
| **Chiến lược** | Đa tầng tách biệt: Layout Detection → OCR → Key Information Extraction | Trực tiếp từ ảnh/PDF tài liệu + prompt có cấu trúc |
| **Module Python** | [`src/docai/track_a/`](src/docai/track_a/) | [`src/docai/track_b/`](src/docai/track_b/) |
| **CLI kiểm tra** | `python -m docai.track_a` | `python -m docai.track_b` |
| **API Route** | `POST /parse/classic` | `POST /parse/vlm` |
| **Đầu ra chuẩn** | `UnifiedDocumentOutput` | `UnifiedDocumentOutput` |
| **Tình trạng** | Scaffold (`501`) | Scaffold (`501`) |

`track_a` và `track_b` chỉ được import `docai.shared`, không import lẫn nhau.
Chỉ bổ sung phần hỗ trợ mới khi đã chọn model và có đầu việc cụ thể.

---

## Cấu trúc repository

```text
.
├── README.md, AGENTS.md, CODEOWNERS
├── pyproject.toml, requirements.txt, docker-compose.yml, .gitignore
├── src/docai/
│   ├── __init__.py, api.py
│   ├── shared/              Schema và config dùng chung
│   ├── track_a/             Pipeline và CLI của Thành viên A
│   └── track_b/             Parser và CLI của Thành viên B
├── tests/
│   ├── conftest.py, shared/
│   ├── track_a/
│   └── track_b/
├── notebooks/               01-eda.ipynb cũ; track_a/, track_b/
├── data/                    raw/, processed/ (chỉ .gitkeep trong Git)
├── frontend/                React + TypeScript + Vite
└── docs/
    ├── architecture.md
    └── tasks/               shared.md, track-a.md, track-b.md
```

`notebooks/01-eda.ipynb` còn tham chiếu package cũ và chưa chạy được theo source hiện tại.

---

## Chạy local

### 1. Cài đặt môi trường & chạy Backend API

Yêu cầu **Python 3.10+**. Từ thư mục gốc của repository:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn docai.api:app --reload --host 127.0.0.1 --port 8000
```

Sau khi khởi động, kiểm tra service tại `http://127.0.0.1:8000/health` hoặc tài liệu Swagger tại `http://127.0.0.1:8000/docs`.

### 2. Chạy Frontend (trong terminal khác)

Yêu cầu **Node.js 18+**:

```powershell
cd frontend
npm install
npm run dev
```

Vite chuyển các request `/api` tới FastAPI ở cổng `8000`.

### 3. Chạy bằng Docker Compose (tùy chọn)

```powershell
docker compose up --build
```

### 4. Chạy CLI kiểm tra scaffold

Các lệnh CLI hiện chỉ kiểm tra tính hợp lệ của tham số đầu vào và in thông tin scaffold (chưa chạy inference model):

```powershell
python -m docai.track_a --image path/to/document.jpg
python -m docai.track_b --image path/to/document.jpg --type invoice
```

---

## API

| Endpoint | Method | Chức năng | Trạng thái hiện tại |
| --- | --- | --- | --- |
| `/health` | `GET` | Kiểm tra trạng thái hoạt động và phiên bản service | `200 OK` |
| `/parse/classic` | `POST` | Trích xuất tài liệu theo pipeline Track A (`file`, `document_type`) | `501 Not Implemented` |
| `/parse/vlm` | `POST` | Trích xuất tài liệu theo pipeline Track B (`file`, `document_type`) | `501 Not Implemented` |

> [!IMPORTANT]
> **Đồng bộ Schema:** Mọi thay đổi đối với [`src/docai/shared/schema.py`](src/docai/shared/schema.py) bắt buộc phải được cập nhật tương ứng trong [`frontend/src/types/document.ts`](frontend/src/types/document.ts) và được cả hai Track review.

---

## Kiểm thử & Tài liệu

Chạy test Python hiện có sau khi cài package:

```powershell
pytest -q
```

### Tài liệu tham khảo trong repo

- [Kiến trúc hệ thống và hai processing Track](docs/architecture.md)
- [Kế hoạch chung, ownership và workstream Data/Product/Research](docs/tasks/shared.md)
- [Kế hoạch Track A](docs/tasks/track-a.md)
- [Kế hoạch Track B](docs/tasks/track-b.md)
- [Quy tắc repository (`AGENTS.md`)](AGENTS.md)

---

## Giấy phép

Phát hành theo giấy phép **Apache-2.0**.
