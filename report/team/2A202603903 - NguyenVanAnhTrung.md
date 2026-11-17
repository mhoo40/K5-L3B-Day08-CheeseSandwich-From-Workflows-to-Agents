
## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Anh Trung
- MSSV: 2A202603903


## 2. Phần việc phụ trách

Shape phụ trách: A - Workflow
Báo cáo cá nhân

## 3. Đóng góp cụ thể

Hoàn thành shape A (Checkpoint 2 và checkpoint 3)


## 4. Bằng chứng

Link commit, tên test, run id hoặc trích đoạn report liên quan.

...

## 5. Công cụ AI đã dùng

**Công cụ:** Claude Code.

**Dùng vào việc gì** (shape A, file `src/lab8/shapes/workflow.py`):

| Việc | Tôi tự làm | Claude Code làm |
|---|---|---|
| Đọc docstring, phân tích input/output của `get_claim_view`, `lookup_order`, `compute_compensation`, `durability.issue_refund`, `Trace`, `finish` | Đặt câu hỏi, đọc lại code gốc | Tóm tắt input/output và ánh xạ `reason` của `issue_refund` sang `status` |
| Bước 1–2 (đọc claim, thiếu `order_id` → `needs_info`) | Viết khung ban đầu: `connect`, gọi `get_claim_view`, các nhánh `if` | Sửa import sai (`from db` → `from lab8.db`), sửa lời gọi `finish()` thiếu tham số, thêm `Trace`/`Budget`/helper `done()` và `try/finally` đóng connection |
| Bước 3 (`lookup_order` → `escalated`) | Viết lời gọi và nhánh `escalated` | Chỉ ra 2 lỗi: thiếu tham số `principal_id`, thiếu `return` trước `done(...)` |
| Bước 4–7 (quote, `denied`, `issue_refund`, `resolved`/`failed`) | Yêu cầu và đọc lại code | Viết code các bước này |
| CP3 (`crash_at`, không bắt `InjectedCrash`) | Hỏi gợi ý | Giải thích bước 6 đã đáp ứng CP3; chỉ ra đoạn code tôi thêm sau `finally:` là sai và cần xoá |

Bước 8 (MockLLM soạn reply) không làm. Shape không gọi model nên model không chọn số tiền và không commit refund.

**Tự kiểm tra kết quả:**

- `python -m lab8.smoke` pass; `python -m pytest -q -m student -o addopts= -k workflow` → 62 passed.
- Giải thích vì sao truyền quote đầy đủ vào `durability.issue_refund`

## 6. Tự đánh giá

...
