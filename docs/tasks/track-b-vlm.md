# Kế hoạch Track B VLM và phân công chung DocAI

Tài liệu này là master plan về ownership, thứ tự/gates và task chi tiết của Track B cùng các workstream dùng chung. Kế hoạch Track A riêng tại [track-a-classic.md](track-a-classic.md).

## Điều phối chung DocAI


### Tài liệu này dùng để làm gì?

Đây là bản phân công tổng thể. Mỗi workstream có một kế hoạch chi tiết liên
kết bên dưới. Không xem kế hoạch là bằng chứng code, dataset, model hay
benchmark đã tồn tại.

DocAI là Document Intelligence Platform cho hai domain ngang hàng: Invoice
Intelligence và Contract Intelligence. Track là hướng xử lý, model là một
thành phần cụ thể trong hướng đó, domain task là việc cần giải quyết, còn
pipeline là chuỗi bước từ tài liệu đến output. Một Track có thể chứa nhiều
model; không mặc định một Track tương đương một model hoặc một domain.

Một số từ dùng trong kế hoạch: **pretrained model** là model đã được huấn luyện
trước; **fine-tuning** là tiếp tục huấn luyện có giám sát cho domain/task cụ thể;
**adapter** là lớp chuyển giao diện chung sang từng model/provider;
**ground truth** là đáp án tham chiếu đã được kiểm tra; **fixture** là mẫu test
deterministic, không đại diện benchmark; **manifest** là danh sách file/metadata
để truy xuất dataset; **data split** là phần train/validation/test và
**leakage** là thông tin cùng nguồn lọt qua các split làm kết quả cao giả.

```text
Người dùng → React/TypeScript/Vite → FastAPI/Python
           → Track A hoặc Track B → UnifiedDocumentOutput
           → Risk/Evidence → người dùng review
                         ↘ Research & Evaluation
```

Research đo output thật so với ground truth. Research không thay thế luồng sản
phẩm và không được dùng placeholder hoặc fixture như kết quả benchmark.

### Trạng thái code và dữ liệu tại thời điểm audit

| Khu vực | Bằng chứng trong repo | Trạng thái trung thực |
|---|---|---|
| Shared schema | `backend/shared/src/docai/shared/schema.py`; Pydantic models và kiểm tra BoundingBox | `BASELINE`; chưa có evidence/span model riêng cho Contract |
| FastAPI | `backend/shared/src/docai/shared/api.py`; `/health` và hai route parse | `/health` có implementation; parse routes ném `501`, nên extraction là `SCAFFOLD` |
| Track A | `backend/track-a/src/docai/track_a/pipeline.py`; có khung Layout/OCR/KIE và polygon-to-box utility | `SCAFFOLD`; inference chưa triển khai, checkpoint `NOT SELECTED` |
| Track B | `backend/track-b/src/docai/track_b/parser.py`; prompt builder và JSON-to-Pydantic mapping | `SCAFFOLD`; model adapter/inference chưa triển khai, model `NOT SELECTED` |
| Frontend | React pages, typed API client, Vite proxy | `SCAFFOLD`; Invoice/Contract là placeholder, Research page ghi `PLANNED`; chưa gọi extraction thật |
| Risk/Evidence | Schema có `risk_flags`, field có box/page/raw_text | Chưa có risk runtime trong code hiện tại; Contract span model chưa có |
| Data | `data/raw/` và `data/processed/` chỉ có `.gitkeep`; không thấy dataset | Chưa tải/chưa xác minh; chưa có ground truth trong repo |
| Evaluation | Chưa có evaluation package trong source hiện tại; chỉ có test schema/config/API routes | `PLANNED`; chưa có metric hoặc benchmark thật |
| Model/compute | Không thấy checkpoint hoặc cấu hình model được chọn | Candidate không được xem là quyết định; không có inference/paid compute trong audit |
| EDA/Modal artifacts | `notebooks/01-eda.ipynb` còn import `docai.data`/`docai.core.schema` đã bị xóa; `modal/` chỉ có `__pycache__`, không có deploy source | Notebook là scaffold cũ, không chạy được theo source hiện tại; không có Modal app/deployment implementation |

`tests/` có test dùng chung cho schema, config và đăng ký API routes. Không có
test suite riêng cho Track A/B trong cây source hiện tại. `GUIDE.md` là local
workbook không canonical và còn đường dẫn cũ; dùng tài liệu trong `docs/tasks/`,
`README.md`, `docs/architecture.md` và `AGENTS.md` làm nguồn hiện hành.

### Ai sở hữu phần nào?

| Workstream | Primary owner | Reviewer | Ranh giới |
|---|---|---|---|
| Track A Classic | Thành viên A | Thành viên B | Layout, OCR, KIE, mapping cả Invoice và Contract, runner và diagnostic theo stage |
| Track B VLM | Thành viên B | Thành viên A | Input ở VLM boundary, prompt, adapter nhiều candidate, parse/validate, mapping, reliability và runner |
| Data Foundation | Thành viên B | Thành viên A | Acquisition plan, integrity, annotation mapping, split, data contract và quality report; không viết model logic |
| Shared API/Product integration | Thành viên B | Thành viên A review interface | FastAPI upload/validation, orchestration, request lifecycle, tích hợp output và shared risk/evidence contract |
| React frontend | **Chưa được phân công** | Thành viên B review API integration; reviewer UI cần nhóm chỉ định | Không tự suy đoán người phụ trách. PE2, PE5–PE7 bị chặn cho đến khi nhóm quyết định owner |
| Shared schema | Thành viên B thực hiện thay đổi được duyệt | Thành viên A bắt buộc review | Hai thành viên thống nhất semantics; chỉ một người thực hiện mỗi thay đổi |
| Research & Evaluation | Thành viên B dẫn dắt protocol/data/experiment plumbing; Thành viên A dẫn dắt model-specific analysis ở RE7 | Người còn lại review theo từng task | Metric và kết luận tách riêng theo domain, Track và model candidate |

Mỗi task trong kế hoạch chi tiết chỉ có một primary owner. Reviewer không trở
thành đồng sở hữu mặc định. Track A không import model internals của Track B;
Track B không phụ thuộc implementation nội bộ của Track A. Cả hai chỉ tích hợp
qua shared contract và runner boundary đã review.

### Khái niệm phải giữ riêng

- **Track:** hướng tiếp cận xử lý, ví dụ Classic nhiều stage hoặc VLM-native.
- **Model:** checkpoint/provider cụ thể chạy trong một hay nhiều stage.
- **Domain task:** việc cần giải quyết như Invoice field extraction hoặc
  Contract clause extraction.
- **Pipeline:** các bước chuẩn bị, inference, mapping và validation nối thành
  luồng xử lý.

Track A có thể ghép nhiều model chuyên biệt. Track B cần adapter để thay/thử
nhiều VLM. Một VLM dùng được cho cả hai domain, mỗi domain dùng model riêng, hay
nhiều candidate theo domain đều là giả thuyết cần đánh giá, không phải quyết
định có sẵn.

### Các gate triển khai

```text
G0 Repository / ownership audit
  └─ PASS → G1 Shared contract proposal + data acquisition plan
               └─ PASS → Track A và Track B phát triển song song bằng fixture
                            ├─ A8 runner contract (mock) ─┐
                            └─ B9 runner contract (mock) ─┴→ G2
                                                               ↓
                                              G3 Product integration (mock)
                                                               ↓
                                                G4 E2E contract flow (mock)

G1 data plan → license-approved data → verified split/ground truth
G1 model strategy → selected/approved model/resource
                  └─ real Track runs + G4 → G5 Research evaluation → G6 report
```

| Gate | Prerequisite / validation | Điều kiện PASS và output | Owner / reviewer | Nếu FAIL |
|---|---|---|---|---|
| G0 — Audit | A0, B0, D0; rà path và status thật | Current tree, ownership, scaffold và blockers được ghi; không có path giả | B; A review | Sửa inventory; không bắt đầu task phụ thuộc path chưa xác minh |
| G1 — Shared proposal | A1, B1, PE1, PE10 proposals; D1 có thể chạy song song nhưng không chặn contract; fixtures deterministic | Input/output/error/evidence semantics và shared risk/evidence boundary được review; data source/license plan được ghi riêng | B điều phối; A review | Dừng thay đổi shared contract; ghi decision cần nhóm |
| G2 — Runner contracts | G1 PASS; Track owners dựng runner boundary/test doubles bằng taxonomy fixtures | A8 và B9 trả contract output/error bằng injected mock; không cần model selection, dataset download hoặc React owner; chưa claim inference | A cho A8; B cho B9; owner kia review | Sửa boundary trong Track; không chờ model selection để viết contract tests |
| G3 — Product integration (mock) | G2 PASS; PE1, PE3, PE4, API portion PE8; React owner chỉ cần trước UI integration | API gọi runner interface; mock result gắn test-only | B API; A review | Sửa API/runner integration; không route tới provider/model trực tiếp |
| G4 — E2E contract flow (mock) | G3 PASS; PE2, PE5, PE6, UI portion PE8, PE9 và React owner đã chỉ định | Upload → API → mock runner → schema → UI được kiểm tra cho hai domain/Track | B; React owner; A review | Chặn E2E UI; không gọi fixture là extraction thật |
| G5 — Real evaluation readiness | D2–D7, RE1–RE3; license/split/ground truth và model/resource được duyệt | Real runner output và protocol versioned; Invoice/Contract metric definitions sẵn | B; A review | Không chạy/công bố metric nếu data/model permission chưa đạt |
| G6 — Research result | G5 PASS; RE4–RE8; real runs được duyệt | Report tái lập theo domain/Track/model, latency/cost/failure; không fake | B tổng hợp; A review diễn giải model | Ghi `NOT RUN`/`BLOCKED`, không tuyên bố thắng-thua |

Fixtures cho phép hai track và Product Engineering làm contract/orchestration
trước khi có dataset. Chúng chỉ chứng minh deterministic behavior; không mở
G5/G6.

### Roadmap và tài liệu chi tiết

| Giai đoạn | Task | Mục tiêu |
|---|---|---|
| 0. Audit/ownership | A0, B0, PE1 | Inventory thực tế, boundary và quyền sở hữu |
| 1. Shared/data foundation | A1, B1, PE1, PE10; D1 chạy song song, D2 chỉ sau khi acquisition được cho phép | Contract và kế hoạch dữ liệu rõ trước khi phụ thuộc |
| 2. Song song theo track | A2–A7; B2–B8 bằng fixture; D2–D6 theo prereq data | Stage/prompt/adapter/mapping; dataset-specific mapping đợi D4, mock contract không đợi acquisition |
| 3. Runner contracts | A8–A9; B9–B10; D7 | Boundary/test pass với mocks; model selection/data thật vẫn độc lập |
| 4. Product mock integration | PE2–PE6, PE8–PE9 | Upload, API orchestration, workspaces và E2E contract flow; không phải real inference |
| 5. Research + Research UI | RE1–RE8, rồi PE7 | Real evaluation sau license, ground truth, model/resource approvals; UI chỉ đọc report đã review |

- [Track A Classic](track-a-classic.md)
- Task chi tiết D/PE/RE được mô tả ở phần “Workstreams dùng chung” phía dưới.

### Quy tắc model, dữ liệu và status

- Candidate hiện được nêu trong task không được xem là lựa chọn cuối. Ghi model
  card/candidate matrix gồm version/checkpoint, license, domain, input, resource,
  latency definition, output/evidence support và kết quả trên protocol chung.
- Chỉ chọn inference hay fine-tuning sau baseline, kiểm tra license/dữ liệu,
  compute, chi phí và lý do kỳ vọng có cải thiện. LoRA là một phương án, không
  phải yêu cầu mặc định. Không tải weight/dataset, gọi paid API/GPU hoặc train
  trong lần viết kế hoạch này.
- Tách `raw dataset`, `processed dataset`, `annotation/ground truth`, `fixture`
  và `model output` cả trong storage lẫn báo cáo.
- `IMPLEMENTED`: hành vi có code/evidence; `BASELINE`: nền nhỏ có kiểm tra và
  giới hạn; `SCAFFOLD`: interface/placeholder; `PLANNED`: chưa triển khai;
  `NOT SELECTED`: chưa quyết định candidate; `BLOCKED`: prerequisite chưa đạt.
- Task dùng status `NOT STARTED`, `IN PROGRESS`, `BLOCKED`, `SCAFFOLD`, `PASS`,
  `FAIL` hoặc `NOT RUN`. Chỉ dùng `PASS` khi có artifact/validation nêu trong
  task; không dùng “Done” thay evidence.

### Test và handoff

- Owner của module viết unit test cho transformations, errors, mapping và
  boundaries; tests shared schema/API vẫn ở `tests/`.
- Shared contract change yêu cầu Pydantic validation và cập nhật TypeScript
  mirror. Runner contract test dùng fixture có tên rõ là synthetic/deterministic.
- Data tests kiểm tra manifest, checksum, split integrity và mapping; không
  commit file dữ liệu thật.
- Product integration test kiểm tra request lifecycle và error response; E2E
  phải phân biệt test fixture với tài liệu người dùng.
- Research chỉ chạy metric khi có dataset/split/ground truth và protocol khóa.
  Ghi model/prompt/config version, input strategy, hardware, latency boundary,
  failures và các bước loại trừ tài liệu nhạy cảm.
- Handoff gồm output/path, status, test command + kết quả, known limitations,
  downstream owner/task và blocker. Không stage/commit/push trừ khi yêu cầu riêng.

### Thành viên B nên bắt đầu từ đâu?

1. B0/A0/D0 đã có audit snapshot trong tài liệu này; A review các path và status.
   Không coi audit đó là runtime validation.
2. Soạn đề xuất **A1/B1/PE1/PE10** song song: A định nghĩa stage contract, B định
   nghĩa adapter boundary, B điều phối API/error/output proposal. Sau đó A và
   Product Engineering review chéo để G1 không tạo interface vòng lặp.
3. Chốt **B1, PE1 và PE10** với A; chưa sửa schema nếu Contract evidence cần
   thay đổi. A1/B1/PE1 proposals có thể chuẩn bị song song; G1 review mới cho
   phép implementation phụ thuộc shared contract.
4. Làm **D1** song song để xác minh nguồn/license/access; không download. D2
   chỉ tiến khi nguồn/license được xác minh và acquisition được cho phép.
5. Sau G1, phát triển B2, B3, B5, B6 và phần API policy-compatible ở B8 bằng
   fixture. B7 dùng synthetic mapping cho mock, D4 cho dataset-specific mapping;
   B9 mock runner chờ B1–B3/B5–B8, không chờ B4 hoặc dataset acquisition; B4
   inference thật chờ candidate/data/resource approval. Không gọi inference thật.
6. Nhóm cần chỉ định React owner trước PE2, PE5–PE7 và E2E UI; backend PE3/PE4
   proposal có thể đi trước mà không giả định owner UI.

**Trạng thái audit task split:** hoàn thiện tài liệu theo snapshot code hiện có;
không phải xác nhận pipeline, model, dataset, sản phẩm hay benchmark đã PASS.

## Track B VLM — kế hoạch chi tiết


### Track B giải quyết việc gì?

Track B là hướng **VLM-native**: model nhận page/document cùng instruction rồi
tạo candidate response; adapter, parser, validation và mapping vẫn là các bước
riêng. Track B có thể thử nhiều VLM qua một adapter contract. Nó phải hướng tới
cả Invoice/Receipt và Contract; không mặc định một model tốt ngang nhau trên cả
hai domain.

```text
document/pages → input preparation → prompt theo domain
               → VLM candidate → parse → schema validation
               → Invoice fields hoặc Contract clauses/evidence
               → UnifiedDocumentOutput
```

**Primary owner:** Thành viên B — VLM/integration. **Reviewer:** Thành viên A.
Product Engineering review boundary; Research review candidate comparison.

### Audit code thật tại thời điểm viết kế hoạch

- `backend/track-b/src/docai/track_b/parser.py` có prompt đơn giản cho Invoice/
  Contract và `parse_raw_json_to_output` dùng JSON + Pydantic validation;
  `parse()` ném `NotImplementedError`.
- Constructor giữ `model_name` nhưng không có adapter/endpoint hoạt động.
- `backend/track-b/scripts/run.py` kiểm tra path, in prompt và ghi rõ inference
  chưa triển khai; script không gọi model.
- Shared output hiện ở `backend/shared/src/docai/shared/schema.py`.
- Không thấy model checkpoint, prompt version registry, dataset, real response,
  timeout/retry runtime hay Track B test suite. PaddleOCR-VL/dots.ocr là ví dụ
  candidate, không phải model đã được chọn.

### B0 — Audit repository và shared contract

- **Vấn đề / lý do:** Task cũ trỏ code/schema/API ở path đã đổi và đôi lúc coi
  risk runtime như đã có.
- **Primary owner / reviewer:** B / A.
- **Phụ thuộc:** Không.
- **Đầu vào:** Current Track B source/CLI, shared Pydantic contract, TypeScript,
  FastAPI routes và test tree.
- **Các bước:** Kiểm tra actual imports/behavior; phân loại parser/prompt/schema
  validation vs model inference; kiểm kê Contract/Invoice needs và shared gaps.
- **Files:** `backend/track-b/src/docai/track_b/`,
  `backend/track-b/scripts/run.py`, `backend/shared/src/docai/shared/`,
  `frontend/src/types/document.ts`, `tests/`.
- **Đầu ra:** Inventory current code, valid paths, status và blockers.
- **PASS:** Prompt builder/JSON mapping được mô tả là code scaffold; parse model
  thật, risk runtime, data/benchmark được ghi là chưa có.
- **Validation:** Đối chiếu import/method body với file hiện tại; audit snapshot
  được ghi trong task split và phần này.
- **Ngoài phạm vi:** Không đổi source/schema hoặc chọn model.
- **Bàn giao:** B1 và PE1.
- **Trạng thái:** `PASS` — chỉ audit snapshot, không phải inference pass.

### B1 — Chốt model-agnostic adapter contract

- **Vấn đề / lý do:** FastAPI/Product không được phụ thuộc prompt, provider hay
  nội bộ một VLM candidate.
- **Primary owner / reviewer:** B / A; Product Engineering reviewer.
- **Phụ thuộc:** B0 và proposal A1. PE1 lấy proposal này làm input; G1 review cả hai.
- **Đầu vào:** Shared schema, API input, Invoice/Contract requirements, provider
  classes có thể cần local/hosted interface.
- **Các bước:** Định nghĩa document/page input, request ID, prompt/domain version,
  candidate model metadata, raw response, usage/timing, evidence capabilities,
  missing behavior, typed error và capability negotiation.
- **Files:** `backend/track-b/src/docai/track_b/`; shared API/schema chỉ proposal;
  không đặt prompt trong frontend.
- **Đầu ra:** Adapter protocol/decision record không chứa provider-specific types
  ở public boundary.
- **PASS:** A và Product đồng ý input/output/error vocabulary; thay candidate
  không đòi sửa FastAPI/React; unknown capability không bị giả định.
- **Validation:** Contract examples/mock adapters cho success, unavailable,
  timeout, malformed raw response.
- **Ngoài phạm vi:** Không gọi endpoint, chưa chọn provider/model.
- **Bàn giao:** B2–B9 và PE4.
- **Trạng thái:** `NOT STARTED`.

### B2 — Chuẩn bị ảnh/PDF nhiều trang

- **Vấn đề / lý do:** VLM nhận giới hạn resolution/token/page; Contract dài có
  thể vượt context nếu gửi toàn bộ hoặc bị cắt âm thầm.
- **Primary owner / reviewer:** B / A; PE review shared upload boundary.
- **Phụ thuộc:** B1 và PE3 input limits để thiết kế boundary. D3 xác minh format
  thật trước khi hỗ trợ dataset cụ thể; synthetic fixtures cho phép thiết kế trước.
- **Đầu vào:** Image/PDF validated request, page order, document type và model
  candidate capabilities khi có.
- **Các bước:** Quy định format/page extraction, image resize/resolution, order,
  size/page limits; cho Contract chọn full-document, page selection hoặc
  chunking theo policy; ghi chunk/page map, overlap/merge rule/context limit;
  mọi truncate phải trả metadata/error rõ, không drop pages im lặng.
- **Files:** `backend/track-b/src/docai/track_b/`; shared upload validation ở
  `backend/shared/`/PE3; không claim runtime preprocessing đã có.
- **Đầu ra:** Deterministic page bundle và document coverage record.
- **PASS:** Multi-page order stable; supported/unsupported format rõ; từng
  omitted/truncated page có báo cáo; Contract clause evidence có mapping về page.
- **Validation:** PDF/image fixtures, corrupt/oversize, page reorder, long-document
  chunk boundaries và reassembly deterministic.
- **Ngoài phạm vi:** Không âm thầm bỏ trang; image enhancement shared thuộc PE;
  không upload cloud khi chưa duyệt.
- **Bàn giao:** B3/B4; Track A review input parity; PE3/PE4.
- **Trạng thái:** `PLANNED` — chưa có document/page preparation runtime.

### B3 — Version prompt riêng theo domain

- **Vấn đề / lý do:** Invoice fields và Contract clauses khác taxonomy; một
  instruction chung dễ làm model bỏ field hoặc bịa nội dung.
- **Primary owner / reviewer:** B / A; Data owner review label vocabulary.
- **Phụ thuộc:** B1 và B2 page semantics. D4 cần trước khi khóa prompt theo
  annotation của dataset; prompt skeleton/fixture cho hai domain có thể chuẩn bị
  trước đó.
- **Đầu vào:** Invoice/Contract target fields/categories, missing-value/evidence
  rules, output schema và model capability notes.
- **Các bước:** Tạo prompt riêng Invoice/Receipt và Contract; nêu type/format,
  missing behavior, source evidence, uncertainty và no-inference requirement;
  gắn immutable prompt version/hash; tạo test cases/snapshot; tránh prompt injection
  từ nội dung document.
- **Files:** Prompt/config đặt trong `backend/track-b/src/` hoặc thư mục owner
  chỉ khi prompt artifact thực; không để trong `frontend/`.
- **Đầu ra:** Versioned prompt set + domain coverage matrix.
- **PASS:** Hai domain có instruction/taxonomy riêng; version truy được; prompt
  không claim compliance/evidence capability không có.
- **Validation:** Snapshot/required-key/missing-clause cases với deterministic
  fixture; không coi prompt compliance là accuracy.
- **Ngoài phạm vi:** Không tuyên bố prompt tốt nhất nếu chưa đánh giá; không dùng
  test set để lặp prompt tune.
- **Bàn giao:** B4 adapter experiment, B5 parse fixture, RE1–RE3.
- **Trạng thái:** `SCAFFOLD` — có prompt builder đơn giản, chưa versioned.

### B4 — So sánh VLM candidates và chọn inference/fine-tuning

- **Vấn đề / lý do:** Một hard-coded VLM có thể không đáp ứng cả Invoice và
  Contract về chất lượng, context, evidence, latency hoặc license.
- **Primary owner / reviewer:** B / A; Research reviewer; user duyệt paid endpoint,
  download, GPU và fine-tuning resource.
- **Phụ thuộc:** B1–B3; D1–D5 source/license/data/split; RE1 protocol.
- **Đầu vào:** Candidate list có lý do (ví dụ PaddleOCR-VL, dots.ocr hoặc candidate
  khác), model card/version/checkpoint, supported inputs, context, license,
  hardware/API cost và baseline.
- **Các bước:** Dùng adapter contract; ghi candidate matrix; chạy cùng page/sample
  strategy cho Invoice và Contract riêng; xem option một model cho hai domain,
  model riêng theo domain hoặc nhiều candidate; chọn inference-only baseline
  trước. Fine-tuning/LoRA chỉ đề xuất nếu license, đủ train data, baseline,
  compute budget và expected gain đều có bằng chứng.
- **Files:** Matrix/decision report trong `docs/tasks/` hoặc Research artifacts;
  implementation adapter ở `backend/track-b/src/` sau approval.
- **Đầu ra:** Per-domain candidate decision (`SELECTED` hoặc `NOT SELECTED`) và
  rationale/version/config; candidate matrix giữ lại rejected option.
- **PASS:** Không hard-code model trước decision; fair protocol; license/resource
  review; quyết định fine-tune có justification hoặc ghi inference-only.
- **Validation:** Candidate tests trên D5-approved validation set; test split
  tách; cost/GPU chỉ sau explicit approval; không giả mạo candidate result.
- **Ngoài phạm vi:** Không download weights, gọi paid API, train/fine-tune trong
  audit/planning; không biến ví dụ thành lựa chọn chính thức.
- **Bàn giao:** B9 tích hợp adapter đã chọn; RE4 so sánh; PE4 nhận runner config.
- **Trạng thái:** `NOT STARTED` — model/provider decision là `NOT SELECTED`;
  chưa có candidate được duyệt hoặc run evidence.

### B5 — Parse structured response có lỗi thực tế

- **Vấn đề / lý do:** Model có thể trả JSON hợp lệ, fenced JSON, thêm prose,
  response bị cắt hoặc sai kiểu.
- **Primary owner / reviewer:** B / A.
- **Phụ thuộc:** B1 và schema semantics; B3 fixtures; không cần model thật để
  implement parser.
- **Đầu vào:** Raw response, candidate metadata, prompt version và parse policy.
- **Các bước:** Phân biệt JSON parse error, truncated, missing key, wrong type,
  duplicate/ambiguous field và unsupported shape; chỉ trích fenced/prose theo
  policy an toàn; không sửa value để “trông hợp lý”; giữ raw response access
  chỉ trong test/redacted diagnostics.
- **Files:** `backend/track-b/src/docai/track_b/parser.py` hiện gọi `json.loads`
  trong mapper; B5 parser implementation ở package này.
- **Đầu ra:** Typed parse result/error tách raw candidate khỏi validated output.
- **PASS:** Các failure class phân biệt; malformed không thành empty success;
  không mất model/request metadata.
- **Validation:** Valid JSON, fenced, prose, truncated, malformed, missing keys,
  wrong types và duplicate keys fixture.
- **Ngoài phạm vi:** JSON parse success không đồng nghĩa schema/factual success;
  không fake repair.
- **Bàn giao:** B6 validation/mapping.
- **Trạng thái:** `SCAFFOLD` — hiện chỉ `json.loads`, model call chưa có.

### B6 — Validate schema và normalize an toàn

- **Vấn đề / lý do:** Cần phân biệt parse thành công, schema hợp lệ và đúng sự
  thật trong document.
- **Primary owner / reviewer:** B / A; shared schema owner review.
- **Phụ thuộc:** B5 và PE1/A1 decision.
- **Đầu vào:** Typed candidate, Pydantic contract, explicit normalization rules.
- **Các bước:** Validate document type, fields, confidence, page, coordinates,
  missing value và optional evidence; chỉ normalize theo domain rules có nguồn;
  báo unsupported/missing thay vì tự sửa; giữ raw-to-normalized trace.
- **Files:** `backend/track-b/src/docai/track_b/parser.py`,
  `backend/shared/src/docai/shared/schema.py`; TypeScript mirror consumer.
- **Đầu ra:** Validated representation hoặc typed validation errors.
- **PASS:** Pydantic validation pass không được gắn nhãn factually correct;
  invalid range/coordinate bị reject; normalization traceable.
- **Validation:** Confidence ngoài `[0,1]`, reversed box, page invalid, missing,
  type mismatch; contract tests shared không đổi requirement để pass.
- **Ngoài phạm vi:** Không đổi schema đơn phương, không đánh đồng model confidence
  với correctness.
- **Bàn giao:** B7 evidence mapping và B9 runner.
- **Trạng thái:** `SCAFFOLD` — Pydantic validation đã có trong JSON helper,
  normalization/status handling chưa đầy đủ.

### B7 — Map Invoice/Contract evidence trung thực

- **Vấn đề / lý do:** Reviewer cần trace field/clause; VLM có thể không trả box
  hoặc source span đáng tin.
- **Primary owner / reviewer:** B / A; PE10 reviewer.
- **Phụ thuộc:** B2, B5, B6 và PE10 evidence decision. D4 cần cho mapping theo
  annotation thật; synthetic domain fixtures đủ cho mock runner mapping.
- **Đầu vào:** Validated values, raw response, page/chunk map, evidence capability
  của model/adapter.
- **Các bước:** Map Invoice seller/date/tax/total/line items; map Contract
  metadata, clause category/text/page/span; phân biệt cited text với verified
  source evidence; giữ missing evidence; map chunk pages về original document.
- **Files:** Track B package và shared schema; schema hiện có field-level
  `bounding_box`, `page_number`, `raw_text`, chưa có span model riêng.
- **Đầu ra:** Evidence map hoặc explicit `UNAVAILABLE`/missing state.
- **PASS:** Không tạo page/box/highlight/raw text; Contract clause không bị ép
  scalar; unsupported evidence limitation được gửi lên PE10.
- **Validation:** Fixture evidence present/missing, wrong page, chunk mapping,
  invoice field và multi-page clause cases.
- **Ngoài phạm vi:** Risk rules dùng shared Product layer khi tồn tại; task không
  được giả định risk runtime hiện có.
- **Bàn giao:** PE5/PE6 và RE7.
- **Trạng thái:** `BLOCKED` — shared evidence semantics chưa được chốt.

### B8 — Timeout, retry, logging và request tracing

- **Vấn đề / lý do:** Provider/network timeout không giống malformed response;
  retry không giới hạn gây cost và duplicate.
- **Primary owner / reviewer:** B / A; PE reviewer security/request lifecycle.
- **Phụ thuộc:** B1 adapter errors và phần API retry/lifecycle policy của PE8;
  không phụ thuộc upload UI. UI lifecycle wiring của PE8 có thể đến sau PE2.
- **Đầu vào:** Typed error classes, request ID, provider usage/timing metadata.
- **Các bước:** Chỉ retry lỗi transient; đặt max attempts/backoff/deadline;
  không retry validation vô hạn; log model/version/prompt/page count/latency/status
  với redaction; không log credential, full document hoặc raw sensitive output.
- **Files:** Track B adapter/runtime, config policy và tests; hiện chưa có runtime.
- **Đầu ra:** Reliability policy và structured safe telemetry.
- **PASS:** Mọi request có terminal state; retry bounded/idempotent; timeout và
  auth/model error phân biệt; telemetry đủ tái lập mà không lộ payload.
- **Validation:** Mock timeout/transport/auth/invalid response, retry count và
  redaction tests; không gọi provider.
- **Ngoài phạm vi:** Không log secret hoặc document content; không retry mọi lỗi.
- **Bàn giao:** B9 runner; PE8 lifecycle; RE5 timing boundary.
- **Trạng thái:** `PLANNED`.

### B9 — Track B runner và tests

- **Vấn đề / lý do:** Product cần một call boundary nhận document/domain, không
  tự ghép prompt/provider/parser.
- **Primary owner / reviewer:** B / A; PE review.
- **Phụ thuộc:** B1–B3, B5–B8, PE1/G1 shared-contract approval; B7 mock mapping
  dùng synthetic fixtures. B4 candidate selection chỉ prerequisite cho
  inference thật; mock adapter cho phép dựng runner contract trước khi
  model/resource được chọn.
- **Đầu vào:** Validated document/pages, DocumentType, candidate selection,
  prompt version và shared schema.
- **Các bước:** Orchestrate preparation→prompt→adapter→parse→validate→evidence;
  trả `pipeline_track=track_b_vlm`; ghi model/checkpoint/prompt/version/config
  khi thật có; thiếu model trả typed unavailable; viết deterministic tests.
- **Files:** `backend/track-b/src/docai/track_b/`, public export `__init__.py`,
  `backend/track-b/scripts/run.py`, Track tests khi nội dung thật.
- **Đầu ra:** Model-agnostic Track B runner + unit/contract tests.
- **PASS:** Invoice/Contract chạy cùng runner contract; model details encapsulated;
  output Pydantic valid hoặc typed unavailable/error; mock contract pass không
  được gọi là inference/benchmark.
- **Validation:** Mock adapters cho both domains, malformed/unavailable/timeout/
  missing evidence; end-to-end real chỉ sau data/model/resource gate.
- **Ngoài phạm vi:** Không đặt prompt/model internals vào FastAPI hoặc React.
- **Bàn giao:** PE4/PE9 và B10 Research handoff.
- **Trạng thái:** `NOT STARTED` — runner/mock contract chưa được triển khai;
  real inference adapter chờ B4/model/resource và B7 evidence decision.

### B10 — Research handoff theo model candidate

- **Vấn đề / lý do:** Research phải biết candidate nào chạy với prompt/input/config
  nào và response nào fail.
- **Primary owner / reviewer:** B / A.
- **Phụ thuộc:** B4/B8/B9 cho real model handoff; D5/RE1 bắt buộc trước mọi
  benchmark claim. Fixture-only handoff không có metric.
- **Đầu vào:** Candidate/model card, checkpoint hash, prompt version, generation
  settings, input/chunk strategy, request/failure records.
- **Các bước:** Xuất sanitized run manifest; map raw-to-parsed-to-validated;
  phân Invoice/Contract; ghi hardware/provider, latency boundary, retry/failures
  và limitations; fixture run ghi rõ synthetic.
- **Files:** Run metadata/report ngoài Git nếu sensitive/large; Research docs.
- **Đầu ra:** Reproducibility handoff cho từng model/domain.
- **PASS:** Candidate, version, config và source data/split trace được; report
  không gọi fixture/JSON-valid là benchmark.
- **Validation:** Independent manifest review/re-run theo RE protocol.
- **Ngoài phạm vi:** Không công bố performance nếu chưa có real ground truth.
- **Bàn giao:** RE4–RE8; quyết định chọn model quay lại A/B/Product.
- **Trạng thái:** `BLOCKED` — chưa có model run hoặc verified ground truth.

## Workstreams dùng chung — kế hoạch chi tiết


Phần này chứa các task chi tiết của Data Foundation, Product Engineering và Research & Evaluation; ownership, dependency graph, execution gates và thứ tự tổng thể nằm ở phần “Điều phối chung DocAI” đầu file.

### Data Foundation — dữ liệu dùng chung

#### Vì sao cần một workstream dữ liệu?

Invoice/Receipt và Contract có nhãn, định dạng và cách chia dữ liệu khác nhau.
Nếu hai Track tự tải và chuyển đổi dữ liệu riêng, chúng có thể đánh giá những
tập khác nhau hoặc làm mất nhãn gốc. Data Foundation chuẩn bị dữ liệu có thể
truy nguyên cho Track A, Track B và Research; workstream này không triển khai
model.

**Primary owner:** Thành viên B — Data Engineering. **Reviewer:** Thành viên A.
**Collaborator:** Track owners cung cấp input requirements; Research duyệt
ground truth/split trước khi đánh giá.

#### Trạng thái hiện tại

Trong repo, `data/raw/` và `data/processed/` chỉ có `.gitkeep`; không thấy data
file hoặc manifest. Vì vậy CORD v2, SROIE, MC-OCR 2021, CUAD v1 và DocILE đều
là **candidate trong kế hoạch, chưa xác nhận đã tải, quyền truy cập, license,
integrity hay phù hợp phiên bản**. Không commit dataset. `data/interim/` không
có trong cây hiện tại.

#### Dataset ứng viên

| Domain | Candidate | Dùng để tìm hiểu; chưa phải lựa chọn/approval |
|---|---|---|
| Invoice/Receipt | CORD v2 | Xác minh release, license, annotation, format và domain coverage |
| Invoice/Receipt | SROIE | Xác minh nguồn/release, license, task labels và split |
| Invoice/Receipt | MC-OCR 2021 | Xác minh access terms, ngôn ngữ, annotation và split |
| Contract | CUAD v1 | Xác minh license/source, clause taxonomy, annotation granularity và split |
| Optional | DocILE | Chỉ xem xét nếu bổ sung câu hỏi nghiên cứu rõ và license/resource phù hợp |

#### D0 — Audit EDA notebook và tình trạng data artifacts

- **Vấn đề / lý do:** Notebook hiện có thể làm người mới tưởng package loader,
  EDA và dataset schema vẫn tồn tại.
- **Primary owner / reviewer:** B / A.
- **Phụ thuộc:** Không.
- **Đầu vào:** `notebooks/01-eda.ipynb`, cây `data/`, source packages và
  `pyproject.toml`.
- **Các bước:** Xác nhận notebook import `docai.data`/`docai.core.schema` nhưng
  package đó không còn; ghi `.ipynb` là historical scaffold, không chạy; kiểm tra
  data dirs chỉ có placeholders; xác nhận `modal/` chỉ có ignored bytecode và
  không có deploy source.
- **Files:** Notebook, `data/raw/.gitkeep`, `data/processed/.gitkeep`, current
  backend package paths. Không sửa notebook code trong task planning này.
- **Đầu ra:** Ghi nhận rõ notebook/modal không chứng minh data inspection,
  acquisition hoặc GPU deployment đã xảy ra.
- **PASS:** Các status trên được phản ánh ở master task split; không có task nào
  phụ thuộc EDA notebook hiện tại để tải/đọc dataset.
- **Validation:** Đối chiếu import trong notebook với `rg --files` và source tree;
  inventory `data/` và `modal/`.
- **Ngoài phạm vi:** Không phục hồi `docai.data`, không chạy notebook, không khôi
  phục Modal source từ `.pyc`, không tải dataset.
- **Bàn giao:** D1 acquisition plan; D3 chọn nơi/format cho EDA mới sau khi data
  được phép dùng.
- **Trạng thái:** `PASS` — audit snapshot hoàn tất; notebook vẫn là scaffold cũ.

#### D1 — Lập kế hoạch acquisition và license

- **Vấn đề / lý do:** Chưa có bằng chứng dataset nào đã được chọn hoặc có thể
  dùng. Tải sai release hoặc không nắm quyền sử dụng tạo rủi ro pháp lý và làm
  kết quả khó tái lập.
- **Primary owner / reviewer:** B / A. Research reviewer: B theo protocol.
- **Phụ thuộc:** D0 PASS.
- **Đầu vào:** Candidate list ở trên, câu hỏi product/research và nguồn chính
  thức từng dataset.
- **Các bước:** Xác định owner/source URL, release/version, license/access
  terms, format, kích thước dự kiến, annotation/split, phương thức tải chính
  thức và yêu cầu attribution. Ghi rõ mục đích thương mại/nghiên cứu có phù hợp
  không; nếu điều khoản chưa rõ thì dừng candidate đó và xin review.
- **Files:** Hiện có `data/raw/`, `data/processed/`, `README.md` và
  `.gitignore`. Artifact dự kiến: bảng acquisition trong tài liệu này hoặc
  manifest có version; không tạo duplicate catalog nếu task split đã đủ.
- **Đầu ra:** Ma trận nguồn/license/access/version, quyết định
  `ELIGIBLE`/`INELIGIBLE`/`NEEDS REVIEW`, dự kiến storage và người phê duyệt.
- **PASS:** Mọi candidate dùng trong bước sau có nguồn/version và quyền sử
  dụng được reviewer xác nhận; unknown được ghi rõ và không tải.
- **Validation:** Đối chiếu license/source với trang phát hành chính thức và
  lưu URL/ngày kiểm tra; reviewer ký xác nhận. Không cần download để hoàn tất D1.
- **Ngoài phạm vi:** Không tải dữ liệu/model, không gọi API trả phí, không tự
  kết luận license pháp lý khi nguồn không rõ.
- **Bàn giao:** Data owner chuyển eligible source/version cho D2; Research
  nhận giới hạn license/domain để quyết định protocol.
- **Trạng thái:** `NOT STARTED`.

#### D2 — Quản lý raw data, manifest và integrity

- **Vấn đề / lý do:** Raw file phải giữ nguyên và truy xuất được mà không đưa
  dataset lớn vào Git.
- **Primary owner / reviewer:** B / A.
- **Phụ thuộc:** D1 PASS và quyết định rõ cho phép acquisition từng dataset.
- **Đầu vào:** Dataset đã được phép dùng, hướng dẫn tải chính thức, cấu trúc
  release và storage policy.
- **Các bước:** Chọn đường dẫn raw theo dataset/version; giữ nguyên cấu trúc và
  metadata/license; lập manifest có relative path, checksum, size, source,
  version và ngày acquisition; kiểm tra `.gitignore` bao phủ file lớn/nhạy cảm;
  xác nhận không có raw data trong Git index.
- **Files:** `data/raw/`, `.gitignore`; manifest dự kiến dưới `data/metadata/`
  chỉ khi có file thực và quyết định lưu trữ được thống nhất.
- **Đầu ra:** Raw dataset nằm ngoài Git cùng manifest/checksum có thể tái tạo.
- **PASS:** Checksum đọc lại khớp manifest, source/version truy được và
  `git status` không đề xuất commit data payload.
- **Validation:** Integrity scan cục bộ; kiểm tra ignore/tracking; không upload
  hoặc chia sẻ dữ liệu.
- **Ngoài phạm vi:** Không sửa raw file, không đưa sample nhạy cảm vào report,
  không commit dataset/checkpoint.
- **Bàn giao:** D3 nhận manifest và đường dẫn raw; A review checksum/storage.
- **Trạng thái:** `BLOCKED` — chờ D1 và quyền acquisition.

#### D3 — Kiểm kê và kiểm tra chất lượng dataset

- **Vấn đề / lý do:** Tên dataset không nói lên số document dùng được, lỗi file
  hay độ phủ nhãn.
- **Primary owner / reviewer:** B / A; Research xác nhận thống kê cần cho metric.
- **Phụ thuộc:** D2 PASS.
- **Đầu vào:** Raw manifest, annotation gốc và schema release.
- **Các bước:** Đếm document/page/file type; xác định image/PDF; dò file lỗi,
  thiếu annotation, duplicate, missing label và sai liên kết document-page;
  thống kê coverage theo field/clause/ngôn ngữ khi license cho phép; giữ script
  inspection deterministic và chỉ xuất aggregate.
- **Files:** `data/raw/`; script dự kiến trong `backend/shared/` chỉ sau khi có
  yêu cầu tái sử dụng cụ thể; report dự kiến ở `docs/tasks/` hoặc artifact
  metadata đã định, không để logic chỉ trong notebook.
- **Đầu ra:** Dataset inventory và quality report theo version/checksum.
- **PASS:** Số lượng report tái lập từ manifest; lỗi/loại trừ có rule và count;
  không lộ document content.
- **Validation:** Re-run inventory trên cùng manifest cho cùng aggregate;
  sample inspection chỉ khi license cho phép và lưu an toàn.
- **Ngoài phạm vi:** Không sửa annotation gốc, không gộp dataset/split, không
  kết luận chất lượng model.
- **Bàn giao:** D4 nhận label inventory; Research nhận coverage/limitation.
- **Trạng thái:** `BLOCKED` — chưa có raw dataset.

#### D4 — Mapping annotation mà không mất nhãn gốc

- **Vấn đề / lý do:** Các bộ dữ liệu có ontology, granularity và cách biểu diễn
  khác nhau; một nhãn CUAD không mặc nhiên tương đương một field Invoice.
- **Primary owner / reviewer:** B / A; Track owners review input cần thiết.
- **Phụ thuộc:** D3 PASS và shared contract semantics của G1 được review.
- **Đầu vào:** Annotation schema gốc, label inventory và source license.
- **Các bước:** Viết mapping riêng theo dataset/domain; giữ raw label/value/span;
  định nghĩa transform có thể đảo/trace khi hợp lý; ghi unmatched label, missing
  value, coordinate/page convention và version. Không ép CUAD clauses vào scalar
  Invoice fields.
- **Files:** Mapping specs/config dự kiến đặt cạnh adapter dữ liệu trong
  `backend/shared/` sau khi owner chốt loại artifact; nguồn hiện có là shared
  schema tại `backend/shared/src/docai/shared/schema.py`.
- **Đầu ra:** Mapping spec/versioned fixtures; không cần đưa dữ liệu thật vào Git.
- **PASS:** Mọi raw label có mapping hoặc disposition `UNMAPPED`; mapping giữ
  page/span/box nếu nguồn cung cấp và báo missing nếu không có.
- **Validation:** Round-trip/coverage checks trên annotation được phép dùng;
  reviewer đối chiếu các domain riêng.
- **Ngoài phạm vi:** Không sửa shared schema đơn phương, không tự sinh evidence,
  không train model.
- **Bàn giao:** A/B nhận adapter contract; RE2/RE3 nhận taxonomy và limitations.
- **Trạng thái:** `BLOCKED` — chờ annotation inventory và contract agreement.

#### D5 — Chốt split và ngăn data leakage

- **Vấn đề / lý do:** Tài liệu trùng/biến thể giữa train, validation và test có
  thể làm metric cao giả.
- **Primary owner / reviewer:** B / A; Research bắt buộc review.
- **Phụ thuộc:** D3 và D4 PASS; xem xét split gốc trước mọi thay đổi.
- **Đầu vào:** Split chính thức, document IDs, duplicate audit và mapping.
- **Các bước:** Ghi split nguồn; kiểm tra duplicate/near-duplicate và cùng
  contract/vendor/template xuyên split; giữ nguyên official split trừ khi có
  protocol approved; tạo split mới chỉ khi có lý do, seed và group key rõ.
- **Files:** Split metadata/manifest dự kiến dưới `data/metadata/` ngoài payload
  lớn; protocol tại phần Research & Evaluation trong file này.
- **Đầu ra:** Version/hash của split và leakage report.
- **PASS:** Không có leakage chưa giải thích; mọi exclusion/change có lý do,
  seed, count và review; test set không dùng để chọn threshold/model.
- **Validation:** Script kiểm tra ID overlap, group overlap và checksum.
- **Ngoài phạm vi:** Không trộn split tiện tay, không tune trên test set.
- **Bàn giao:** RE1 khóa protocol; candidate evaluation chỉ dùng split được duyệt.
- **Trạng thái:** `BLOCKED` — chờ dataset/annotation.

#### D6 — Định nghĩa processed-data contract

- **Vấn đề / lý do:** Hai Track cần nhận tài liệu/page và annotation tham chiếu
  theo cách có thể hiểu mà không biết chi tiết storage của nhau.
- **Primary owner / reviewer:** B / A; PE1 review API boundary.
- **Phụ thuộc:** G1 shared contract và D4 annotation mapping PASS.
- **Đầu vào:** Dataset mappings, shared schema, A/B runner input proposals.
- **Các bước:** Chốt identifier ổn định, document type, pages/order, image
  reference, raw annotation reference, source provenance và split membership;
  tách rõ record data khỏi model output và fixture.
- **Files:** `backend/shared/src/docai/shared/schema.py` là schema output hiện
  có; processed contract/spec là artifact tài liệu, không tự sửa schema/runtime.
- **Đầu ra:** Processed-data spec/version và fixture nhỏ deterministic.
- **PASS:** Cả A/B review; mọi field optional/missing/coordinate có semantics;
  raw source truy được mà không copy nội dung nhạy cảm vào log.
- **Validation:** Contract validation trên fixture; không cần model inference.
- **Ngoài phạm vi:** Không thêm runtime preprocessor hoặc thay output schema
  khi chưa có approval.
- **Bàn giao:** A/B dùng cùng input fixture; PE tích hợp request/document IDs.
- **Trạng thái:** `BLOCKED` — chờ G1 và D4.

#### D7 — Phát hành data quality report

- **Vấn đề / lý do:** Người dùng kết quả nghiên cứu cần biết dữ liệu bao phủ gì
  và không bao phủ gì.
- **Primary owner / reviewer:** B / A; Research duyệt mọi claim ảnh hưởng metric.
- **Phụ thuộc:** D2–D6 PASS.
- **Đầu vào:** Manifest, quality, mapping, split và license decisions.
- **Các bước:** Tóm tắt integrity, coverage, missing/corrupt/duplicate,
  annotation limitations, excluded samples, split/leakage checks và giới hạn
  license; chỉ công bố aggregate được phép.
- **Files:** Report dự kiến trong `docs/` khi có kết quả thật; task này hiện là
  kế hoạch, chưa có report dữ liệu.
- **Đầu ra:** Data quality report có dataset/version/split identity.
- **PASS:** Mọi con số trace được về script/manifest; không coi fixture là raw
  dataset hoặc ground truth.
- **Validation:** Reproduction check và review riêng theo Invoice/Contract.
- **Ngoài phạm vi:** Không đưa kết luận chất lượng model vào data report.
- **Bàn giao:** RE1 nhận split/coverage; A/B nhận limitation để thiết kế pipeline.
- **Trạng thái:** `BLOCKED` — chờ D2–D6.

#### Handoff và từ vựng trạng thái dữ liệu

Mỗi dataset ghi một trong `CANDIDATE`, `LICENSE REVIEW`, `APPROVED FOR
ACQUISITION`, `DOWNLOADED`, `INTEGRITY VERIFIED`, `ANNOTATION MAPPED` và
`EVALUATION READY`. Chỉ nâng status khi có manifest/report tương ứng. Raw,
processed, annotation/ground truth, fixture và model output có đường dẫn/nhãn
riêng; không dùng fixture để tuyên bố dataset hoặc benchmark thật.

### Product Engineering — API và sản phẩm


#### Sản phẩm cần làm gì?

Product Engineering nối người dùng với hai processing Track và shared result.
Frontend hiện dùng React, TypeScript, Vite, HTML/CSS; backend duy nhất là
Python/FastAPI/Pydantic. Node chỉ phục vụ frontend tooling. Không tạo Node
business backend, gọi model provider từ browser hoặc hiển thị extraction/metric
giả.

**Primary owner API/integration:** Thành viên B. **Reviewer:** Thành viên A
review contract và runner boundary. **React owner:** chưa được chỉ định trong
tài liệu/repo hiện có; nhóm cần chốt người trước PE2/PE5–PE7, không suy đoán.

#### Trạng thái code hiện tại

- API: `backend/shared/src/docai/shared/api.py` có `/health`; `/parse/classic`
  và `/parse/vlm` nhận upload/form nhưng ném `501`. Chưa có compare/explain.
- Contract: `backend/shared/src/docai/shared/schema.py` có
  `UnifiedDocumentOutput`, `ExtractedField`, `RiskFlag`, `BoundingBox`;
  TypeScript mirror ở `frontend/src/types/document.ts`.
- Frontend có Home, Invoice, Contract, Research pages và API client ở
  `frontend/src/services/api.ts`. Invoice/Contract là placeholder; Research
  hiển thị trạng thái PLANNED; code page chưa gọi `parseDocument`.
- Chưa có upload validation, document ID lifecycle, runner orchestration,
  structured API error, risk runtime hoặc evidence UI.
- `tests/` mới có schema/config/API route registration tests. `package.json`
  có dev/build/preview, chưa có test runner.

#### PE1 — Chốt shared API contract

- **Vấn đề / lý do:** Python schema, multipart request và TypeScript type hiện
  chỉ là baseline; lỗi/request metadata/evidence lifecycle chưa được quy định
  đủ cho Invoice và Contract.
- **Primary owner / reviewer:** B / A. Track A/B owner review field/evidence semantics.
- **Phụ thuộc:** G0 audit. Nhận proposal A1/B1 để thiết kế contract; không yêu
  cầu G1 trước khi viết proposal PE1.
- **Đầu vào:** `backend/shared/src/docai/shared/{api.py,schema.py,config.py}`,
  `frontend/src/types/document.ts`, `frontend/src/services/api.ts`.
- **Các bước:** Ghi route/method/content type; upload metadata và
  `document_type`; output envelope; request/document ID; error shape/code;
  optional/missing semantics; page/evidence; versioning/backward compatibility.
  Tách parse success khỏi factual correctness.
- **Files:** Các file source trên; task spec ở đây. Chỉ sửa implementation sau
  khi proposal được hai Track review.
- **Đầu ra:** Versioned API/contract spec và compatibility decision.
- **PASS:** Python/TypeScript field names/types và error cases khớp; Invoice và
  Contract đều biểu diễn được; mọi thiếu hụt Contract evidence được nêu.
- **Validation:** Contract examples cho 2 domain được Pydantic validate và
  đối chiếu TS; chỉ test khi implementation task được duyệt.
- **Ngoài phạm vi:** Không mở rộng schema đơn phương, không thêm API framework,
  không đưa model logic vào route/frontend.
- **Bàn giao:** B triển khai PE3/PE4; A/B dùng làm input cho runner contract.
- **Trạng thái:** `NOT STARTED` — schema hiện có là baseline, chưa phải quyết
  định hoàn chỉnh cho upload/errors/evidence.

#### PE2 — Thiết kế upload flow ở browser

- **Vấn đề / lý do:** Invoice/Contract pages hiện chỉ mô tả workflow; user chưa
  thể chọn domain/file hoặc xem lỗi upload.
- **Primary owner / reviewer:** **Chưa phân công** / B review API behavior; nhóm
  cần chỉ định reviewer UI.
- **Phụ thuộc:** PE1 PASS và owner React được chỉ định.
- **Đầu vào:** `frontend/src/pages/InvoicePage.tsx`,
  `ContractPage.tsx`, `components/WorkspacePlaceholder.tsx`,
  `services/api.ts`, contract PE1.
- **Các bước:** Domain selection; file picker và supported format/size feedback;
  submit/cancel policy; accessible label/focus; upload, validation và server
  errors; không gửi file đến model provider trực tiếp.
- **Files:** `frontend/src/pages/`, `components/`, `services/api.ts`, types.
- **Đầu ra:** Upload UI dùng FastAPI boundary và hiển thị trạng thái request.
- **PASS:** Domain/file/type validation được người dùng hiểu; unsupported/oversize
  được báo trước hoặc bằng API error; không lộ tài liệu khi lỗi.
- **Validation:** Browser/manual cases cho Invoice, Contract, unsupported file,
  cancel, server error và keyboard accessibility; test harness chưa chọn.
- **Ngoài phạm vi:** Không hiển thị extraction giả, không thêm router/framework
  hoặc storage phía browser ngoài quyết định.
- **Bàn giao:** PE3 nhận request fields; PE8 nhận state/error events.
- **Trạng thái:** `BLOCKED` — React owner chưa được nhóm chỉ định.

#### PE3 — Nhận và validate upload trong FastAPI

- **Vấn đề / lý do:** Route hiện khai báo `UploadFile` và `DocumentType` nhưng
  chưa kiểm tra payload hay quản lý file; route parse vẫn trả 501.
- **Primary owner / reviewer:** B / A review interface; security review nội bộ
  trước khi nhận tài liệu nhạy cảm.
- **Phụ thuộc:** PE1 PASS; storage/temp-file policy và size/file allowlist được duyệt.
- **Đầu vào:** API contract, `api.py`, config, MIME/extension requirements.
- **Các bước:** Kiểm tra content/type thực tế cùng extension; giới hạn bytes/page;
  đặt tên tạm an toàn; tránh path traversal; cleanup trên success/error/cancel;
  tạo request/document ID; trả error code có thể hiển thị an toàn.
- **Files:** `backend/shared/src/docai/shared/api.py`, `config.py`, shared tests;
  storage policy/config chỉ thêm khi cần thật.
- **Đầu ra:** Validated request/document input và typed API errors, trước model call.
- **PASS:** Invalid/oversize/empty/malformed uploads bị từ chối; temp files được
  cleanup; không log payload/credential; health route vẫn độc lập.
- **Validation:** API tests cho content type, empty/oversize/error/cleanup;
  test không dùng dịch vụ ngoài.
- **Ngoài phạm vi:** Không gọi Track/provider từ route ở task này; không thêm DB.
- **Bàn giao:** PE4 nhận validated document abstraction; PE8 nhận status/error.
- **Trạng thái:** `SCAFFOLD` — route nhận upload/form nhưng validation lifecycle
  chưa được triển khai.

#### PE4 — Điều phối Track qua runner boundary

- **Vấn đề / lý do:** FastAPI không được biết model internals; hiện parse routes
  trả 501 và chưa gọi runner.
- **Primary owner / reviewer:** B / A review runner interface.
- **Phụ thuộc:** PE1, PE3, A8 và B9 PASS; Track owners approve interface.
- **Đầu vào:** Validated input, selected track, domain type, runner protocols,
  shared output/errors.
- **Các bước:** Chọn runner qua allowlisted Track; truyền document/type và
  request ID; map typed errors sang API errors; không import provider/prompt
  internals; hỗ trợ partial/failure policy đã duyệt.
- **Files:** `backend/shared/src/docai/shared/api.py`; Track runners dưới
  `backend/track-a/src/` và `backend/track-b/src/`.
- **Đầu ra:** API orchestration nhỏ gọi boundary ổn định.
- **PASS:** Route chỉ biết protocol; response validate shared schema; unavailable
  model trả lỗi rõ, không trả fake result.
- **Validation:** Integration tests với fake deterministic runners cho success,
  validation failure, timeout/unavailable và domain type.
- **Ngoài phạm vi:** Không hard-code model/provider, không sửa Track logic.
- **Bàn giao:** PE9 tích hợp E2E; UI dùng response/errors theo PE1.
- **Trạng thái:** `BLOCKED` — runners A8/B9 chưa có implementation.

#### PE5 — Invoice Intelligence Workspace

- **Vấn đề / lý do:** `InvoicePage.tsx` hiện chỉ render `WorkspacePlaceholder`.
- **Primary owner / reviewer:** **Chưa phân công** / B review API; A review
  extraction/evidence semantics.
- **Phụ thuộc:** Owner React được chỉ định; PE1/PE2; PE4 trước khi render output.
- **Đầu vào:** Invoice schema, API response, risk/evidence decisions PE10.
- **Các bước:** Upload Invoice/Receipt; hiển thị seller/date/tax/totals/line items
  khi có; confidence và evidence theo nguồn thật; risk flags là review signals;
  phân biệt missing/low confidence/error.
- **Files:** `frontend/src/pages/InvoicePage.tsx`, components, types, service.
- **Đầu ra:** Workspace cho người dùng kiểm tra, không kết luận gian lận.
- **PASS:** Có thể trace field tới page/source evidence nếu được engine cung cấp;
  thiếu evidence hiển thị rõ; không hard-code mẫu như kết quả thật.
- **Validation:** UI states success/empty/missing/evidence/error bằng fixture
  được gắn nhãn test; E2E với API chỉ sau PE9.
- **Ngoài phạm vi:** Không implement Invoice model/risk policy trong React.
- **Bàn giao:** PE9 và RE protocol review UI-observed fields.
- **Trạng thái:** `BLOCKED` — owner React và upstream output chưa chốt.

#### PE6 — Contract Intelligence Workspace

- **Vấn đề / lý do:** `ContractPage.tsx` là placeholder; Contract cần clause/span
  dài và page evidence, không phải bảng Invoice kéo dài.
- **Primary owner / reviewer:** **Chưa phân công** / B review API; A review
  document evidence semantics.
- **Phụ thuộc:** Owner React được chỉ định; PE1/PE2/PE10 và Contract runner.
- **Đầu vào:** Contract metadata/clause taxonomy, output/evidence contract, API errors.
- **Các bước:** Hiển thị metadata, clause category/text, page/span khi có, missing
  clause và review signal; cho phép mở tài liệu tại evidence chỉ khi nguồn thật;
  ghi rõ hỗ trợ review chứ không đưa legal conclusion.
- **Files:** `frontend/src/pages/ContractPage.tsx`, components, TS types/service.
- **Đầu ra:** Workspace giúp tìm và đối chiếu clause.
- **PASS:** Clause text/category/page không bị ép thành scalar Invoice; evidence
  missing được biểu diễn là missing; cảnh báo pháp lý không khẳng định chắc chắn.
- **Validation:** UI fixtures cho clause nhiều trang, thiếu evidence, missing
  clause và error; phân biệt fixture với user result.
- **Ngoài phạm vi:** Không tự tạo Contract taxonomy/legal advice hoặc model logic.
- **Bàn giao:** PE9; B/A owner rà mapping cross-track.
- **Trạng thái:** `BLOCKED` — owner React, Contract evidence representation chưa chốt.

#### PE7 — Research Lab cho kết quả có nguồn

- **Vấn đề / lý do:** `ResearchPage.tsx` là trang placeholder với metric labels,
  chưa có result store/protocol.
- **Primary owner / reviewer:** **Chưa phân công** / B review data/API; A review
  model-comparison interpretation.
- **Phụ thuộc:** Owner React; RE1–RE4 và report schema có dữ liệu thật.
- **Đầu vào:** Evaluation report versioned, domain/Track/model identifiers,
  uncertainty/failure coverage.
- **Các bước:** Chỉ hiển thị metric có dataset/split/protocol link; tách Invoice,
  Contract, Track và model candidate; show sample counts/limitations; không lấy
  value từ fixture hoặc scaffold.
- **Files:** `frontend/src/pages/ResearchPage.tsx`; RE docs/artifacts.
- **Đầu ra:** Research UI đọc report thật hoặc trạng thái `NOT RUN`.
- **PASS:** Mỗi metric trace được về report; không có value giả/thiếu denominator;
  unavailable data ghi rõ.
- **Validation:** Empty/NOT RUN/report available states; kiểm tra provenance link.
- **Ngoài phạm vi:** Không tính metric ad hoc trong browser, không tự gọi model.
- **Bàn giao:** RE8 và PE9.
- **Trạng thái:** `BLOCKED` — frontend owner và Research report contract chưa có.

#### PE8 — Request lifecycle, loading và lỗi

- **Vấn đề / lý do:** Client hiện chỉ throw status text; chưa phân biệt processing,
  timeout, partial success, unsupported và retryable error.
- **Primary owner / reviewer:** B cho API semantics / A; frontend owner cần tham gia
  và nhóm cần chỉ định owner UI.
- **Phụ thuộc:** PE1 và PE3 cho API lifecycle; PE2 chỉ là prerequisite cho UI
  wiring, không chặn API policy/runner integration. React owner cần được chỉ
  định trước khi hoàn thiện UI states.
- **Đầu vào:** Request/error contract, request ID và UI lifecycle events.
- **Các bước:** Chuẩn hóa status; phân loại retryable/non-retryable; giới hạn
  retry; hiển thị request ID an toàn; hỗ trợ cancel/timeout policy; bảo đảm retry
  không gửi duplicate không kiểm soát.
- **Files:** `api.py`, `frontend/src/services/api.ts`, pages/components và tests.
- **Đầu ra:** Lifecycle nhất quán từ upload đến terminal state.
- **PASS:** Mọi request kết thúc ở success/partial/failure/cancel; lỗi hiển thị
  rõ; credential/sensitive body không xuất hiện log/UI.
- **Validation:** API/client tests cho timeout, HTTP errors, invalid JSON,
  cancellation và retry policy.
- **Ngoài phạm vi:** Không retry validation errors vô hạn; không hứa background
  job nếu chưa có runtime design.
- **Bàn giao:** PE4/PE9.
- **Trạng thái:** `SCAFFOLD` — client error throw đơn giản; lifecycle đầy đủ chưa có.

#### PE9 — Tích hợp end-to-end

- **Vấn đề / lý do:** Unit/schema/route checks riêng không chứng minh UI → API →
  runner → schema → UI có cùng contract.
- **Primary owner / reviewer:** B API/E2E integration / A; React owner sau khi chỉ định.
- **Phụ thuộc:** PE2–PE6, PE8, A8, B9 và G3 PASS. PE7 Research Lab tích hợp
  riêng khi report thật có; không chặn Product E2E bằng benchmark chưa tồn tại.
- **Đầu vào:** Deterministic fixture, test runners, API contract, frontend states.
- **Các bước:** Test Invoice và Contract, từng Track, happy/error/partial path;
  xác minh field/evidence không bị mất hoặc đổi tên; ghi test fixture metadata.
- **Files:** `tests/integration/`, frontend tests/harness chỉ khi được chọn,
  `frontend/src/services/api.ts`.
- **Đầu ra:** E2E test plan và kết quả có thể tái lập.
- **PASS:** Hai domain và hai Track đi đúng route/schema; lỗi không biến thành
  kết quả thành công; không dùng inference/paid API mặc định.
- **Validation:** Test dùng fake runners/fixtures; real-run E2E chỉ khi model,
  data và resource được duyệt.
- **Ngoài phạm vi:** Không coi static page render là extraction E2E.
- **Bàn giao:** G4; RE nhận run boundary/provenance.
- **Trạng thái:** `BLOCKED` — runners và workspace chưa triển khai.

#### PE10 — Shared Risk và Evidence contract

- **Vấn đề / lý do:** Shared schema có `risk_flags`, `bounding_box`, `page_number`,
  `raw_text`, nhưng code hiện không có risk runtime; Contract span/evidence model
  riêng chưa tồn tại. Track B B6 cũ đã nói “dùng chung risk layer” như thể layer
  đang có — đó là sai trạng thái.
- **Primary owner / reviewer:** B điều phối Product/shared implementation / A;
  Track A/B owner review mapping của mình.
- **Phụ thuộc:** PE1 proposal và domain requirements A1/B1; task này chốt
  semantics từ yêu cầu/schema hiện có, không chờ A7/B7 implementation.
- **Đầu vào:** Shared schema, Invoice/Contract requirements, audit evidence
  capabilities và known gaps trong A/B plans.
- **Các bước:** Phân biệt extraction evidence với risk finding; nêu source/provenance
  và missing semantics; xác định invoice arithmetic vs Contract clause review;
  xác định input rule layer; lập schema-change proposal nếu current box/page/raw
  text không đủ. Chỉ sau review mới implement shared logic.
- **Files:** `backend/shared/src/docai/shared/schema.py`; `api.py`; A/B mapping code.
- **Đầu ra:** Risk/evidence contract và decision record; runtime implementation
  là task follow-up sau approval.
- **PASS:** Không duplicate risk rule trong Track; missing evidence không bị bịa;
  Contract output giữ span/page cần thiết hoặc blocker schema được ghi rõ; UI
  wording là review aid, không phải fraud/legal verdict.
- **Validation:** Shared contract examples cho Invoice/Contract, field có/không
  evidence, rule output và backward compatibility review.
- **Ngoài phạm vi:** Không tự đổi schema/policy, không tạo fake risk/evidence.
- **Bàn giao:** Track A/B mapping, PE5/PE6 và RE7.
- **Trạng thái:** `SCAFFOLD` ở output envelope; runtime risk/evidence `PLANNED`.

#### Quyết định còn thiếu

Nhóm cần chỉ định React primary owner và UI reviewer trước PE2/PE5–PE7. Không
chặn PE1/PE3 backend contract work để chờ quyết định UI; không chuyển UI ownership
sang B chỉ vì B làm API.

### Research & Evaluation — protocol và đánh giá


#### Research trả lời câu hỏi nào?

Research so sánh Track A/B và từng model candidate trên Invoice/Receipt lẫn
Contract. Kết quả phải dựa trên output inference thật, ground truth được kiểm
tra và protocol có version. Product workspace trả kết quả phục vụ người dùng;
Research giải thích mức chính xác, failure, độ bền, latency, cost và evidence.

**Primary owner chung:** Thành viên B dẫn dắt protocol, dataset và experiment
plumbing. **Reviewer:** Thành viên A. RE7 về model/evidence interpretation do
A dẫn dắt, B review. Mỗi task vẫn có một primary owner.

#### Trạng thái hiện tại

Trong source hiện có shared schema/config/API tests; không thấy evaluation
package, ground-truth dataset, model output hoặc benchmark artifact. Frontend
Research page chỉ có nhãn metric và trạng thái `PLANNED`. Không có metric thật.

#### RE1 — Khóa evaluation protocol

- **Vấn đề / lý do:** Kết quả không so sánh được nếu khác split, taxonomy,
  normalization hoặc evaluation unit.
- **Primary owner / reviewer:** B / A; D owner cung cấp provenance.
- **Phụ thuộc:** D3–D5; PE1 shared contract; Track A/B nêu output fields.
- **Đầu vào:** Dataset version/license, annotation mapping, source split,
  Invoice/Contract taxonomy và model output format.
- **Các bước:** Chốt dataset/release/hash/split; unit (document/page/field/clause);
  inclusion/exclusion; missing-value/duplicate policy; exact và normalized
  matching; aggregation/confidence intervals nếu đủ mẫu; test-set isolation.
- **Files:** Phần Data Foundation trong file này, PE1 contract và protocol
  artifact dự kiến trong `docs/` trước khi chạy.
- **Đầu ra:** Versioned protocol, metric definitions và run manifest template.
- **PASS:** A, Data owner và cả Track owners review; Invoice/Contract tách rõ;
  một run độc lập có thể tái tạo split/metric; test set không dùng để chọn model.
- **Validation:** Protocol review bằng fixture minh họa, không công bố metric.
- **Ngoài phạm vi:** Không tự chọn model, không tính benchmark từ fixture.
- **Bàn giao:** RE2/RE3 và mọi candidate evaluation.
- **Trạng thái:** `NOT STARTED` — chưa có ground truth được xác minh.

#### RE2 — Định nghĩa Invoice/Receipt evaluation

- **Vấn đề / lý do:** Invoice field và bảng hàng có dạng giá trị khác nhau; một
  phép so chuỗi duy nhất có thể đánh giá sai.
- **Primary owner / reviewer:** B / A; Track A/B owners review field mapping.
- **Phụ thuộc:** RE1 và D4/D5 PASS.
- **Đầu vào:** CORD/SROIE/MC-OCR candidate đã xác minh, canonical Invoice fields,
  raw annotations và mapping.
- **Các bước:** Tách field coverage/missing; định nghĩa exact match và normalization
  theo field (date/currency/number/string); precision/recall/F1 khi phù hợp;
  line-item/table metrics chỉ khi annotation hỗ trợ; báo unsupported field riêng.
- **Files:** Spec/report artifact trong `docs/`; reusable metric code chỉ tạo
  dưới `backend/shared/` sau task implement được duyệt.
- **Đầu ra:** Invoice metric spec, examples và template kết quả.
- **PASS:** Metric gắn rõ dataset/split/domain/field; normalization deterministic;
  denominator và missing prediction/ground-truth policy được ghi.
- **Validation:** Hand-calculated fixture cases cho exact/normalized/missing;
  chưa có fixture nào được gọi là benchmark.
- **Ngoài phạm vi:** Không chuyển metric Contract sang Invoice hoặc tune trên test.
- **Bàn giao:** RE4 fair comparison; RE8 report.
- **Trạng thái:** `BLOCKED` — chờ RE1 và verified Invoice annotations.

#### RE3 — Định nghĩa Contract evaluation

- **Vấn đề / lý do:** Clause classification, span/text và page evidence khác
  scalar Invoice fields.
- **Primary owner / reviewer:** B / A; Contract taxonomy owner review.
- **Phụ thuộc:** RE1, D4/D5 và shared evidence decision PE10.
- **Đầu vào:** CUAD candidate đã xác minh, raw clause labels/spans và Contract
  taxonomy.
- **Các bước:** Xác định clause category coverage; classification vs extraction;
  text/span match rule; page evidence accuracy/availability; missing clause và
  multiple clauses policy; giới hạn taxonomy của annotation.
- **Files:** Protocol tại `docs/`; evidence source là Track output + shared
  contract; không assume `ExtractedField` một mình biểu diễn mọi span.
- **Đầu ra:** Contract metric spec theo category, span/text và evidence.
- **PASS:** Không ép Invoice metric; category/split/denominator rõ; thiếu span
  capability được báo blocker thay vì suy đoán.
- **Validation:** Hand-calculated cases cho exact/overlap/partial/missing span;
  không tính trên data chưa được duyệt.
- **Ngoài phạm vi:** Không đưa kết luận pháp lý hoặc fake ground truth.
- **Bàn giao:** RE4/RE7/RE8.
- **Trạng thái:** `BLOCKED` — chờ CUAD verification và PE10 evidence decision.

#### RE4 — So sánh Track công bằng

- **Vấn đề / lý do:** So sánh lệch nếu Track nhận page khác, normalization khác
  hoặc một bên được tune trên test.
- **Primary owner / reviewer:** B / A.
- **Phụ thuộc:** RE1–RE3; A8 và B9 runner PASS; output thật được version.
- **Đầu vào:** Cùng dataset/split/ground truth, run manifests, exclusions, model
  metadata và field/clause mapping.
- **Các bước:** Chạy từng Track trên cùng evaluation units; giữ input/page policy
  khác biệt có lý do và đo/ghi riêng; báo per-domain, per-field/category,
  failures/missing evidence; không gom trung bình che mất failure mode.
- **Files:** Run artifacts ngoài Git theo approved storage; report trong `docs/`
  khi có dữ liệu thật.
- **Đầu ra:** Paired comparison tables/analysis, trace về từng run.
- **PASS:** Điều kiện đánh giá và data provenance tương đương hoặc khác biệt
  được định lượng; metric tái lập; fixture/mock bị loại khỏi benchmark.
- **Validation:** Re-run một subset; đối chiếu counts/split/model fingerprints.
- **Ngoài phạm vi:** Không tuyên bố track thắng chỉ từ agreement hoặc một metric.
- **Bàn giao:** RE8 và Product Research UI PE7.
- **Trạng thái:** `BLOCKED` — model runners, real outputs và RE1–RE3 chưa PASS.

#### RE5 — Đo latency và cost

- **Vấn đề / lý do:** Một số latency có thể bỏ qua warm-up, preprocessing hoặc
  parse; cost có thể bỏ qua hardware/API usage.
- **Primary owner / reviewer:** B / A; resource owner kiểm tra cost assumption.
- **Phụ thuộc:** Runner thật, RE1 và approved compute/provider.
- **Đầu vào:** Run manifest, hardware/provider, timing boundaries và usage records.
- **Các bước:** Đo preprocessing, model inference, parsing/validation và total
  request riêng; quy định cold/warm behavior, batch size, page count, timeout;
  tính cost per document theo invoice/resource billing có căn cứ.
- **Files:** Track runner metadata, API lifecycle và report artifacts; không lưu
  credential trong repo.
- **Đầu ra:** Latency/cost methodology và kết quả theo model/domain.
- **PASS:** Có số mẫu, statistic, timing boundary, hardware/provider và cost
  source; mock latency ghi riêng, không dùng làm real result.
- **Validation:** Repeated run theo protocol; đối chiếu logs với request IDs,
  không log document payload.
- **Ngoài phạm vi:** Không gọi paid service/Modal hoặc phát sinh GPU cost nếu
  chưa được user duyệt.
- **Bàn giao:** RE8 và Product planning.
- **Trạng thái:** `BLOCKED` — chưa có real inference/resource approval.

#### RE6 — Đo robustness

- **Vấn đề / lý do:** Input thật có thể mờ, xoay hoặc bị crop; chưa biết chất
  lượng thay đổi thế nào.
- **Primary owner / reviewer:** B / A; Track owners review degradation method.
- **Phụ thuộc:** RE1–RE4, verified clean baseline và được phép biến đổi dataset.
- **Đầu vào:** Test-only sample, degradation parameters/seeds và output baseline.
- **Các bước:** Chọn blur/rotation/noise/brightness/crop/perspective/watermark phù
  hợp; lưu severity/seed; chạy từng Track cùng sample; đo performance drop so với
  clean input; tách preprocessing cố cải thiện input khỏi robustness cố làm input
  xấu để đo sức chịu.
- **Files:** Experiment spec/report trong `docs/`; script reusable chỉ sau task
  được giao, không để pipeline duy nhất trong notebook.
- **Đầu ra:** Robustness protocol và degradation report theo domain/Track/model.
- **PASS:** Transform reproducible; clean baseline và severity rõ; không làm
  thay đổi ground truth; không công bố nếu sample quá ít/không đại diện.
- **Validation:** Seed replay, image integrity và paired metric checks.
- **Ngoài phạm vi:** Không áp dụng augmentation vào training/evaluation mà không
  ghi mục đích; không tạo robustness claim từ synthetic fixture.
- **Bàn giao:** RE8; PE quyết định preprocessing chỉ sau evidence.
- **Trạng thái:** `BLOCKED` — chưa có dataset/baseline/protocol.

#### RE7 — Đánh giá evidence và explainability

- **Vấn đề / lý do:** Box/span có thể giúp người review, nhưng attention map hoặc
  model confidence không tự chứng minh lời giải thích đúng.
- **Primary owner / reviewer:** A / B.
- **Phụ thuộc:** PE10 shared evidence contract, A7/B7 evidence mapping và RE1.
- **Đầu vào:** Source document được phép review, extracted values/clauses, source
  evidence và reviewer protocol.
- **Các bước:** Phân loại evidence thật/thiếu/không hỗ trợ; đo page/span alignment
  khi ground truth cho phép; khảo sát reviewer usefulness nếu có protocol;
  phân biệt confidence, attribution và causal explanation.
- **Files:** Track mapping outputs, schema và RE report; explainability runtime
  không có trong code hiện tại.
- **Đầu ra:** Evidence quality rubric, failure examples đã khử nhạy cảm và report.
- **PASS:** Claim chỉ dựa evidence đo được; attention không bị gọi là proof;
  Contract span limitation được ghi; privacy/licensing được giữ.
- **Validation:** Blind/manual review protocol hoặc span metrics có annotation;
  không dùng heatmap giả.
- **Ngoài phạm vi:** Không sinh overlay/evidence không do engine cung cấp; không
  tuyên bố pháp lý.
- **Bàn giao:** PE5/PE6 và RE8.
- **Trạng thái:** `BLOCKED` — evidence contract và annotation chưa có.

#### RE8 — Viết report tái lập

- **Vấn đề / lý do:** Con số rời rạc không giúp nhóm biết model/Track nào phù
  hợp cho domain nào.
- **Primary owner / reviewer:** B / A.
- **Phụ thuộc:** RE1–RE7 và real runs đã được duyệt. G6 review report trước khi
  chấp nhận/công bố kết luận; RE8 không phụ thuộc ngược vào G6.
- **Đầu vào:** Versioned run manifests, metric tables, failure analysis, limits
  và review comments.
- **Các bước:** Báo Invoice và Contract riêng; tách model candidate/Track; nêu
  data/split/metric/config/latency/cost; trình bày failure/missing evidence,
  uncertainty và limitations; không extrapolate ngoài sample.
- **Files:** Report mới trong `docs/reports/` chỉ tạo khi có kết quả thật; hiện
  thư mục report canonical chưa có file trong working tree.
- **Đầu ra:** Research report có source links và reproduction recipe.
- **PASS:** Mỗi claim gắn run/data/protocol; fixture/mock được loại trừ hoặc
  ghi test-only; reviewer có thể tái lập; không có metric tự tạo.
- **Validation:** Re-run report generation/spot checks; independent review của A.
- **Ngoài phạm vi:** Không sửa product status hoặc quảng bá candidate thành model
  production đã chọn.
- **Bàn giao:** PE7 chỉ đọc report đã review; nhóm quyết định model/roadmap bằng
  evidence.
- **Trạng thái:** `BLOCKED` — chưa có run và ground truth.
