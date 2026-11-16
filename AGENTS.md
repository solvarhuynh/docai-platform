# Hướng dẫn AI agent — repository DocAI

File này là hướng dẫn gốc cho mọi AI agent làm việc trong repository. Đọc hết
file này và `README.md` trước khi sửa. Sau đó đọc đúng tài liệu kiến trúc,
workstream và source/test liên quan trực tiếp đến task. Nếu có `AGENTS.md` trong
thư mục con về sau, hãy đọc cả file đó; hướng dẫn gần file đang sửa nhất bổ sung
hoặc giới hạn hướng dẫn gốc.

Tài liệu này mô tả **repository hiện có**, không biến kế hoạch thành tính năng
đã làm. Khi source và tài liệu không khớp, kiểm tra code/test trước, ghi nhận
mâu thuẫn và sửa tài liệu phù hợp trong phạm vi được giao.

## 1. DocAI giải quyết vấn đề gì?

DocAI là nền tảng Document Intelligence thử nghiệm cho hai sản phẩm ngang hàng:

- **Invoice Intelligence:** đọc Invoice/Receipt để tìm bên bán, ngày, thuế,
  tổng tiền, dòng hàng và thông tin cần người dùng kiểm tra.
- **Contract Intelligence:** tìm metadata và điều khoản hợp đồng, giữ nội dung
  clause cùng nguồn/trang để hỗ trợ rà soát.

Invoice không phải sản phẩm chính còn Contract là phần phụ. Cả hai processing
Track đều phải hướng đến cả hai domain. Taxonomy, model, prompt và metric có thể
khác theo domain.

Đường đi mục tiêu của sản phẩm:

```text
Người dùng
  → React + TypeScript + Vite
  → HTTP/REST/JSON
  → FastAPI + Python
  → Track A hoặc Track B
  → UnifiedDocumentOutput
  → Risk/Evidence để người dùng rà soát
```

Research & Evaluation chạy song song trên kết quả inference thật và ground
truth đã xác minh. Product giúp người dùng xử lý tài liệu; Research đo chất
lượng, lỗi, độ bền, evidence, latency và cost. Fixture/mock chỉ kiểm tra hành
vi deterministic, không phải kết quả sản phẩm hay benchmark.

## 2. Các khái niệm không được dùng lẫn nhau

- **Domain task:** công việc theo nghiệp vụ, ví dụ Invoice field extraction hoặc
  Contract clause extraction.
- **Track:** hướng xử lý tài liệu. Track A là Classic nhiều stage; Track B là
  VLM-native.
- **Model:** checkpoint hoặc dịch vụ cụ thể chạy ở một hay nhiều stage. Một
  Track có thể chứa nhiều model/candidate.
- **Pipeline:** các bước nối từ input qua preprocessing/inference/mapping đến
  output.
- **Adapter:** lớp chuyển giao diện chung của Track sang API/model cụ thể.
- **Ground truth:** annotation tham chiếu được xác minh để đo kết quả.
- **Fixture:** input/output deterministic phục vụ test; không đại diện dữ liệu
  thật hoặc benchmark.

Không mặc định Track A là một model, Track B là một model, hoặc mỗi Track chỉ
phục vụ một domain. Không mặc định một model bắt buộc xử lý tốt cả Invoice và
Contract.

## 3. Hai processing Track

### Track A — Classic multi-stage

Luồng dự kiến:

```text
Document/pages → Layout Detection → OCR → KIE
               → Invoice fields hoặc Contract clauses/evidence
               → UnifiedDocumentOutput
```

OCR (Optical Character Recognition) đọc chữ trong ảnh và giữ vị trí của chữ.
KIE (Key Information Extraction) gán ý nghĩa nghiệp vụ cho chữ/token đó. Track
này có thể dùng model riêng cho layout, OCR và KIE. Model/checkpoint production
chưa được chọn; các lớp hiện có là scaffold, inference method chưa triển khai.

### Track B — VLM-native

Luồng dự kiến:

```text
Document/pages → chuẩn bị input và prompt theo domain
               → VLM candidate → parse → validate → evidence mapping
               → UnifiedDocumentOutput
```

VLM (Vision-Language Model) nhận ảnh/tài liệu và instruction để tạo kết quả có
cấu trúc. “Single-pass” chỉ mô tả phía model; chuẩn bị input, chunking, parsing,
validation, retry và mapping vẫn là các bước riêng. PaddleOCR-VL, dots.ocr hoặc
model khác chỉ là candidate cho tới khi có quyết định dựa trên license, dữ liệu,
baseline, chất lượng và tài nguyên. Inference/adapter thật hiện chưa có.

### Shared contract

Python source of truth hiện là
`backend/shared/src/docai/shared/schema.py`. Browser mirror là
`frontend/src/types/document.ts`. Thay đổi contract phải xem xét cả hai phía,
backward compatibility và owner của hai Track.

`UnifiedDocumentOutput` hiện gồm `document_type`, `fields`,
`overall_confidence`, `risk_flags`, optional `execution_time_ms` và
`pipeline_track`, cùng `metadata`. Mỗi `ExtractedField` có value, confidence,
page, optional box và raw text. Schema kiểm tra cấu trúc/type/range; nó không
xác nhận nội dung đúng với tài liệu.

Evidence hiện còn hạn chế: box/page/raw text ở field. Chưa có Contract span model
riêng và chưa có risk engine runtime. Không tự tạo box, page, quote, highlight,
risk hoặc confidence nếu engine không cung cấp.

## 4. Cấu trúc repository hiện tại

```text
.
├── AGENTS.md                         Hướng dẫn gốc cho agent
├── README.md                         Giới thiệu, quick start, API và link docs
├── pyproject.toml                    Python package/dependencies/build config
├── requirements.txt                  Python dependency install list
├── docker-compose.yml                Cấu hình chạy API local bằng Docker
├── backend/
│   ├── shared/src/docai/shared/
│   │   ├── api.py                    FastAPI app, health và parse routes
│   │   ├── config.py                 Settings API hiện tại
│   │   ├── schema.py                 Pydantic shared contract
│   │   └── __init__.py
│   ├── track-a/
│   │   ├── src/docai/track_a/
│   │   │   ├── pipeline.py           Layout/OCR/KIE scaffold và geometry utility
│   │   │   └── __init__.py
│   │   ├── scripts/run.py            CLI scaffold, không chạy inference
│   │   ├── README.md                 Điểm bắt đầu của owner Track A
│   │   └── CHANGELOG.md              Lịch sử thay đổi riêng của owner A
│   └── track-b/
│       ├── src/docai/track_b/
│       │   ├── parser.py             Prompt/JSON mapping scaffold; chưa gọi model
│       │   └── __init__.py
│       ├── scripts/run.py            CLI scaffold, không chạy inference
│       ├── README.md                 Điểm bắt đầu của owner Track B
│       └── CHANGELOG.md              Lịch sử thay đổi riêng của owner B
├── frontend/
│   ├── package.json                  React/Vite scripts và dependencies
│   ├── vite.config.ts                Vite/dev proxy configuration
│   └── src/
│       ├── main.tsx, App.tsx         Browser entry và app shell
│       ├── types/document.ts         TypeScript mirror của shared schema
│       ├── services/api.ts           Health check và parse API client
│       ├── pages/                    Home, Invoice, Contract, Research
│       ├── components/               Shared UI components/placeholders
│       └── styles.css                Giao diện hiện tại
├── tests/
│   ├── conftest.py                   Shared test setup
│   ├── unit/                         Config và schema tests
│   └── integration/                  API route tests
├── data/
│   ├── raw/                          Vị trí dữ liệu nguồn; hiện chỉ placeholder
│   └── processed/                    Vị trí dữ liệu đã xử lý; hiện placeholder
└── docs/
    ├── architecture.md              Kiến trúc và cây thư mục
    ├── how-to-run.md                Hướng dẫn chạy chi tiết
    ├── processing-tracks.md         Giải thích hai hướng xử lý
    └── tasks/
        ├── track-a-classic.md        Task plan Track A
        └── track-b-vlm.md            Track B, master plan và task dùng chung
```

`scripts/` ở mỗi Track chỉ nhận argument, gọi package và trình bày kết quả.
Reusable logic thuộc package `src/` của owner. `backend/shared/` chứa API,
config và schema dùng chung. `tests/`, frontend, data policy, packaging, root
configuration và docs là shared. Không chuyển shared schema/API tests vào một
Track chỉ vì test nhắc đến Track đó.

`notebooks/`, Modal, report artifacts và một số tài liệu lịch sử có thể xuất
hiện trong lịch sử hoặc môi trường local nhưng không phải runtime source hiện
hành. Không dựa vào chúng để khẳng định có data/model/deployment. `GUIDE.md` là
workbook local không canonical; dùng README, docs và file này làm hướng dẫn hiện
hành. `.cursor/rules/` đã được repository owner chủ động xóa; không tự khôi phục.

## 5. Ownership và ranh giới làm việc

Task-level owner/reviewer, dependency, gate và roadmap nằm trong
[`docs/tasks/track-b-vlm.md`](docs/tasks/track-b-vlm.md), phần “Điều phối chung
DocAI”. Đọc task plan Track A/B tương ứng trước khi làm.

- **Thành viên A — Track A:** Layout, OCR, token/box, KIE, Invoice/Contract
  mapping và runner/diagnostic của Track A.
- **Thành viên B — Track B:** page/input preparation tại ranh giới VLM, prompt,
  adapter nhiều candidate, parse/validation, evidence mapping, reliability và
  runner của Track B.
- **Data Foundation:** Thành viên B dẫn dắt acquisition plan, integrity,
  annotation mapping, split và quality report; A review. Data owner không viết
  model logic.
- **Product API/integration:** Thành viên B dẫn dắt FastAPI upload/orchestration
  và shared integration; A review interface.
- **React frontend:** owner chưa được quyết định trong repo. Không tự gán người;
  PE2, PE5–PE7 và E2E UI cần quyết định của nhóm.
- **Shared schema:** semantics thống nhất bởi hai Track; một primary implementer
  cho mỗi thay đổi và Track owner còn lại review. Không thay schema đơn phương.
- **Research:** B dẫn dắt protocol/data/experiment plumbing; A review và dẫn dắt
  phân tích model/evidence ở RE7. Mỗi task có một primary owner cụ thể.

Track A không phụ thuộc implementation nội bộ Track B và ngược lại. Tích hợp
qua shared schema và runner boundary đã review. Không để task “Both members”
thay cho primary owner.

## 6. Trạng thái thực tế — không phóng đại

- Shared Pydantic schema/config: baseline nhỏ; không phải contract đã bao phủ
  mọi nhu cầu evidence của Contract.
- `GET /health`: có implementation.
- `POST /parse/classic` và `POST /parse/vlm`: route tồn tại nhưng trả `501`.
- Track A `pipeline.py`: có class/layout utility và polygon-to-box conversion;
  các inference methods ném `NotImplementedError`.
- Track B `parser.py`: tạo prompt đơn giản và có JSON-to-Pydantic helper;
  `parse()` chưa gọi model, adapter/provider chưa có.
- React Invoice/Contract pages: placeholder. Research page là planned. API client
  tồn tại nhưng pages chưa nối extraction thật.
- Risk: có type `RiskFlag`/`risk_flags`; chưa có risk rule runtime.
- Evidence: field-level box/page/raw text; chưa có Contract span model riêng.
- Data: raw/processed dirs chỉ có placeholder; chưa có dataset/ground truth được
  kiểm tra.
- Evaluation: chưa có evaluation package/metric hoặc benchmark thật.
- Model/checkpoint/provider: chưa chọn; không inference thật.
- Test tree: shared config/schema/API route tests; chưa có Track-specific suite.

Dùng các nhãn sau cho tài liệu và bàn giao:

- `IMPLEMENTED`: hành vi có code và bằng chứng kiểm tra phù hợp.
- `BASELINE`: nền tảng nhỏ đã chạy/kiểm tra trong phạm vi nêu rõ.
- `SCAFFOLD`: interface, placeholder hoặc utility nhưng runtime chính chưa xong.
- `PLANNED`: mới nằm trong kế hoạch.
- `NOT SELECTED`: chưa quyết định model/provider/candidate.
- `BLOCKED`: prerequisite cụ thể chưa đạt.
- `NOT RUN`: validation/runtime chưa chạy.

Schema-valid không có nghĩa factual correctness. Compile/build pass không có
nghĩa model inference hay benchmark pass. Fixture pass chỉ chứng minh contract
hoặc logic fixture.

## 7. Nguồn tài liệu canonical

Đọc tài liệu phù hợp, tránh tạo bản sao cạnh tranh:

- Tổng quan, setup nhanh, API: `README.md`.
- Cách chạy đầy đủ: [`docs/how-to-run.md`](docs/how-to-run.md).
- Kiến trúc/cây repo: [`docs/architecture.md`](docs/architecture.md).
- Track, model, pipeline: [`docs/processing-tracks.md`](docs/processing-tracks.md).
- Ownership, dependency, gate, roadmap, Track B và task dùng chung:
  [`docs/tasks/track-b-vlm.md`](docs/tasks/track-b-vlm.md).
- Kế hoạch Track A: [`docs/tasks/track-a-classic.md`](docs/tasks/track-a-classic.md).
- Chi tiết code owner: `backend/track-a/README.md` và
  `backend/track-b/README.md`.
- Trạng thái lịch sử: `backend/track-a/CHANGELOG.md` và
  `backend/track-b/CHANGELOG.md`.

Nếu canonical docs mâu thuẫn, không tự chọn theo sở thích: ghi lại chính xác
hai claim, kiểm tra source/test, rồi sửa đúng tài liệu trong phạm vi hoặc báo
blocker nếu cần quyết định của owner.

## 8. Cách bắt đầu và triển khai task

1. **Kiểm tra trạng thái trước:** chạy `git branch --show-current` và
   `git status --short --branch`. Ghi nhận file đã sửa/xóa/untracked. Không reset,
   stash, checkout, clean, xóa hoặc ghi đè thay đổi người dùng.
2. **Chốt phạm vi:** xác định task ID, primary owner, reviewer, input, output,
   dependency/gate, validation và điều kiện dừng từ task plan.
3. **Đọc code thật:** dùng `rg --files`, `rg` và đọc file/test liên quan. Không
   suy ra implementation từ README, tên thư mục hay task plan.
4. **Tìm đường dẫn hiện có trước:** ưu tiên sửa in-place. Không tạo `copy`,
   `new`, `latest`, `final2` hoặc nguồn dữ liệu trùng.
5. **Phân loại thay đổi:** xác định thuộc Track A, Track B, shared API/schema,
   frontend, data, research hay docs. Chỉ sửa phạm vi đã giao; khi tạo/move file,
   kiểm tra và cập nhật reference cũ có liên quan.
6. **Làm theo gate:** có thể dùng fixture/mock cho contract work nếu task cho
   phép. Không đi qua gate bị FAIL/BLOCKED và không coi mock là real inference.
7. **Bảo toàn trạng thái:** stage path cụ thể; không dùng `git add .`/`-A` mặc
   định. Không commit/push trừ khi user yêu cầu rõ hoặc workflow yêu cầu.
8. **Bàn giao:** nêu output/file, trạng thái, validation kèm lệnh/kết quả, giới
   hạn, downstream owner/task và blocker.

Nếu shared schema, API semantics, model choice, evaluation protocol hoặc paid
resource cần thay đổi mà chưa có review/approval theo task plan, dừng phần phụ
thuộc, ghi proposal và tiếp tục phần độc lập an toàn.

## 9. Quy tắc implementation

- Python reusable logic nằm trong `backend/shared/src/` hoặc `backend/track-*/src/`
  theo ownership. CLI nằm trong `backend/track-*/scripts/`, chỉ parse arguments,
  gọi package và trình bày output.
- Import qua namespace `docai.*`; không dùng `sys.path.append/insert`.
- FastAPI là business backend duy nhất. Node.js chỉ phục vụ React/Vite tooling;
  không thêm Express/NestJS hoặc model logic vào browser.
- Route điều phối qua runner contract, không chứa prompt/provider/model internals.
- Invoice và Contract dùng taxonomy riêng trong outer output phù hợp. Không xem
  Contract là Invoice dài hơn; không ép clause thành scalar ngắn.
- Không tự repair response thành giá trị nghe có vẻ hợp lý. Parse success,
  schema validation và factual correctness là ba việc khác nhau.
- Không log API key, credential, toàn bộ tài liệu nhạy cảm hoặc raw response nhạy
  cảm. Chỉ lưu metadata tối thiểu và đã redaction.
- Không train/fine-tune, tải weights/dataset, gọi paid API/Modal GPU hoặc deploy
  nếu task chưa cho phép rõ. Không thêm framework/database/service để làm repo
  phức tạp hơn khi chưa có requirement.
- Không dùng test split để chọn model/threshold/prompt hoặc làm fine-tuning.
- Giữ backward compatibility ở API/public boundary. Nếu breaking change không
  tránh được, ghi consumer bị ảnh hưởng và yêu cầu cross-owner review.

## 10. Dữ liệu, model và artifact

Giữ riêng các loại artifact: raw dataset, processed dataset, annotation/ground
truth, test fixture và model output. Mỗi claim về dataset/model phải truy được
source, version và trạng thái.

- Không commit `.env`, secret, credential, dataset nặng, checkpoint, weight,
  `*.pt`, `*.safetensors`, `models/` hoặc `checkpoints/`.
- Tôn trọng `.gitignore`; kiểm tra `git status` để không đưa artifact local vào
  thay đổi.
- Không nâng dataset thành `DOWNLOADED` nếu file chưa có; không ghi
  `INTEGRITY VERIFIED` nếu chưa có manifest/checksum kiểm tra.
- Không sửa raw annotation để làm vừa taxonomy. Mapping phải giữ raw label và
  giải thích nhãn chưa map.
- Trước khi xóa artifact, xác minh đường dẫn tuyệt đối nằm trong repo và file
  không phải dữ liệu người dùng. Preserve file ignored/untracked không rõ nguồn.

## 11. Tài liệu và ngôn ngữ làm việc

- Tài liệu hướng dẫn trong repo viết tiếng Việt UTF-8 có dấu; giữ thuật ngữ
  tiếng Anh cần thiết và giải nghĩa ở lần dùng đầu.
- Viết cho hai người có chuyên môn khác nhau: Thành viên A mạnh AI/ML/DL;
  Thành viên B mạnh Data Engineering và đang phát triển AI/ML. Giải thích vấn đề,
  lý do, input, output và cách kiểm tra thay vì liệt kê jargon.
- Mỗi chủ đề có một nguồn canonical. Tạo link thay vì copy cùng nội dung sang
  nhiều file. Khi di chuyển/xóa tài liệu, sửa mọi link và đường dẫn đang dùng.
- Phân biệt rõ hiện trạng, kế hoạch, giả thuyết, candidate và quyết định.
- Mỗi task plan phải nêu vấn đề, owner/reviewer, dependency, input, bước làm,
  file, output, acceptance, validation, out of scope, handoff và status.
- Không ghi log như đã hoàn thành tính năng nếu chỉ cập nhật plan hoặc audit.

## 12. Validation và cách chạy

Chọn kiểm tra nhỏ nhất có thể chứng minh phần vừa đổi. Không mặc định chạy model,
GPU, Modal hoặc dịch vụ trả phí.

### Python

Từ thư mục gốc, cài editable package cùng API dependencies:

```powershell
python -m pip install -e ".[api]"
uvicorn docai.shared.api:app --reload --host 127.0.0.1 --port 8000
```

`pyproject.toml` khai báo package roots ở `backend/shared/src`,
`backend/track-a/src`, `backend/track-b/src`. Test Python hiện có:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
npm run build
```

Frontend gọi API qua `/api` mặc định theo Vite proxy; `VITE_API_BASE_URL` có
thể đổi base URL. Xem `docs/how-to-run.md` trước nếu task cần quy trình chi tiết.

### Docker

```powershell
docker compose config
docker compose up --build
```

Chỉ dùng lệnh liên quan đến scope. Nếu task hoặc user cấm test/build thì không
chạy. Báo `PASS`, `FAIL`, `NOT RUN` hoặc `BLOCKED` kèm bằng chứng; không viết
“all tests passed” nếu không chạy.

## 13. Git, changelog và bàn giao

- Làm trên branch phù hợp; không commit trực tiếp vào `main` theo workflow repo.
- Xem diff/status trước khi stage; stage đúng path task đã sửa.
- Commit message nếu được yêu cầu: `feat(scope)`, `fix(scope)`, `docs(scope)`,
  `refactor(scope)`, `test(scope)` hoặc `chore(scope)`.
- Chỉ commit/push khi user yêu cầu rõ hoặc workflow hiện hành quy định.
- Mỗi thành viên ghi lịch sử thay đổi trong CHANGELOG của mình tại
  `backend/track-a/CHANGELOG.md` hoặc `backend/track-b/CHANGELOG.md`. Không tạo
  thư mục log chung hoặc changelog thứ hai.
- Không sửa/xóa lịch sử cũ. Nếu changelog/log đang bị xóa hoặc thay đổi sẵn,
  không tự khôi phục/ghi đè; báo tình trạng trong handoff.
- Local-only audit không đổi project không được mô tả như feature đã hoàn tất.

Bàn giao cuối cần nêu: thay đổi gì và vì sao; file nào tác động; validation nào
PASS/FAIL/NOT RUN; phần còn SCAFFOLD/PLANNED/NOT SELECTED/BLOCKED; có dùng model,
data, API, GPU hay không; và task/owner an toàn tiếp theo.

## 14. Khi nào phải dừng

Dừng phần bị ảnh hưởng và báo rõ khi:

- nguồn canonical có mâu thuẫn làm thay đổi semantics;
- working tree có thay đổi liên quan có nguy cơ bị ghi đè;
- sửa shared schema/API/risk/evaluation contract mà thiếu review bắt buộc;
- model, checkpoint, credential, dataset, compute hoặc provider chưa được duyệt;
- yêu cầu metric nhưng thiếu real output, ground truth hoặc protocol;
- chỉ có thể làm task “pass” bằng cách giảm requirement hoặc sửa ngoài scope;
- target xóa/di chuyển file chưa xác định chắc chắn.

Tiếp tục các phần độc lập không gặp blocker và mô tả chính xác phần nào đang
chờ quyết định.
