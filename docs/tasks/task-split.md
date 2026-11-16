# Phân công công việc DocAI

## Tài liệu này dùng để làm gì?

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

## Trạng thái code và dữ liệu tại thời điểm audit

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

## Ai sở hữu phần nào?

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

## Khái niệm phải giữ riêng

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

## Các gate triển khai

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

## Roadmap và tài liệu chi tiết

| Giai đoạn | Task | Mục tiêu |
|---|---|---|
| 0. Audit/ownership | A0, B0, PE1 | Inventory thực tế, boundary và quyền sở hữu |
| 1. Shared/data foundation | A1, B1, PE1, PE10; D1 chạy song song, D2 chỉ sau khi acquisition được cho phép | Contract và kế hoạch dữ liệu rõ trước khi phụ thuộc |
| 2. Song song theo track | A2–A7; B2–B8 bằng fixture; D2–D6 theo prereq data | Stage/prompt/adapter/mapping; dataset-specific mapping đợi D4, mock contract không đợi acquisition |
| 3. Runner contracts | A8–A9; B9–B10; D7 | Boundary/test pass với mocks; model selection/data thật vẫn độc lập |
| 4. Product mock integration | PE2–PE6, PE8–PE9 | Upload, API orchestration, workspaces và E2E contract flow; không phải real inference |
| 5. Research + Research UI | RE1–RE8, rồi PE7 | Real evaluation sau license, ground truth, model/resource approvals; UI chỉ đọc report đã review |

- [Track A Classic](track-a-classic.md)
- [Track B VLM](track-b-vlm.md)
- [Data Foundation](data-foundation-tasks.md)
- [Product Engineering](product-engineering-tasks.md)
- [Research & Evaluation](research-evaluation-tasks.md)

## Quy tắc model, dữ liệu và status

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

## Test và handoff

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

## Thành viên B nên bắt đầu từ đâu?

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
