# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** VoPhuHan
- **MSSV:** 2A202602628
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/yohan-vinai/K4-L3A-Day13-Monitoring-LLMOps
- **Commit SHA cuối:** Xem `HEAD` của repository cá nhân sau khi push (SHA không thể tự ghi trong chính commit đó vì nội dung thay đổi sẽ sinh SHA mới)
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
| Trace list, waterfall, metadata, correlation IDs, prompt versions/rollback | `evidence/06-langfuse-traces.txt` (Langfuse API readback; UI screenshots cần chụp riêng) |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | Chờ challenge release của Lab Coach |
| Incident log | Chờ challenge release của Lab Coach |
| Incident trace | Chờ challenge CP3; trace phải nằm trong project Langfuse cá nhân |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | Chưa đo trước khi sửa | 100/100 | 52 bản ghi, 24 correlation IDs; không thiếu metadata, không phát hiện PII |
| `validate_dashboard.py` | Chưa đo trước khi sửa | 6/6 panel | Dashboard contract hợp lệ; runtime JSON và screenshot được lưu |
| `pytest` | Chưa đo trước khi sửa | 26 passed | Chạy local trên commit hiện tại |
| Số traces hợp lệ | Chưa có | 12 | Langfuse Cloud API xác nhận 12 root trace, mỗi trace có retrieval/generation child observations |
| Số PII leak | Chưa đo trước khi sửa | 0 | Validator không phát hiện PII trong log hiện tại |
| Latency P95 / TTFT P95 | Chưa đo trước khi sửa | 162 ms / 55 ms | Mock practice snapshot với 23 requests; xem dashboard runtime JSON/screenshot |
| Retrieval success rate | Chưa đo trước khi sửa | 100% | Mock practice workload; không đại diện dịch vụ thật |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware nhận `x-request-id` hợp lệ dạng `req-<8-hex>`, nếu thiếu/sai định dạng thì sinh ID; bind vào request context và trả lại cùng `x-response-time-ms`.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env`, `correlation_id`, latency/token/cost/quality và payload preview đã rút gọn.
- **Cách bảo đảm PII được scrub trước khi ghi:** Structlog processor đệ quy scrub mọi chuỗi trong event dictionary trước JSONL file writer và JSON renderer. Pattern gồm email, điện thoại VN, CCCD và thẻ thanh toán.
- **Cách kiểm chứng kết quả:** `validate_logs.py` đạt 100/100; request practice có correlation ID được trả lại; sample log cho thấy email/điện thoại/CCCD đã che; tests gồm kiểm tra cả số thẻ giả.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** `.env` có key pair; Langfuse API xác nhận 12 traces trong project đang được key sử dụng. Project hiện có tên `My Project`; nên đổi tên trong Langfuse UI thành `day13-k4-l3a-2A202602628` theo quy ước của lab.
- **Cấu trúc root/retrieval/generation observations:** Đã kiểm tra waterfall live: `lab-agent-run` có hai child `knowledge-retrieval` và `chat-completion`. Root input/output không được capture; child input/output đã rà PII với 0 mẫu khớp email/điện thoại/CCCD/thẻ.
- **Cách nối trace với log:** Correlation ID cùng feature/model xuất hiện trong metadata trace và structured log; session ID được hash trước khi gắn vào trace. Bảng ID nằm trong `evidence/06-langfuse-traces.txt`.
- **Prompt name:** `day13-chat`, đọc thành công từ Langfuse project.
- **Version/label baseline:** Version 1 có `baseline` và `production`.
- **Version/label candidate:** Version 2 có `candidate`; đã tạo trace chọn label `candidate`.
- **Trace ID của mỗi version:** Có trace version 1 và version 2 trong `evidence/06-langfuse-traces.txt`; trace version 2 cũng ghi nhận lúc production được promote.
- **Cách promote và rollback `production`:** Chuyển `production` từ version 1 sang version 2, gửi request và đọc lại trace ghi prompt version 2; sau đó gắn `production` lại version 1 và API xác nhận production hiện resolve về version 1.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Dashboard local tại `/dashboard`, đọc JSONL đã scrub, time range 60 phút, refresh 30 giây, có latency/TTFT, traffic, errors/retrieval, cost, tokens và quality. Runtime screenshot: `evidence/11-dashboard-overview.png`.
- **SLO và lý do chọn:** `fast_successful_requests` mục tiêu 99.5% trong cửa sổ trượt 28 ngày; request tốt là response thành công trong tối đa 3000 ms.
- **Cách tính error budget:** `100% - 99.5% = 0.5%`; tương đương 50 request không đạt trên mỗi 10,000 request trong cửa sổ SLO.
- **Ba alert và runbook tương ứng:** Availability error rate >2% trong 5 phút (critical), latency P95 >3000 ms trong 10 phút, retrieval success <90% trong 5 phút; cấu hình ở `config/alert_rules.yaml`, hướng dẫn ở `docs/alerts.md`.

## 7. Điều tra challenge

- **Challenge ID:** Chờ Lab Coach release challenge riêng K4-L3A; `config/challenge.json` hiện chưa có.
- **Khoảng thời gian điều tra:** Chưa chạy challenge.
- **Triệu chứng từ metrics:** Chưa có.
- **Log line và correlation ID liên quan:** Chưa có.
- **Trace ID và span gây ảnh hưởng:** Chưa có; chờ challenge chính thức và cần key project Langfuse cá nhân để tạo trace.
- **Root cause:** Chưa kết luận.
- **Fix action:** Chưa kết luận.
- **Preventive measure:** Chưa kết luận.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Dashboard lấy `data/logs.jsonl` làm nguồn chính theo contract; PII scrub chạy trước file writer để giữ an toàn cho cả file lẫn console.
- **Một lỗi/blocker đã gặp:** Ban đầu hai Langfuse key rỗng làm SDK export thất bại; đã xử lý no-op khi thiếu credential. Sau khi a tự tạo và nạp key, tracing được bật và trace live đã xác nhận.
- **Cách tìm nguyên nhân và xử lý:** Kiểm tra key chỉ ở dạng có/không, không in secret; chạy API riêng ở cổng 8001, xác nhận health báo tracing enabled rồi đọc observations và prompt versions từ đúng project.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics khoanh triệu chứng và thời gian; `correlation_id` tìm request trong log; trace của cùng ID chỉ ra span gây chậm/lỗi.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Trace phân biệt được prompt version 1/2 và correlation ID; token/cost được ghi theo generation. Rollback production về version 1 đã được đọc lại từ API.
- **Điều quan trọng nhất đã học:** Tracing phải vừa nối được với log vừa tránh capture nội dung user; prompt label có thể promote/rollback độc lập với code và cần có trace xác nhận version thực dùng.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** CP3 chưa thể chạy vì challenge chính thức đúng lớp chưa release. Cần chụp các ảnh UI Langfuse theo rubric; API evidence hiện có trong `evidence/06-langfuse-traces.txt`. Số liệu dashboard hiện tại chỉ từ fake LLM practice.

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace (chờ challenge CP3).
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân; API evidence đã lưu, UI screenshots còn thiếu và phải không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
