# Hướng dẫn AI agent — DocAI

Đọc toàn bộ file này và README.md trước khi sửa. Đọc thêm docs/architecture.md,
task plan và source/test liên quan. AGENTS.md gần file sửa nhất có thể bổ sung
hướng dẫn. Source và test quyết định hiện trạng; plan không chứng minh tính năng.

## Mục đích và khái niệm

DocAI thử nghiệm Document Intelligence cho hai domain ngang hàng: Invoice/
Receipt và Contract. Cả Track A (Classic layout → OCR → KIE) và Track B
(VLM-native) đều hướng tới cả hai domain. Product trả UnifiedDocumentOutput
để người dùng rà soát; Research chỉ đo bằng output thật và ground truth đã xác
minh. Fixture/mock chỉ chứng minh hành vi deterministic.

- Domain task: việc nghiệp vụ, như Invoice field hoặc Contract clause extraction.
- Track: hướng xử lý tài liệu; mỗi track có thể chứa nhiều model.
- Model: checkpoint hoặc dịch vụ cụ thể chạy ở một hay nhiều stage.
- Pipeline: chuỗi bước từ input, inference, mapping đến output.
- Adapter: lớp nối giao diện Track với model/provider.
- Ground truth: annotation tham chiếu đã xác minh.
- Fixture: dữ liệu deterministic cho test, không phải benchmark.

Không đồng nhất Track với model hoặc domain. Contract clause cần nội dung và
nguồn/trang; không ép thành scalar ngắn. Không tự tạo evidence, confidence hoặc
risk khi engine chưa cung cấp.

## Ownership và ranh giới

- Thành viên A sở hữu src/docai/track_a/, tests/track_a/, notebooks/track_a/.
- Thành viên B sở hữu src/docai/track_b/, tests/track_b/, notebooks/track_b/.
- Hai thành viên cùng review src/docai/shared/ và src/docai/api.py khi đổi
  contract hoặc API semantics. Một task vẫn cần một primary owner.
- Data Foundation, Product Engineering, Research và reviewer theo
  [plan chung](docs/tasks/shared.md); [Track A](docs/tasks/track-a.md) và
  [Track B](docs/tasks/track-b.md) có task riêng. Frontend owner chưa chốt.
- track_a và track_b chỉ import docai.shared; không import lẫn nhau.
  API điều phối qua runner boundary, không chứa model/prompt internals.

Schema Python là src/docai/shared/schema.py; browser mirror là
frontend/src/types/document.ts. Mọi thay đổi contract phải xem cả hai,
backward compatibility và cross-owner review. Schema-valid không chứng minh
nội dung đúng tài liệu. Route parse hiện trả 501, không có inference thật.

## Nhãn trạng thái và giới hạn

- IMPLEMENTED: có code và bằng chứng kiểm tra phù hợp.
- BASELINE: nền nhỏ đã kiểm tra trong phạm vi nêu rõ.
- SCAFFOLD: interface/utility/placeholder, runtime chính chưa xong.
- PLANNED: chỉ có trong kế hoạch.
- NOT SELECTED: model/provider/candidate chưa quyết định.
- BLOCKED: prerequisite cụ thể chưa đạt.
- NOT RUN: validation/runtime chưa chạy.

Hiện health route IMPLEMENTED; schema/config BASELINE; Track A/B inference
SCAFFOLD; model NOT SELECTED; data/ground truth/evaluation thật chưa có.
Risk chỉ có type, chưa có rule runtime; Contract span model riêng chưa có.
Compile/build hoặc fixture pass không phải benchmark/inference pass.

Không train/fine-tune, tải weights/dataset, gọi paid API/GPU, deploy hoặc thêm
service/framework khi task chưa cho phép. Không đưa secret, dữ liệu nhạy cảm,
checkpoint hay raw response vào Git/log. Không dùng test split để chọn model,
threshold hoặc prompt. Raw data, processed data, ground truth, fixture và model
output phải được phân biệt và truy nguồn.

## Bắt đầu một task

1. Chạy git branch --show-current và git status --short --branch; ghi nhận
   file đã sửa, xóa, untracked. Không reset, stash, clean hoặc ghi đè của user.
2. Xác định task ID, primary owner, reviewer, input/output, dependency/gate,
   validation và điều kiện dừng trong plan tương ứng.
3. Đọc source/test thật bằng rg; tìm path hiện có trước khi tạo hoặc move file.
4. Chỉ sửa scope được giao. Reusable Python logic ở src/docai/; CLI của track
   ở __main__.py. Import qua docai.*, không chèn sys.path.
5. Theo gate: fixture cho contract work khi task cho phép, không nâng mock
   thành inference thật. Contract/API/risk/evaluation semantics cần review
   trước khi implementation phụ thuộc.
6. Xem diff/status trước khi stage path cụ thể. Chỉ commit/push khi user yêu
   cầu rõ hoặc workflow hiện hành quy định; không commit trực tiếp vào main.
7. Bàn giao file/output, nhãn trạng thái, lệnh validation và PASS/FAIL/NOT RUN,
   giới hạn, owner/task tiếp theo, blocker; nêu có dùng model/data/API/GPU không.

Nếu canonical docs mâu thuẫn về semantics, working tree có nguy cơ bị ghi đè,
thiếu review cho shared contract, hoặc cần resource chưa duyệt, dừng phần bị
ảnh hưởng và tiếp tục phần độc lập. Không giảm requirement để cho task PASS.

## Tài liệu và kiểm tra

README.md là nguồn duy nhất cho cây repo và cách chạy; docs/architecture.md
giải thích kiến trúc; docs/tasks/ là kế hoạch. Tài liệu hướng dẫn viết tiếng
Việt UTF-8, phân biệt code hiện có với plan/candidate. Sửa link khi move file.
Chọn phép kiểm tra nhỏ nhất chứng minh thay đổi, không gọi model/GPU mặc định.
