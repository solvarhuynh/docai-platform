# Research & Evaluation — kế hoạch công việc

## Research trả lời câu hỏi nào?

Research so sánh Track A/B và từng model candidate trên Invoice/Receipt lẫn
Contract. Kết quả phải dựa trên output inference thật, ground truth được kiểm
tra và protocol có version. Product workspace trả kết quả phục vụ người dùng;
Research giải thích mức chính xác, failure, độ bền, latency, cost và evidence.

**Primary owner chung:** Thành viên B dẫn dắt protocol, dataset và experiment
plumbing. **Reviewer:** Thành viên A. RE7 về model/evidence interpretation do
A dẫn dắt, B review. Mỗi task vẫn có một primary owner.

## Trạng thái hiện tại

Trong source hiện có shared schema/config/API tests; không thấy evaluation
package, ground-truth dataset, model output hoặc benchmark artifact. Frontend
Research page chỉ có nhãn metric và trạng thái `PLANNED`. Không có metric thật.

## RE1 — Khóa evaluation protocol

- **Vấn đề / lý do:** Kết quả không so sánh được nếu khác split, taxonomy,
  normalization hoặc evaluation unit.
- **Primary owner / reviewer:** B / A; D owner cung cấp provenance.
- **Phụ thuộc:** D3–D5; PE1 shared contract; Track A/B nêu output fields.
- **Đầu vào:** Dataset version/license, annotation mapping, source split,
  Invoice/Contract taxonomy và model output format.
- **Các bước:** Chốt dataset/release/hash/split; unit (document/page/field/clause);
  inclusion/exclusion; missing-value/duplicate policy; exact và normalized
  matching; aggregation/confidence intervals nếu đủ mẫu; test-set isolation.
- **Files:** `docs/tasks/data-foundation-tasks.md`, PE1 contract và protocol
  artifact dự kiến trong `docs/` trước khi chạy.
- **Đầu ra:** Versioned protocol, metric definitions và run manifest template.
- **PASS:** A, Data owner và cả Track owners review; Invoice/Contract tách rõ;
  một run độc lập có thể tái tạo split/metric; test set không dùng để chọn model.
- **Validation:** Protocol review bằng fixture minh họa, không công bố metric.
- **Ngoài phạm vi:** Không tự chọn model, không tính benchmark từ fixture.
- **Bàn giao:** RE2/RE3 và mọi candidate evaluation.
- **Trạng thái:** `NOT STARTED` — chưa có ground truth được xác minh.

## RE2 — Định nghĩa Invoice/Receipt evaluation

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

## RE3 — Định nghĩa Contract evaluation

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

## RE4 — So sánh Track công bằng

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

## RE5 — Đo latency và cost

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

## RE6 — Đo robustness

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

## RE7 — Đánh giá evidence và explainability

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

## RE8 — Viết report tái lập

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
