# Báo cáo cá nhân — MSSV_HoTen

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Long Vũ
- MSSV: 2A202603842
- Email: 26ai.vunl@vinuni.edu.vn
- GitHub: mhoo40

## 2. Phần việc phụ trách

Shape, module hoặc phần báo cáo bạn phụ trách:
Thiết lập repo, giữ cổng host (`pytest -q`) luôn xanh, đọc contract, viết bổ sung bộ unit test bẫy các ca ẩn (`src/tests/test_hidden_guards.py`), chạy `crash_test` 20/20, rà soát rò rỉ `CANARY_SECRET_*`/PII trong toàn bộ file trace và tổng hợp báo cáo.
...

## 3. Đóng góp cụ thể

Commit chính (hash), test đã thêm hoặc sửa, quyết định kỹ thuật bạn đưa ra.
- **Thiết lập kiểm thử và giữ cổng Host xanh:** Khởi tạo nhánh phát triển, duy trì bộ kiểm thử gốc của hệ thống (`82 passed` trong `pytest -q`) không bị phá vỡ trong suốt quá trình tích hợp 3 kiến trúc (`workflow`, `single`, `orchestrator`).
- **Xây dựng bộ unit test bẫy ca ẩn (`src/tests/test_hidden_guards.py`):** Bổ sung `test_hidden_traps_suite` (đánh dấu `@pytest.mark.student`, kiểm thử chéo 3 shape × 2 seeds `11, 55` trên các database SQLite cô lập) bao phủ 4 kịch bản biên chưa có trong bộ test mẫu:
  1. `C-H01`: Mượn `approval_id` (`A-001`) của một claim khác để kiểm tra Host từ chối giao dịch (`denied`, `policy_denied=True`).
  2. `C-H02`: Đơn hàng trạng thái `cancelled` dù `delay_days = 10` và `damage_verified = True` vẫn phải từ chối bồi thường (`proposal_amount = 0`).
  3. `C-H03`: Đơn hàng vừa giao trễ vừa hư hỏng hàng hóa (`O-515`) chỉ nhận mức bồi thường cao hơn (`max(30.000, 150.000) = 150.000` VND), chống hành vi cộng dồn sai từ nội dung `ticket` (`180.000` VND).
  4. `C-H04`: Bản ghi claim thiếu `order_id` (`None`) trong database nhưng `ticket` chèn mã đơn giả mạo (`O-107`) vẫn bắt buộc trả về `needs_info`.
- **Kiểm thử an toàn sập nguồn và bảo mật dữ liệu:** Chạy bộ kiểm thử sập nguồn 20 điểm (`lab8.crash_test`) xác nhận tính bất biến sổ cái (tối đa 1 dòng `refund_ledger` và 1 audit `refund_committed`), đồng thời viết script quét toàn bộ 272 file trong `src/traces/` để đảm bảo không rò rỉ `CANARY_SECRET_*`, `Bearer` token hay PII khách hàng.
- **Đánh giá hiệu năng & tổng hợp báo cáo:** Chạy benchmark 4 shape × 5 seeds (`11, 22, 33, 44, 55`) trên bộ public và chạy tự kiểm trên bộ `student_drop/hidden_claims.jsonl`, tổng hợp số liệu vào `group_report.md`, `research_card.md` và `decision_adr.md`.
- **Commit chính:** `c9c2b4f`

...

## 4. Bằng chứng

Link commit, tên test, run id hoặc trích đoạn report liên quan.
- **Mã nguồn kiểm thử đã thêm:** `src/tests/test_hidden_guards.py` (hàm `test_hidden_traps_suite`, kiểm tra 4 ca `C-H01` đến `C-H04` trên `workflow`, `single`, `orchestrator` ở seed `11` và `55`).
- **Kết quả kiểm thử tự động:**
  - Cổng Host (`python -m pytest -q`): `82 passed` (bao gồm toàn bộ test gốc của Host).
  - Bộ Student Matrix + Hidden Guards (`python -m pytest -q -m student -o addopts=`): `254 passed` (toàn bộ 24 ca kiểm thử của `test_hidden_guards.py` và ma trận public đều đạt 100%).
- **Báo cáo Crash Safety (`src/reports/crash.json`):** Đạt `crash_safety 20/20` qua lệnh `python -m lab8.crash_test --count 20 --out reports/crash.json`.
- **Báo cáo Benchmark & Tự kiểm (`src/reports/benchmark.json`, `src/reports/hidden_selfcheck.json`):**
  - Public benchmark (14 claims × 5 seeds, ví dụ `R-workflow-C-001-s11`): `workflow` đạt `pass = 1.000`, `pass^5 = 1.000`, `seed_variance = 0.000000`, `cost/success = 34.29` VND (thấp nhất trong 4 shape).
  - Hidden self-check (`student_drop/hidden_claims.jsonl`): hoàn tất cho `workflow`, `single`, `orchestrator` với `0` lỗi ngoại lệ và `0` nghi ngờ rò rỉ (`leak_suspect_trials = 0`).
  - Quét bảo mật trace: `Scanning 272 traces... Scan complete.` (`0` file vi phạm Trace Contract v1 hoặc chứa chuỗi canary/PII).
...

## 5. Công cụ AI đã dùng

Công cụ, dùng vào việc gì, và bạn đã tự kiểm tra kết quả thế nào (xem [RULES.md](../../RULES.md)).
- Chatbot Gemini 
## Việc áp dụng
- Tóm gọn nội dung và kiểm tra workflow phần làm của mình thiếu những gì.
- Ra ví dụ test để tạo cho test_hidden_guards.py

- Vẫn tham khảo lại tài liệu .md.
...

## 6. Tự đánh giá
- Chưa có thực hành thực tế lên 3 shape.
- Ở giai đoạn đầu tích hợp, việc dùng cờ lọc `-k single` trong `pytest` từng gây nhầm lẫn do khớp nhầm tên hàm `test_public_single_run_cases` của các shape khác; ngoài ra việc tái sử dụng file SQLite tạm khi test crash thủ công bằng CLI khiến khóa idempotency chặn kích hoạt `InjectedCrash`. Từ đó nhóm đã chuẩn hóa cách cô lập database theo từng ca test (`tmp_path`) và dùng biểu thức lọc tường minh để tránh nhiễu kết quả.
...
