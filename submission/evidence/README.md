# Evidence cá nhân

Đặt ảnh hoặc output text dùng để chấm vào thư mục này. Danh sách đầy đủ xem tại [docs/SUBMISSION.md](../../docs/SUBMISSION.md).

Evidence local hiện có:

```text
01-pytest.txt
02-log-validator.txt
03-dashboard-validator.txt
04-structured-log.txt
05-pii-redaction.txt
11-dashboard-overview.png
11-dashboard-runtime.json
practice-load-test.txt
request-id-headers.txt
```

Trace, prompt-version/rollback và incident evidence vẫn cần Langfuse project/key
cùng challenge release đúng lớp. Dashboard JSON và ảnh hiện tại chỉ phản ánh
mock practice trong môi trường local.

Các file chờ thu thập sau:

```text
06-trace-list.png
07-trace-waterfall.png
08-trace-metadata.png
09-prompt-versions.png
10-prompt-rollback.png
12-incident-metric.png
13-incident-log.png
14-incident-trace.png
```

Có thể dùng `.txt` cho output của tests/validators. Có thể tách dashboard thành nhiều ảnh nếu một ảnh không đọc rõ.

Ảnh `04`, `05`, `13` lấy từ terminal hoặc `data/logs.jsonl`. Ảnh `06`–`10`, `14` lấy từ project Langfuse cá nhân `day13-k4-l3a-<MSSV>` và nên nhìn thấy tên project. Không mở/chụp trang API Keys.

Từ `submission/REPORT.md`, dẫn ảnh bằng đường dẫn tương đối:

```markdown
![Trace waterfall](evidence/07-trace-waterfall.png)
```

Không commit secret, API key, PII thô hoặc evidence của học viên/lớp khác.
