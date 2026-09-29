# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** VoPhuHan
- **MSSV:** 2A202602628
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/yohan-vinai/K4-L3A-Day13-Monitoring-LLMOps
- **Commit SHA cuối:** Chưa chốt; xem commit cuối trên repository sau khi hoàn tất Langfuse/CP3
- **Challenge ID:** Chờ Lab Coach release challenge riêng cho K4-L3A tại CP3

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.txt` |
| Log validator | `evidence/02-log-validator.txt` |
| Dashboard validator | `evidence/03-dashboard-validator.txt` |
| Structured log | `evidence/04-structured-log.txt` |
| PII redaction | `evidence/05-pii-redaction.txt` |
| Trace list | Chưa tạo; tự tạo project/key Langfuse cá nhân theo `docs/SETUP.md` rồi chạy workload |
| Trace waterfall | Chưa có; cần traces trong project Langfuse cá nhân |
| Trace metadata | Chưa có; cần traces trong project Langfuse cá nhân |
| Prompt versions | Chưa tạo; thực hiện trong project Langfuse cá nhân |
| Prompt rollback | Chưa thực hiện; thực hiện trong project Langfuse cá nhân |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | Chờ challenge release của Lab Coach |
| Incident log | Chờ challenge release của Lab Coach |
| Incident trace | Chờ challenge CP3; trace phải nằm trong project Langfuse cá nhân |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | Chưa đo trước khi sửa | 100/100 | 25 bản ghi, 12 correlation IDs; không thiếu metadata, không phát hiện PII |
| `validate_dashboard.py` | Chưa đo trước khi sửa | 6/6 panel | Dashboard contract hợp lệ; runtime JSON và screenshot được lưu |
| `pytest` | Chưa đo trước khi sửa | 26 passed | Chạy local trên commit hiện tại |
| Số traces hợp lệ | Chưa có | 0 | Chưa tự tạo project/key Langfuse cá nhân; app đang tracing-disabled vì hai key trong `.env` đang trống |
| Số PII leak | Chưa đo trước khi sửa | 0 | Validator không phát hiện PII trong log hiện tại |
| Latency P95 / TTFT P95 | Chưa đo trước khi sửa | 162 ms / 55 ms | Mock practice snapshot với 23 requests; xem dashboard runtime JSON/screenshot |
| Retrieval success rate | Chưa đo trước khi sửa | 100% | Mock practice workload; không đại diện dịch vụ thật |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware nhận `x-request-id` hợp lệ dạng `req-<8-hex>`, nếu thiếu/sai định dạng thì sinh ID; bind vào request context và trả lại cùng `x-response-time-ms`.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env`, `correlation_id`, latency/token/cost/quality và payload preview đã rút gọn.
- **Cách bảo đảm PII được scrub trước khi ghi:** Structlog processor đệ quy scrub mọi chuỗi trong event dictionary trước JSONL file writer và JSON renderer. Pattern gồm email, điện thoại VN, CCCD và thẻ thanh toán.
- **Cách kiểm chứng kết quả:** `validate_logs.py` đạt 100/100; request practice có correlation ID được trả lại; sample log cho thấy email/điện thoại/CCCD đã che; tests gồm kiểm tra cả số thẻ giả.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Chưa có trace; hai key trong `.env` đang trống. Hướng dẫn yêu cầu mỗi học viên tự tạo project và key, không cần chờ Lab Coach.
- **Cấu trúc root/retrieval/generation observations:** Đã thêm child observation cho retriever và generation; test xác nhận cấu trúc, model, prompt reference, token usage và cost. Input/output không ghi raw prompt/answer. Chưa xác minh waterfall live vì chưa cấu hình key project cá nhân.
- **Cách nối trace với log:** Root trace metadata nhận correlation ID cùng feature/model; session ID được hash trước khi gắn vào trace.
- **Prompt name:** `day13-chat` (cấu hình mặc định; chưa xác minh trên Langfuse project).
- **Version/label baseline:** Chưa tạo trên Langfuse.
- **Version/label candidate:** Chưa tạo trên Langfuse.
- **Trace ID của mỗi version:** Chưa có.
- **Cách promote và rollback `production`:** Chưa thực hiện; có thể làm sau khi tự tạo project Langfuse cá nhân và cấu hình API key riêng.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Dashboard local tại `/dashboard`, đọc JSONL đã scrub, time range 60 phút, refresh 30 giây, có latency/TTFT, traffic, errors/retrieval, cost, tokens và quality. Runtime screenshot: `evidence/11-dashboard-overview.png`.
- **SLO và lý do chọn:** `fast_successful_requests` mục tiêu 99.5% trong cửa sổ trượt 28 ngày; request tốt là response thành công trong tối đa 3000 ms.
- **Cách tính error budget:** `100% - 99.5% = 0.5%`; tương đương 50 request không đạt trên mỗi 10,000 request trong cửa sổ SLO.
- **Ba alert và runbook tương ứng:** Availability error rate >2% trong 5 phút (critical), latency P95 >3000 ms trong 10 phút, retrieval success <90% trong 5 phút; cấu hình ở `config/alert_rules.yaml`, hướng dẫn ở `docs/alerts.md`.

## 7. Điều tra challenge

- **Challenge ID:** Chờ Lab Coach xác nhận challenge K4-L3A đã release.
- **Khoảng thời gian điều tra:** Chưa chạy challenge.
- **Triệu chứng từ metrics:** Chưa có.
- **Log line và correlation ID liên quan:** Chưa có.
- **Trace ID và span gây ảnh hưởng:** Chưa có; chờ challenge chính thức và cần key project Langfuse cá nhân để tạo trace.
- **Root cause:** Chưa kết luận.
- **Fix action:** Chưa kết luận.
- **Preventive measure:** Chưa kết luận.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Dashboard lấy `data/logs.jsonl` làm nguồn chính theo contract; PII scrub chạy trước file writer để giữ an toàn cho cả file lẫn console.
- **Một lỗi/blocker đã gặp:** File `.env` có Langfuse keys rỗng khiến SDK khởi tạo exporter và trả 401.
- **Cách tìm nguyên nhân và xử lý:** Kiểm tra trạng thái key theo dạng có/không, đối chiếu hành vi Langfuse SDK v4, rồi đặt client no-op khi thiếu credentials. Chạy lại API: không còn request export; health báo tracing disabled.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics khoanh triệu chứng và thời gian; `correlation_id` tìm request trong log; trace của cùng ID chỉ ra span gây chậm/lỗi.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Chưa có evidence runtime cho prompt/rollback; phần config đã giữ lại correlation giữa version, usage/cost và request để truy nguyên khi Langfuse sẵn sàng.
- **Điều quan trọng nhất đã học:** Chưa điền; học viên tự hoàn thiện sau khi làm challenge và demo.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Cần tự tạo Langfuse project/key để thu trace và prompt evidence; CP3 chờ Lab Coach release challenge riêng. Số liệu dashboard hiện tại chỉ từ fake LLM practice.

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
