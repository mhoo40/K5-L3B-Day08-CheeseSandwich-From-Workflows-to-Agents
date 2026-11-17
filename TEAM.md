# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |        |      |       |        |         |
|   2 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| | | | |

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

