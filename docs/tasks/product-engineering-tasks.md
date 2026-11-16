# Product Engineering — kế hoạch công việc

## Sản phẩm cần làm gì?

Product Engineering nối người dùng với hai processing Track và shared result.
Frontend hiện dùng React, TypeScript, Vite, HTML/CSS; backend duy nhất là
Python/FastAPI/Pydantic. Node chỉ phục vụ frontend tooling. Không tạo Node
business backend, gọi model provider từ browser hoặc hiển thị extraction/metric
giả.

**Primary owner API/integration:** Thành viên B. **Reviewer:** Thành viên A
review contract và runner boundary. **React owner:** chưa được chỉ định trong
tài liệu/repo hiện có; nhóm cần chốt người trước PE2/PE5–PE7, không suy đoán.

## Trạng thái code hiện tại

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

## PE1 — Chốt shared API contract

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

## PE2 — Thiết kế upload flow ở browser

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

## PE3 — Nhận và validate upload trong FastAPI

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

## PE4 — Điều phối Track qua runner boundary

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

## PE5 — Invoice Intelligence Workspace

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

## PE6 — Contract Intelligence Workspace

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

## PE7 — Research Lab cho kết quả có nguồn

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

## PE8 — Request lifecycle, loading và lỗi

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

## PE9 — Tích hợp end-to-end

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

## PE10 — Shared Risk và Evidence contract

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

## Quyết định còn thiếu

Nhóm cần chỉ định React primary owner và UI reviewer trước PE2/PE5–PE7. Không
chặn PE1/PE3 backend contract work để chờ quyết định UI; không chuyển UI ownership
sang B chỉ vì B làm API.
