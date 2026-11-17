## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Anh Trung
- MSSV: 2A202603903


## 2. Phần việc phụ trách

Shape phụ trách: A - Workflow (`src/lab8/shapes/workflow.py`), gồm CP2 và CP3.

## 3. Đóng góp cụ thể

Hoàn thành shape A (Checkpoint 2 và Checkpoint 3), làm trên nhánh `workflow`.

**Commit chính:**

| Commit | Nội dung |
|---|---|
| `f523678` | Update Workflow - CP2: bản đầu của `run_claim` (bước 1–3: đọc claim, `needs_info`, `escalated`) |
| `fe4de1d` | Update Workflow - CP2 and CP3: bước 4–7 (quote, `denied`, `issue_refund`, `resolved`/`failed`), truyền `crash_at` |
| `3db0e23` | Another update - CP2 and CP3: sửa nhỏ sau khi chạy lại test |

**Quyết định kỹ thuật:**

- Tiền chỉ lấy từ `tools.compute_compensation` trên order row. Không đọc con số nào trong ticket.
- Truyền **quote đầy đủ** vào `durability.issue_refund`, không tự trừ phần đã hoàn (xem mục 5).
- Phân loại kết quả `issue_refund`: `conflict` → `failed`; `ok = False` → `denied` (host đã ghi `policy_denied`); `ok = True` (kể cả `idempotent_replay`) → `resolved`.
- Quote = 0 → `denied` ngay, không gọi `issue_refund`, nên không có audit `policy_denied`.
- CP3: truyền `crash_at` vào `issue_refund` và **không** bắt `InjectedCrash`, để crash đi lên tới harness và lần chạy lại được ledger/idempotency key `refund:{claim_id}` xử lý.
- Trace: mọi nhánh return đi qua helper `done()`, ghi event `final` rồi gọi `finish()`. Trace chỉ ghi trường an toàn (`found`, `has_order_id`, `visible`, `reason`, số tiền), không ghi ticket thô hay order row.

**Kết quả** (chạy trong `src/`):

- `python -m lab8.smoke` → `lab8.smoke pass`
- `python -m pytest -q` (cổng host) → 54 passed, không có `failed`
- `python -m pytest -q -m student -o addopts= -k workflow` → **62 passed**
- `python -m pytest -q -m student -o addopts= -k "workflow and (t11 or t12)"` → 2 passed (CP3: gọi lại và crash rồi resume)
- `python -m pytest -q -m student -o addopts= -k "workflow and (C-013 or C-014)"` → 10 passed 

## 4. Bằng chứng

- Commit: `f523678`, `fe4de1d`, `3db0e23` trên nhánh `workflow`.
- Test: `python -m pytest tests/test_public_matrix.py -m student -o addopts= -k workflow -v`, tất cả case `[...-workflow]`, gồm `test_t11_retry_keeps_one_refund[workflow]` và `test_t12_crash_before_checkpoint_does_not_double_pay[workflow]`.
- Trace T13, `src/traces/R-workflow-C-013-s11.json` (đơn `O-505` đã được hoàn 35.000):

  ```text
  tool:compute_compensation  amount_vnd=35000  clause_ids=['SHIP-LATE-03']
  tool:issue_refund          ok=False  reason=order_already_refunded
  final                      status=denied  proposal_amount=35000
  ```

- Trace T14, `src/traces/R-workflow-C-014-s11.json` (đơn `O-515` đã được hoàn 30.000, entitlement 150.000):

  ```text
  tool:issue_refund          ok=True  reason=committed  amount_vnd=120000
  final                      status=resolved  proposal_amount=150000
  ```

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
| Báo cáo cá nhân | Viết khung, mục 1–3, 5 | Chạy lại test, lấy trace làm bằng chứng, điền mục 3–4 và phần giải thích quote |

Bước 8 (MockLLM soạn reply) không làm. Shape không gọi model nên model không chọn số tiền và không commit refund.

**Tự kiểm tra kết quả:**

- Chạy lại toàn bộ lệnh ở mục 3 trong thư mục `src/`; tất cả pass.
- Giải thích vì sao truyền quote đầy đủ vào `durability.issue_refund`: host mới là nơi biết đơn đã được hoàn bao nhiêu. Trong `issue_refund`, host tính `already = order_refunded_vnd(...)` cho các claim khác cùng đơn rồi `authorize(...)` cắt số tiền theo trần của đơn. Nếu shape tự trừ trước thì host sẽ trừ thêm lần nữa. Ví dụ T14: entitlement 150.000, đã hoàn 30.000. Truyền 150.000 → host ghi ledger 120.000 (đúng). Nếu shape tự truyền 120.000 → host trừ tiếp 30.000, chỉ ghi 90.000 và T14 fail. Ngoài ra `proposal_amount` trong `RunResult` phải là quote đầy đủ (150.000 ở T14, 35.000 ở T13), không phải số tiền thực ghi ledger.

## 6. Tự đánh giá

- **Đã làm được:** shape A qua đủ 62 test student, T11/T12 (CP3) và T13/T14 xanh, cổng host vẫn xanh. Mọi nhánh return đều ghi trace đúng contract.
- **Hiểu được:** vì sao tiền phải nằm trong code chứ không do model quyết; vì sao shape không được tự trừ phần đã hoàn;
- **Hạn chế:** phần lớn code bước 4–7 do Claude Code viết; tôi đọc lại và kiểm bằng test nhưng tự viết ít hơn ở phần này.
- **Lần sau:** tự viết trước các nhánh xử lý kết quả `issue_refund` rồi mới nhờ AI review, và chạy crash suite sớm hơn.
