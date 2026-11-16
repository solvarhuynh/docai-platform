# Data Foundation — kế hoạch công việc

## Vì sao cần một workstream dữ liệu?

Invoice/Receipt và Contract có nhãn, định dạng và cách chia dữ liệu khác nhau.
Nếu hai Track tự tải và chuyển đổi dữ liệu riêng, chúng có thể đánh giá những
tập khác nhau hoặc làm mất nhãn gốc. Data Foundation chuẩn bị dữ liệu có thể
truy nguyên cho Track A, Track B và Research; workstream này không triển khai
model.

**Primary owner:** Thành viên B — Data Engineering. **Reviewer:** Thành viên A.
**Collaborator:** Track owners cung cấp input requirements; Research duyệt
ground truth/split trước khi đánh giá.

## Trạng thái hiện tại

Trong repo, `data/raw/` và `data/processed/` chỉ có `.gitkeep`; không thấy data
file hoặc manifest. Vì vậy CORD v2, SROIE, MC-OCR 2021, CUAD v1 và DocILE đều
là **candidate trong kế hoạch, chưa xác nhận đã tải, quyền truy cập, license,
integrity hay phù hợp phiên bản**. Không commit dataset. `data/interim/` không
có trong cây hiện tại.

## Dataset ứng viên

| Domain | Candidate | Dùng để tìm hiểu; chưa phải lựa chọn/approval |
|---|---|---|
| Invoice/Receipt | CORD v2 | Xác minh release, license, annotation, format và domain coverage |
| Invoice/Receipt | SROIE | Xác minh nguồn/release, license, task labels và split |
| Invoice/Receipt | MC-OCR 2021 | Xác minh access terms, ngôn ngữ, annotation và split |
| Contract | CUAD v1 | Xác minh license/source, clause taxonomy, annotation granularity và split |
| Optional | DocILE | Chỉ xem xét nếu bổ sung câu hỏi nghiên cứu rõ và license/resource phù hợp |

## D0 — Audit EDA notebook và tình trạng data artifacts

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

## D1 — Lập kế hoạch acquisition và license

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

## D2 — Quản lý raw data, manifest và integrity

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

## D3 — Kiểm kê và kiểm tra chất lượng dataset

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

## D4 — Mapping annotation mà không mất nhãn gốc

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

## D5 — Chốt split và ngăn data leakage

- **Vấn đề / lý do:** Tài liệu trùng/biến thể giữa train, validation và test có
  thể làm metric cao giả.
- **Primary owner / reviewer:** B / A; Research bắt buộc review.
- **Phụ thuộc:** D3 và D4 PASS; xem xét split gốc trước mọi thay đổi.
- **Đầu vào:** Split chính thức, document IDs, duplicate audit và mapping.
- **Các bước:** Ghi split nguồn; kiểm tra duplicate/near-duplicate và cùng
  contract/vendor/template xuyên split; giữ nguyên official split trừ khi có
  protocol approved; tạo split mới chỉ khi có lý do, seed và group key rõ.
- **Files:** Split metadata/manifest dự kiến dưới `data/metadata/` ngoài payload
  lớn; protocol tại `docs/tasks/research-evaluation-tasks.md`.
- **Đầu ra:** Version/hash của split và leakage report.
- **PASS:** Không có leakage chưa giải thích; mọi exclusion/change có lý do,
  seed, count và review; test set không dùng để chọn threshold/model.
- **Validation:** Script kiểm tra ID overlap, group overlap và checksum.
- **Ngoài phạm vi:** Không trộn split tiện tay, không tune trên test set.
- **Bàn giao:** RE1 khóa protocol; candidate evaluation chỉ dùng split được duyệt.
- **Trạng thái:** `BLOCKED` — chờ dataset/annotation.

## D6 — Định nghĩa processed-data contract

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

## D7 — Phát hành data quality report

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

## Handoff và từ vựng trạng thái dữ liệu

Mỗi dataset ghi một trong `CANDIDATE`, `LICENSE REVIEW`, `APPROVED FOR
ACQUISITION`, `DOWNLOADED`, `INTEGRITY VERIFIED`, `ANNOTATION MAPPED` và
`EVALUATION READY`. Chỉ nâng status khi có manifest/report tương ứng. Raw,
processed, annotation/ground truth, fixture và model output có đường dẫn/nhãn
riêng; không dùng fixture để tuyên bố dataset hoặc benchmark thật.
