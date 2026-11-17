# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

### Hiểu bài toán và mục tiêu cốt lõi
Bài toán yêu cầu xây dựng và so sánh bốn kiến trúc xử lý yêu cầu hoàn phí vận chuyển (claim) cho hệ thống giả lập LogiX-VN (`workflow`, `single`, `orchestrator`, và đối chứng `swarm`) dưới cùng một chữ ký hàm `run_claim`[cite: 2]. Mục tiêu trọng tâm không phải là tối đa hóa tính tự chủ của AI, mà là **chọn kiến trúc ít tự chủ nhất nhưng vẫn đáp ứng đầy đủ các tiêu chuẩn nghiệp vụ, độ ổn định và bảo mật**, dựa trên số liệu thực nghiệm thay vì giả định "multi-agent luôn tốt hơn".

Để đảm bảo an toàn tài chính và bảo mật dữ liệu, nhóm thiết lập nguyên tắc ranh giới cứng:
- **Code quyết định toàn bộ logic nghiệp vụ và ghi dữ liệu:** Mọi thao tác tính tiền (`compute_compensation`), kiểm tra quyền sở hữu đơn (`principal_id`), hiệu lực chính sách (`is_current`, `effective_date`), trần hoàn tiền theo đơn, kiểm tra phê duyệt (`approval_id` khớp `claim_id`) và chống ghi trùng (`idempotency_key = refund:{claim_id}`) đều do code Python và Host thực thi[cite: 2, 3].
- **Model chỉ đọc và tổng hợp ngôn ngữ:** Văn bản trong `ticket` luôn được xử lý như dữ liệu người dùng không đáng tin cậy (untrusted input), tuyệt đối không dùng số liệu trong ticket để tính tiền hay bỏ qua chính sách[cite: 3].
...

### Phân công công việc và thứ tự triển khai
Nhóm 4 thành viên chia theo mô hình **3 luồng kiến trúc song song + 1 luồng QA, bảo mật và tổng hợp** trên các nhánh Git độc lập để tránh xung đột mã nguồn:
1. **Nguyễn Văn Anh Trung (Shape A `workflow`):**  cài đặt `workflow.py` đầu tiên làm chuẩn đối chiếu tốc độ và chi phí, sau đó chạy benchmark tổng hợp.
2. **Võ Thanh Huy (Shape B `single` agent):** Xây dựng vòng lặp ReAct tối đa 8 bước với tập tool chỉ đọc, tách biệt hoàn toàn bước gọi `durability.issue_refund` ra khỏi vòng lặp của MockLLM.
3. **Nguyễn Huy Tấn (Shape C `orchestrator`):** Thiết kế luồng điều phối giữa Orchestrator và Investigator (read-only), kiểm soát gói tin `handoff.v1` qua allowlist.
4. **Nguyễn Long Vũ (Security & Báo cáo):** Thiết lập repo, giữ cổng host (`pytest -q`) luôn xanh, đọc contract, viết bổ sung bộ unit test bẫy các ca ẩn (`src/tests/test_hidden_guards.py`), chạy `crash_test` 20/20, rà soát rò rỉ `CANARY_SECRET_*`/PII trong toàn bộ file trace và tổng hợp báo cáo.

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

...

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min-max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

### Bảng so sánh 4 shape trên bộ Public (14 claims × 5 seeds = 70 trials)
*(Số liệu trích xuất từ `src/reports/benchmark.json`, seeds `11, 22, 33, 44, 55`)*[cite: 5]:

| Shape | Pass rate | Pass^5 | Seed min-max | Variance | Cost / success (VND) |  mean/p95 steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Workflow** | 1.000 | 1.000 | 1.000 - 1.000 | 0| 34.29 | 4.43/5 |
| **Single** | 1.000 | 1.000 | 1.000 - 1.000 | 0 | 48.25 | 3.57/4 |
| **Orchestrator** | 1.000 | 1.000 | 1.000 - 1.000 | 0 | 57.04 | 3.71/4 |
| **Swarm** | 0.986 | 0.929 | 0.929 - 1.000 | 0.000816 | 49.57 | 2.80/3 |


### Kiểm tra an toàn sập nguồn, bảo mật và tự kiểm Hidden
- **Crash safety (`src/reports/crash.json`):** Đạt **`20/20`** điểm an toàn trên toàn bộ các mốc `before_effect`, `after_effect_before_checkpoint` và `after_checkpoint`; mỗi claim chỉ tạo tối đa 1 dòng `refund_ledger` và 1 audit `refund_committed` sau khi resume[cite: 5].
- **Bảo mật & Chống rò rỉ:** Đạt `0` lỗi approval bypass và `0` lỗi secret leakage trên toàn bộ 272 file trace được quét (`CANARY_SECRET_*`, `Bearer` token, SĐT, địa chỉ, `internal_note` và `item_name` đều bị chặn hoàn toàn)[cite: 4, 5, 13].
- **Tự kiểm trên bộ Hidden (`src/reports/hidden_selfcheck.json`):** .

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
