# Team

## Thông tin nhóm

- Tên nhóm: CheeseSandwich
- Lớp: L3B
- Repo nhóm: `K5-L3B-Day08-CheeseSandwich-From-Workflows-to-Agents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Nguyễn Long Vũ | 2A202603842 | 26ai.vunl@vinuni.edu.vn | mhoo40 | giữ cổng host (`pytest -q`) luôn xanh, đọc contract, viết bổ sung bộ unit test bẫy các ca ẩn (`src/tests/test_hidden_guards.py`), chạy `crash_test` 20/20, rà soát rò rỉ `CANARY_SECRET_*`/PII trong toàn bộ file trace và tổng hợp báo cáo |
| 2 | Nguyễn Huy Tấn | 2A202603925 | 26ai.tannh@vinuni.edu.vn | Nguyễn Huy Tấn | Thiết kế luồng điều phối giữa Orchestrator và Investigator (read-only), kiểm soát gói tin `handoff.v1` qua allowlist |
| 3 | Nguyễn Văn Anh Trung | 2A202603903 |       | Trungocsdiogee-eee8-k67-hust | cài đặt `workflow.py` đầu tiên làm chuẩn đối chiếu tốc độ và chi phí, sau đó chạy benchmark tổng hợp |
| 4 | Võ Thanh Huy | 2A202603879 | 26ai.huyvt2@vinuni.edu.vn | VThanh-Huy | Xây dựng vòng lặp ReAct tối đa 8 bước với tập tool chỉ đọc, tách biệt hoàn toàn bước gọi `durability.issue_refund` ra khỏi vòng lặp của MockLLM |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Long Vũ | Testing | `c9c2b4f` - benchmark.json, crash.json, test_hidden_gaurds | test_hidden_gaurds |
| Nguyễn Văn Anh Trung | Workflow (shape A) | `f523678`, `fe4de1d`, `3db0e23` - workflow.py (CP2, CP3) | student tests `-k workflow` (62 passed) |
|  |  |  |  |
|  |  |  |  |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603903 - Nguyễn Văn Anh Trung

### Phần việc phụ trách

- Hoàn thành shape A (Checkpoint 2 và 3)

### Đóng góp cụ thể

Hoàn thành shape A (Checkpoint 2 và Checkpoint 3), làm trên nhánh `workflow`.
Kết quả:
- `python -m lab8.smoke` → `lab8.smoke pass`
- `python -m pytest -q` (cổng host) → 54 passed, không có `failed`
- `python -m pytest -q -m student -o addopts= -k workflow` → **62 passed**
- `python -m pytest -q -m student -o addopts= -k "workflow and (t11 or t12)"` → 2 passed (CP3: gọi lại và crash rồi resume)
- `python -m pytest -q -m student -o addopts= -k "workflow and (C-013 or C-014)"` → 10 passed 


### Bằng chứng
- Commit: `f523678`, `fe4de1d`, `3db0e23` trên nhánh `workflow`.

## 2A202603842_NguyenLongVu

### Phần việc phụ trách

- Giữ cổng host (`pytest -q`) luôn xanh, đọc contract, bussiness_rules. 
- Viết bổ sung bộ unit test bẫy các ca ẩn (`src/tests/test_hidden_guards.py`).
- Chạy `crash_test` 20/20, rà soát rò rỉ `CANARY_SECRET_*`/PII trong toàn bộ file trace và tổng hợp báo cáo.

### Đóng góp cụ thể

- **Kiểm soát chất lượng cổng host & nghiệp vụ**: Rà soát toàn bộ contract và business_rules để đảm bảo logic xử lý trạng thái (resolved, denied, needs_info, escalated) đồng nhất trên cả 3 kiến trúc (workflow, single, orchestrator), duy trì bộ test nền pytest -q luôn đạt trạng thái xanh trước mọi lần merge.

- **Mở rộng độ phủ kiểm thử biên**: Thiết kế và triển khai bộ unit test src/tests/test_hidden_guards.py nhằm bắt các tình huống ẩn và ca biên (dữ liệu thiếu trường, sai định dạng, xung đột trạng thái, cô lập phiên SQLite giữa các lần chạy).

- **Kiểm thử chịu tải & rà soát bảo mật/PII**: Thực thi crash_test (đạt *20/20*) và chạy đánh giá diện rộng hidden_selfcheck trên 600 lượt chạy (`40 claims × 5 seeds × 3 shapes`); quét toàn bộ file trace/log đầu ra để xác nhận không phát sinh lỗi thực thi (error_trials = 0) và không rò rỉ dữ liệu nhạy cảm CANARY_SECRET_* hoặc PII (leak_suspects = 0), sau đó tổng hợp báo cáo đánh giá chi tiết cho nhóm.

### Bằng chứng

- `src/tests/test_hidden_guards.py`
- `src\reports\benchmark.json`, `src\reports\crash.json`
