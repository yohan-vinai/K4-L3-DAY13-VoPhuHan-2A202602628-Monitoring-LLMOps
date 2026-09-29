# Evidence cá nhân

Đặt ảnh hoặc output text dùng để chấm vào thư mục này. Danh sách đầy đủ xem tại [docs/SUBMISSION.md](../../docs/SUBMISSION.md).

Evidence local hiện có:

```text
01-pytest.txt
02-log-validator.txt
03-dashboard-validator.txt
04-structured-log.txt
05-pii-redaction.txt
06-langfuse-traces.txt
06-trace-list.jpg
07-trace-waterfall.jpg
08-trace-metadata.jpg
09-prompt-versions.jpg
10-prompt-rollback.jpg
11-dashboard-overview.png
11-dashboard-runtime.json
practice-load-test.txt
request-id-headers.txt
```

`06-langfuse-traces.txt` là readback từ project Langfuse đang được key trong `.env` sử dụng: có trace IDs, correlation IDs, observation hierarchy, prompt labels/versions, kiểm tra PII và rollback. Project trên Langfuse UI hiện là `day13-k4-l3a-2A202602628`. Không lưu hay in key. Incident evidence cần file challenge riêng đúng lớp theo hướng dẫn CP3. Dashboard JSON và ảnh phản ánh cùng một mock practice snapshot gồm 23 requests; load-test text và validators là các lần chạy local sau đó.

Ảnh Langfuse chụp trực tiếp từ Brave đã đăng nhập:

```text
06-trace-list.jpg (12 root traces; project name visible)
07-trace-waterfall.jpg (root + retrieval + generation)
08-trace-metadata.jpg (correlation ID, prompt version/label, token and cost; crop excludes public key)
09-prompt-versions.jpg (v1 baseline/production and v2 candidate/latest)
10-prompt-rollback.jpg (v1 selected with production label; v2 retains candidate/latest)
12-incident-metric.png
13-incident-log.png
14-incident-trace.png
```

Có thể dùng `.txt` cho output của tests/validators. Có thể tách dashboard thành nhiều ảnh nếu một ảnh không đọc rõ.

Ảnh `04`, `05`, `13` lấy từ terminal hoặc `data/logs.jsonl`. Ảnh `06`–`10`, `14` lấy từ project Langfuse cá nhân. Không mở/chụp trang API Keys.

Từ `submission/REPORT.md`, dẫn ảnh bằng đường dẫn tương đối:

```markdown
![Trace waterfall](evidence/07-trace-waterfall.jpg)
```

Không commit secret, API key, PII thô hoặc evidence của học viên/lớp khác.
