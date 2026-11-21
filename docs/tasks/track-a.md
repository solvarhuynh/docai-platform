# Track A Classic — kế hoạch công việc chi tiết

## Track A giải quyết việc gì?

Track A là **processing track** nhiều chặng, có thể dùng nhiều model: layout
detection tìm vùng trang; OCR đọc chữ và vị trí; KIE (Key Information
Extraction) gán ý nghĩa cho token. Pipeline cuối phải xử lý được cả Invoice/
Receipt và Contract rồi tạo `UnifiedDocumentOutput`. “Track A” không phải tên một
model và không đồng nghĩa riêng Invoice.

```text
document/pages → layout → OCR text + geometry → KIE
               → Invoice fields hoặc Contract clauses/evidence
               → shared output
```

**Primary owner:** Thành viên A — AI/ML/DL. **Reviewer:** Thành viên B, đặc biệt
cho input/data mapping, shared boundary và reproducibility. Product Engineering
review runner contract; Research review protocol/model comparison.

Ownership toàn repository, execution gates và các task dùng chung về dữ liệu,
Product Engineering, Research & Evaluation nằm trong
[`shared.md`](shared.md). Đọc phần đó khi task Track A phụ thuộc shared
contract hoặc workstream khác.

## Audit code thật tại thời điểm viết kế hoạch

- `src/docai/track_a/pipeline.py` có `LayoutDetector`,
  `OCRExtractor`, `LayoutLMv3Extractor`. Inference methods ném
  `NotImplementedError`; polygon-to-box và lọc region là utility code.
- `src/docai/track_a/__init__.py` export các class trên.
- `src/docai/track_a/__main__.py` kiểm tra input path và in stage names; không
  chạy model.
- Shared contract hiện ở `src/docai/shared/schema.py`.
- Không thấy checkpoint/model config, OCR/layout weights, dataset hoặc test riêng
  Track A. Model candidate trong nội dung này chỉ là candidate.

## A0 — Audit repository và interface Track A

- **Vấn đề / lý do:** Kế hoạch cũ dùng path trước đó và có thể khiến owner sửa
  module không tồn tại hoặc coi utility là inference.
- **Primary owner / reviewer:** A / B.
- **Phụ thuộc:** Không.
- **Đầu vào:** Cây source hiện tại, task split, shared schema và test tree.
- **Các bước:** Kiểm tra Track A source/CLI/import/test; phân loại implemented,
  scaffold, planned, not selected; xác nhận Invoice và Contract cùng thuộc
  Track A; ghi dependency với Data, PE và Research.
- **Files:** `src/docai/track_a/`,
  `src/docai/track_a/__main__.py`, `src/docai/shared/schema.py`,
  `tests/`.
- **Đầu ra:** Inventory thực tế và danh sách gap.
- **PASS:** Path và trạng thái khớp working tree; `pipeline.py` được ghi scaffold,
  không gọi CLI là inference.
- **Validation:** Đối chiếu `rg --files`, imports và method bodies; audit này đã
  thực hiện cho snapshot hiện tại.
- **Ngoài phạm vi:** Không refactor source hoặc chọn model.
- **Bàn giao:** A1 và B0/PE1 dùng chung inventory.
- **Trạng thái:** `PASS` — audit artifact được ghi tại đây; không phải pipeline
  runtime pass.

## A1 — Thống nhất stage contract và evidence

- **Vấn đề / lý do:** Các stage chưa có input/output ổn định; box/page và missing
  values ảnh hưởng mapping cho cả hai domain.
- **Primary owner / reviewer:** A / B; PE1 review integration boundary.
- **Phụ thuộc:** A0. Đây là proposal chuẩn bị cho G1; không chờ G1 trước khi soạn.
- **Đầu vào:** `src/docai/shared/schema.py`, dataset annotation
  mapping khi có, Track B page/input proposal.
- **Các bước:** Định nghĩa page index, reading order, token text/confidence,
  polygon/box coordinate convention, normalized vs pixel, missing/unreadable
  values, stage errors, model metadata và domain taxonomy. Contract giữ clause
  text/page/source trace; không ép Contract clause thành Invoice scalar.
- **Files:** Shared schema hiện có; thiết kế Track A trong README/task này hoặc
  code docstring khi có task implementation.
- **Đầu ra:** Reviewed stage interface và error vocabulary; nếu shared schema
  thiếu field thì tạo proposal riêng, không tự sửa.
- **PASS:** B và Product Engineering xác nhận runner có thể trả shared output;
  A/B mapping có thể biểu diễn thật hoặc nêu rõ evidence limitation.
- **Validation:** Ví dụ contract cho Invoice và Contract validate được theo
  schema hiện tại hoặc đánh dấu gap cụ thể.
- **Ngoài phạm vi:** Không tự đổi `UnifiedDocumentOutput`.
- **Bàn giao:** A2–A5 và PE1.
- **Trạng thái:** `NOT STARTED`.

## A2 — Chuẩn bị page cho Classic và đánh giá layout

- **Vấn đề / lý do:** Scan/PDF nhiều trang và page geometry có thể làm lệch vùng
  trước khi OCR/KIE.
- **Primary owner / reviewer:** A / B; PE review ranh giới document-level prep.
- **Phụ thuộc:** A1. D3 chỉ cần trước khi xác nhận format/coverage hoặc chạy
  đánh giá candidate trên dữ liệu thật; synthetic input đủ để dựng interface.
- **Đầu vào:** Image/PDF pages, page dimensions, annotation/layout labels,
  requirements từ shared upload boundary.
- **Các bước:** Định nghĩa stage input image/page; rotation/resize/crop policy
  chỉ trong nhu cầu Track A; giữ transform map về trang gốc; xác định region
  taxonomy; khảo sát candidate layout model theo chất lượng, license, footprint,
  hardware và domain coverage. YOLO/doc-layout families là candidate nếu có
  evidence, chưa được chốt.
- **Files:** `pipeline.py` hiện chỉ scaffold; output code dự kiến trong
  `src/docai/track_a/`.
- **Đầu ra:** Page/layout interface, candidate matrix và regions có label,
  confidence, page, source-coordinate box.
- **PASS:** Transform reversible/traceable; box hợp lệ; page order không mất;
  candidate có license/resource evidence; thiếu model báo unavailable.
- **Validation:** Synthetic geometry cases; sau D3 thêm layout annotation
  evaluation, không tuyên bố accuracy trước real run.
- **Ngoài phạm vi:** Shared upload/temp-file security thuộc PE3; không tải weights
  hay chạy GPU khi chưa được duyệt.
- **Bàn giao:** A4 nhận regions; A6 nhận candidate evidence; PE cung cấp page input.
- **Trạng thái:** `SCAFFOLD` — class tồn tại, inference/preprocessing runtime chưa có.

## A3 — OCR text, confidence và geometry

- **Vấn đề / lý do:** KIE không thể phục hồi chữ bị OCR bỏ hoặc sai; OCR phải giữ
  vị trí và nguồn để review.
- **Primary owner / reviewer:** A / B.
- **Phụ thuộc:** A1/A2 input contract. Có thể xây stage boundary/transform
  fixtures trước A6; concrete OCR provider adapter chờ A6 chọn candidate.
- **Đầu vào:** Page image, locale/language, approved OCR candidate/config.
- **Các bước:** So sánh pretrained OCR candidates theo ngôn ngữ/domain, latency,
  license và resource; output text/token, confidence, polygon/box và page;
  giữ raw text; biểu diễn empty/unreadable; nếu fine-tuning đề xuất thì chứng minh
  data/language gap và baseline trước.
- **Files:** `pipeline.py` (`OCRExtractor` hiện scaffold), A test dưới `tests/`
  chỉ khi implementation được giao.
- **Đầu ra:** OCR record traceable và candidate/training decision.
- **PASS:** Geometry truy về original page; confidence range rõ; empty/low quality
  không biến thành text giả; OCR error phân biệt với KIE error.
- **Validation:** Polygon conversion, empty/corrupt/page cases; real OCR metrics
  chỉ trên D5-approved split.
- **Ngoài phạm vi:** Không mặc định PaddleOCR là lựa chọn; không fine-tune/download.
- **Bàn giao:** A4 và A5; D4/Research nhận raw OCR provenance.
- **Trạng thái:** `SCAFFOLD` — `extract_text_and_boxes` chưa inference.

## A4 — Nối OCR với layout và reading order

- **Vấn đề / lý do:** Token gần bảng/total/header có ý nghĩa khác; box overlap
  hoặc reading order sai làm hỏng downstream KIE.
- **Primary owner / reviewer:** A / B.
- **Phụ thuộc:** A2 và A3; A1 geometry semantics.
- **Đầu vào:** Layout regions, OCR tokens/polygons, page transform metadata.
- **Các bước:** Chốt containment/overlap rule, tie-break, reading order theo
  layout; xử lý token ngoài region, overlapping region và box rỗng; giữ nguyên
  source geometry và association confidence.
- **Files:** `src/docai/track_a/pipeline.py` hoặc module con chỉ
  khi logic tách biệt và task được duyệt.
- **Đầu ra:** Token records có layout context và deterministic order.
- **PASS:** Không đổi box gốc; mọi token được associate hoặc ghi unassigned;
  same input cho cùng thứ tự.
- **Validation:** Unit cases inside/outside/overlap, table rows/columns, multi-page.
- **Ngoài phạm vi:** Layout label không tự trở thành business field.
- **Bàn giao:** A5 KIE input preparation.
- **Trạng thái:** `PLANNED`.

## A5 — Chuẩn bị input KIE và taxonomy

- **Vấn đề / lý do:** KIE model nhận token/box theo convention cụ thể; sai scale
  hoặc truncation khiến entity sai.
- **Primary owner / reviewer:** A / B; Data owner review annotation mapping.
- **Phụ thuộc:** A1, A3, A4; cần D4 trước khi khóa label map theo dataset.
  Có thể chuẩn bị token/coordinate/truncation contract bằng taxonomy fixture.
- **Đầu vào:** OCR/layout tokens, annotation BIO/field/clause labels, candidate
  document-understanding model requirements.
- **Các bước:** Tokenize/align subword; normalize coordinates; nếu candidate như
  LayoutLMv3 yêu cầu `[0,1000]`, chuyển rõ từ schema/page coordinates; xử lý
  truncation/window overlap; define BIO labels và separate Invoice/Contract
  taxonomy; preserve page/span mapping.
- **Files:** `pipeline.py` (`LayoutLMv3Extractor` scaffold); dataset mapping ở D4.
- **Đầu ra:** Deterministic KIE inputs, label maps và truncation metadata.
- **PASS:** Token/box index align; BIO invalid cases được phát hiện; không mất
  link về page/source; domain labels không trộn.
- **Validation:** Multi-token entities, subword alignment, out-of-range box,
  truncation/window merge fixtures.
- **Ngoài phạm vi:** Không mặc định LayoutLMv3 production model; không sửa annotation
  gốc hoặc test protocol.
- **Bàn giao:** A6 model study và A7 aggregation.
- **Trạng thái:** `SCAFFOLD` — `extract_fields` chưa inference.

## A6 — Chọn model và quyết định inference hay fine-tuning

- **Vấn đề / lý do:** Track A gồm nhiều stage; hard-code một candidate trước khi
  so sánh có thể sai license, domain hoặc resource.
- **Primary owner / reviewer:** A / B; Research review comparison protocol; user
  approval trước resource có cost.
- **Phụ thuộc:** Proposal interface A2–A5 và D1–D5 dataset/license/split
  evidence. A6 chọn candidate trên protocol; các stage chỉ implement provider
  cụ thể sau quyết định đó.
- **Đầu vào:** Stage-specific candidates (layout, OCR, KIE), pretrained/Hugging
  Face provenance, data/annotation coverage, baseline và hardware constraints.
- **Các bước:** Lập matrix candidate/version/license/input/output/resource;
  chạy cùng protocol; quyết định inference-only trước; chỉ đề xuất fine-tuning
  nếu baseline + data size/quality/license + compute + expected gain có bằng
  chứng; so sánh fine-tuning/LoRA chỉ khi có lý do và approval.
- **Files:** Model decision record dự kiến trong docs/tasks hoặc Research report;
  không thêm model config giả vào source.
- **Đầu ra:** Per-stage model decision hoặc `NOT SELECTED`, cùng rationale.
- **PASS:** Mỗi quyết định trace về run/data/license/resource; không giả định
  YOLOv8-doc, DocLayout-YOLO, PaddleOCR hay LayoutLMv3 đã chốt.
- **Validation:** Candidate matrix reviewed; controlled baseline nếu resource
  được duyệt; không đánh giá trên test để tune.
- **Ngoài phạm vi:** Không tải weights/train/fine-tune trong task planning này.
- **Bàn giao:** A3/A5 implementer; RE2/RE3/RE4 nhận metadata.
- **Trạng thái:** `NOT STARTED` — quyết định model vẫn `NOT SELECTED`; chưa có
  candidate được duyệt hoặc run evidence.

## A7 — Gom entity và mapping Invoice/Contract

- **Vấn đề / lý do:** Token predictions cần được gom thành dữ liệu sử dụng được
  mà không mất source trace.
- **Primary owner / reviewer:** A / B; Contract evidence reviewer từ Product.
- **Phụ thuộc:** A1, A5 và PE10 evidence decision. D4 cần trước mapping nhãn
  dataset thật; mapping fixture Invoice/Contract đủ cho runner contract.
- **Đầu vào:** BIO/tag output, OCR tokens/boxes/page, domain taxonomy.
- **Các bước:** Aggregate entity liền nhau; xử lý broken/duplicate/missing
  entity; normalize value chỉ theo rule domain rõ; giữ raw text/confidence/source;
  map Invoice seller/date/tax/total/line item và Contract metadata/clause
  category/text/page/span riêng.
- **Files:** `pipeline.py` (`LayoutLMv3Extractor` scaffold); shared schema.
- **Đầu ra:** Candidate `ExtractedField` / shared output mapping cùng diagnostics.
- **PASS:** Invoice và Contract mapping tách biệt; clause không bị ép thành
  scalar ngắn; không bịa box/page/source text; invalid entity có typed failure.
- **Validation:** Synthetic BIO/entity cases; mapping examples theo từng domain;
  factual correctness chỉ đo bằng ground truth.
- **Ngoài phạm vi:** Không tự đổi risk policy/shared schema hoặc đưa legal/fraud
  verdict.
- **Bàn giao:** A8 runner; PE10 evidence review; RE2/RE3.
- **Trạng thái:** `PLANNED`.

## A8 — Runner Track A và typed errors

- **Vấn đề / lý do:** Product/Research cần gọi một boundary ổn định thay vì biết
  internals của từng model.
- **Primary owner / reviewer:** A / B; PE reviewer.
- **Phụ thuộc:** A1–A5, A7 mock mapping và PE1/G1 shared-contract approval.
  A6 và D4 là prerequisite cho adapter inference/mapping trên dữ liệu thật;
  runner contract có thể dựng bằng mock adapter và taxonomy fixture trước đó.
- **Đầu vào:** Page/document input, DocumentType, selected stage adapters,
  metadata/error policy.
- **Các bước:** Orchestrate pages/layout/OCR/association/KIE/mapping; trả
  `pipeline_track=track_a_classic`; ghi model/version/config khi thật có; giữ
  stage-level errors; timing chỉ khi đo thật; thiếu model báo `unavailable`.
- **Files:** `src/docai/track_a/`; public export
  `__init__.py`; CLI `src/docai/track_a/__main__.py`.
- **Đầu ra:** Runner interface trả `UnifiedDocumentOutput` hoặc typed error.
- **PASS:** Product gọi được không import model internals; schema validate;
  thiếu inference trả typed unavailable; Invoice/Contract cùng boundary. Mock
  runner pass chỉ là contract pass, không phải inference pass.
- **Validation:** Contract tests với fixture, invalid input/model missing/stage
  failure; end-to-end inference chỉ sau model/data/resource approval.
- **Ngoài phạm vi:** Không đặt business orchestration trong CLI/FastAPI route.
- **Bàn giao:** PE4 integration; RE4/RE5 handoff.
- **Trạng thái:** `NOT STARTED` — runner/mock contract chưa được triển khai;
  real inference tiếp tục chờ A6/model/resource decision.

## A9 — Tests, diagnostics và Research handoff

- **Vấn đề / lý do:** Một output sai không thể sửa tốt nếu không biết lỗi đến từ
  layout, OCR, KIE hay mapping.
- **Primary owner / reviewer:** A / B; Research reviewer.
- **Phụ thuộc:** A2–A5, A7 và A8 mock contract cho unit/diagnostic pass. A6 và
  D5 chỉ bắt buộc cho diagnostics/inference trên model và dữ liệu thật; RE1/D5
  bắt buộc trước metric handoff.
- **Đầu vào:** Runner, fixtures, approved data, model metadata và run conditions.
- **Các bước:** Thêm unit tests cho geometry/association/token/BIO/mapping/errors;
  stage diagnostics/counts; safe run record có model/checkpoint, preprocessing,
  hardware, input scope, versions và failures; bàn giao sample đã khử nhạy cảm.
- **Files:** `tests/` shared chỉ cho contract/integration; Track-specific tests
  dưới `tests/track_a/` chỉ tạo khi có nội dung thật và được thống nhất.
- **Đầu ra:** Test evidence và Research handoff bundle/template.
- **PASS:** Deterministic transformations có coverage; logs không chứa key/full
  document; real metrics chỉ có ground truth/run tái lập; fixture ghi test-only.
- **Validation:** Targeted tests/compile theo code task; không cần tải data/model
  cho unit cases.
- **Ngoài phạm vi:** Không bịa Precision/Recall/F1 hoặc dùng test split để chọn
  threshold/model.
- **Bàn giao:** PE9 cho contract/E2E; RE2–RE8 cho experiment.
- **Trạng thái:** `NOT STARTED`.
