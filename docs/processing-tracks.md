# DocAI và hai cách xử lý tài liệu

Tài liệu này giới thiệu luồng Document Intelligence, contract dữ liệu và hai
processing engine của repo. Đối tượng đọc là người biết lập trình hoặc Data
Engineering nhưng chưa làm AI/ML thường xuyên.

## Từ tài liệu đến dữ liệu có cấu trúc

Con người nhìn hóa đơn và thấy người bán, ngày, bảng hàng và tổng tiền. Máy
tính ban đầu chỉ nhận các điểm ảnh (**pixel**). Hợp đồng khó hơn vì thông tin
có thể trải dài qua nhiều trang và nằm trong các clause có ý nghĩa pháp lý.

```text
ảnh/PDF → đọc chữ + vị trí → hiểu ý nghĩa → field/clause → JSON có cấu trúc
```

**OCR (Optical Character Recognition)** đọc chữ từ ảnh. Với dòng
`Total: 500.000đ`, OCR chuyển pixel thành text để xử lý tiếp, nhưng có thể đọc
sai ký tự và chưa biết số đó là total, tax hay giá một dòng hàng.

Vị trí cũng quan trọng. **Bounding box** là hình chữ nhật chỉ vị trí của chữ
hoặc vùng, thường có dạng `[xmin, ymin, xmax, ymax]`. Số nằm cạnh nhãn `Total`
có thể là tổng tiền; số trong bảng có thể là giá một sản phẩm.
**Layout Detection** tìm các vùng như header, table, signature và total.

**Field** là giá trị có tên như `invoice_date` hoặc `total_amount`.
**Clause** là đoạn có ý nghĩa trong hợp đồng, ví dụ termination clause.
`DocumentType` cho biết tài liệu là `invoice`, `receipt`, `contract` hay
`unknown`, để backend chọn mapping và risk rules theo đúng domain.

## Vì sao cần output có schema?

Text rời rạc chưa đủ cho kế toán hay phần mềm khác. **Structured Output** là
kết quả có hình dạng ổn định. Trong DocAI, `UnifiedDocumentOutput` chứa loại
tài liệu, danh sách field, confidence, risk flags và metadata. **Pydantic**
kiểm tra hình dạng object Python; FastAPI gửi dữ liệu qua JSON tới React.

```text
Track A ─┐
         ├→ UnifiedDocumentOutput → FastAPI JSON → React
Track B ─┘
```

Schema hợp lệ chỉ có nghĩa dữ liệu đúng hình dạng, không chứng minh nội dung
trích xuất đúng với tài liệu. Accuracy cần ground truth và evaluation riêng.
Python source of truth và TypeScript mirror được mô tả trong
[kiến trúc repository](architecture.md).

## Track A: pipeline nhiều specialist

Track A chia xử lý thành các stage riêng. Đây là engine bên trong sản phẩm,
không phải product độc lập và không bắt buộc chỉ dùng một model.

```text
Document → Layout Detection → OCR → Document Understanding/KIE
         → mapping Invoice field hoặc Contract clause
         → UnifiedDocumentOutput
```

Nếu `total_amount` bị mất, có thể lần theo từng stage: layout có cắt nhầm vùng
không, OCR có đọc sai không, hay bước hiểu tài liệu gán nhãn nhầm? Nhược điểm
là **error cascade**: stage sau thường không khôi phục được thông tin mà stage
trước đã bỏ sót.

**Layout Detection** tìm và phân loại vùng như `table`, `header`, `total`.
Các model họ YOLO là candidate, chưa phải quyết định production. **NMS** loại
bỏ các box trùng; **IoU** đo mức giao nhau giữa hai box.

**OCR** gồm text detection (tìm vị trí chữ) và text recognition (đổi vùng chữ
thành Unicode). OCR giữ text, confidence và polygon/box. Có thể đổi polygon
thành rectangle bằng tọa độ min/max. Token OCR nằm trong layout region nào có
thể nhận region đó làm context.

**KIE (Key Information Extraction)** gán ý nghĩa nghiệp vụ cho text. OCR có
thể trả token `Total`, `amount`, `1,500,000`; KIE xác định số nào là
`total_amount`. **LayoutLMv3** là Transformer kết hợp text token, box 2D và
visual patch, để tận dụng quan hệ như số tiền nằm cạnh nhãn Total.

- **Token:** đơn vị nhỏ model xử lý; một từ có thể tách thành nhiều token.
- **Embedding:** biểu diễn số của token hoặc ảnh để model xử lý.
- **Attention:** cơ chế cân nhắc context nào ảnh hưởng tới dự đoán. Đây là tín
  hiệu nội bộ, không tự nó là bằng chứng giải thích hoàn hảo.
- LayoutLM thường dùng tọa độ `[0, 1000]`; schema DocAI có thể dùng `[0, 1]`.
  Phải chuyển đổi rõ ở boundary.

KIE có thể dùng **BIO tagging** để gắn field nhiều token: `B-SELLER` bắt đầu
field, `I-SELLER` tiếp tục field, `O` nằm ngoài field. Aggregation ghép token
liền nhau và có thể tạo union box.

**Pretrained model** đã học pattern tổng quát từ dữ liệu trước đó;
**fine-tuning** điều chỉnh model cho task hẹp hơn; **checkpoint** là trạng
thái model đã lưu; **inference** dùng checkpoint xử lý tài liệu mới. Invoice
cần seller/date/tax/total, còn Contract cần clause span, page context và
taxonomy riêng. Checkpoint production Track A chưa được chọn; implementation
hiện ở trạng thái `SCAFFOLD`.

## Track B: xử lý VLM-native

**VLM (Vision-Language Model)** xử lý hình ảnh và ngôn ngữ cùng lúc. Track B
đưa ảnh tài liệu và structured prompt vào model, sau đó parse và validate
response.

```text
Invoice/Contract image + instruction
  → VLM inference → candidate response
  → parse + schema validation → UnifiedDocumentOutput
```

“Single-pass” chỉ mô tả phần model-facing. Chuẩn bị input, validation, retry,
logging và mapping vẫn là các bước riêng.

Ở mức khái niệm, vision encoder chuyển patch ảnh thành biểu diễn số;
language model xử lý instruction và token; connector kết hợp thông tin ảnh và
chữ. **Multimodal** nghĩa là dùng nhiều dạng input. **Prompt** là instruction
gửi cho model. Structured prompt nêu document type, field/clause cần lấy,
cách biểu diễn giá trị thiếu, evidence và JSON shape. Invoice có thể yêu cầu
seller/date/tax/total; Contract có thể yêu cầu termination/renewal/payment
clause cùng page evidence.

**Hallucination** là nội dung nghe hợp lý nhưng không có trong tài liệu. Ví dụ
model tự điền tax number không xuất hiện trên invoice, hoặc tự tạo renewal
clause cho hợp đồng. Prompt yêu cầu trả “không tìm thấy”, schema validation và
evidence giúp phát hiện hoặc giảm lỗi, nhưng không bảo đảm kết quả đúng.

Track A giống nhiều specialist; Track B giống generalist có thể đổi tác vụ
bằng prompt. Một VLM không tự động giỏi mọi domain: cả Invoice và Contract
vẫn cần taxonomy, validation và evaluation riêng. Chỉ map response đã validate
sang `UnifiedDocumentOutput`; không trả raw response thẳng cho browser.
PaddleOCR-VL và dots.ocr còn là candidate; model Track B chưa được chọn và
parser hiện là `SCAFFOLD`.

## Cách so sánh hai track

Hai track có thể khác implementation nhưng cùng trả `UnifiedDocumentOutput`.
Research so sánh value, missing field, confidence, evidence và
agreement/disagreement trên cùng domain, ground truth và protocol. Hai track
đồng ý với nhau không chứng minh kết quả đúng; bất đồng là mẫu cần review.
Không kết luận track nào tốt hơn chỉ từ kiến trúc.
