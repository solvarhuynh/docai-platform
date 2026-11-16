# Track B VLM — kế hoạch công việc chi tiết

## Track B giải quyết việc gì?

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

## Audit code thật tại thời điểm viết kế hoạch

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

## B0 — Audit repository và shared contract

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

## B1 — Chốt model-agnostic adapter contract

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

## B2 — Chuẩn bị ảnh/PDF nhiều trang

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

## B3 — Version prompt riêng theo domain

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

## B4 — So sánh VLM candidates và chọn inference/fine-tuning

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

## B5 — Parse structured response có lỗi thực tế

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

## B6 — Validate schema và normalize an toàn

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

## B7 — Map Invoice/Contract evidence trung thực

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

## B8 — Timeout, retry, logging và request tracing

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

## B9 — Track B runner và tests

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

## B10 — Research handoff theo model candidate

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
