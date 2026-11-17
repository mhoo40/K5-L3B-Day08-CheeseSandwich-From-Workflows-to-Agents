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
### Ranh giới Code / Model và cơ chế an toàn chung
Ở cả ba shape do nhóm phát triển, quy trình đều tuân thủ nghiêm ngặt ranh giới phân quyền giữa code và mô hình ngôn ngữ:
- **Đọc dữ liệu qua allowlist:** `get_claim_view` và `lookup_order` chỉ trả về các trường được phép (`ORDER_FIELDS`), loại bỏ hoàn toàn `parent_secret`, `raw_headers`, số điện thoại, địa chỉ, ghi chú nội bộ (`internal_note`) và tên sản phẩm (`item_name`)[cite: 1, 11, 13].
- **Tính tiền thuần code & truyền quote đầy đủ:** Cả ba shape đều tính mức bồi thường bằng `tools.compute_compensation` dựa trên bản ghi bảng `orders` và `policies` hiện hành, không bao giờ trích xuất số tiền hay số ngày trễ từ văn bản `ticket`[cite: 11, 12, 13]. Khi `proposal_amount > 0`, shape truyền **quote đầy đủ** vào `durability.issue_refund(..., crash_at=crash_at)` để Host tự kiểm tra `approval_id`, trừ khoản đã hoàn trước đó của đơn (per-order cap) và ghi audit (`refund_committed` hoặc `policy_denied`) trong cùng một giao dịch[cite: 11, 12, 13].
- **Đảm bảo Crash Safety & Trace Contract v1:** Tham số `crash_at` được truyền thẳng vào `issue_refund` và ngoại lệ `InjectedCrash` luôn được ném tiếp ra ngoài (không bị nuốt lỗi), đồng thời kết nối SQLite luôn được đóng trong khối `finally`[cite: 11, 12, 13]. Mọi nhánh thoát (`resolved`, `denied`, `needs_info`, `escalated`, `failed`) đều ghi file trace JSON hợp lệ và đóng gói kết quả qua `common.finish()`[cite: 11, 12, 13].

### Chi tiết ba kiến trúc nhóm cài đặt
1. **Shape A — `workflow` (`src/lab8/shapes/workflow.py`):**
   - **Luồng xử lý:** Thực thi tuyến tính bằng Python thuần (`get_claim_view` -> kiểm tra `order_id` -> `lookup_order` -> `compute_compensation` -> `durability.issue_refund` nếu `proposal_amount > 0`)[cite: 13]. Không gọi `MockLLM`, giúp chi phí mô phỏng thấp nhất và triệt tiêu hoàn toàn dao động theo seed.
   - **Trace events:** Ghi lại 5 loại sự kiện chuẩn hóa gồm `tool:get_claim_view` (`claim_id`, `found`, `has_order_id`), `tool:lookup_order` (`visible`, `reason`), `tool:compute_compensation` (`amount_vnd`, `reason`, `clause_ids`), `tool:issue_refund` (`ok`, `reason`, `conflict`, `amount_vnd`) và `final` (`status`, `proposal_amount`, `error_reason`)[cite: 13].
2. **Shape B — `single` (`src/lab8/shapes/single.py`):**
   - **Luồng xử lý:** Vận hành vòng lặp ReAct qua `run_react(..., max_steps=8)`[cite: 12]. Khởi tạo `observation={"claim": {"claim_id": claim_id}}` để ngăn nội dung `ticket` đi vào ngữ cảnh của agent[cite: 12]. Trong mỗi bước, `decide()` gọi `MockLLM` (`complete(..., purpose="decide")`) và chỉ chọn các tool chỉ đọc (`lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`)[cite: 12]. Bước ghi tiền `issue_refund` nằm hoàn toàn bên ngoài vòng lặp sau khi `run_react` dừng ở trạng thái `"final"`[cite: 12].
   - **Trace events:** Ghi lại các sự kiện đã lọc sạch PII gồm `order` (`visible`, `delay_days`), `policy` (`count`), `quote` (`amount_vnd`, `reason`), `host` (`ok`, `reason`) và `decision` (`status`)[cite: 12].
3. **Shape C — `orchestrator` (`src/lab8/shapes/orchestrator.py`):**
   - **Luồng xử lý:** Orchestrator đọc `claim_id` và `principal_id`, sau đó tạo gói ủy quyền qua `make_handoff` và thực thi nhóm investigator chỉ đọc qua `run_readonly_investigators` với danh sách tool giới hạn `INVESTIGATOR_TOOLS = ["lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"]`[cite: 11]. Sau khi nhận kết quả điều tra, Orchestrator tự kiểm tra tính hợp lệ và gọi `issue_refund` ở cấp điều phối[cite: 11].
   - **Sanitize Handoff & Trace:** Khi gọi `make_handoff`, nhóm chủ động truyền `facts={}` (để Investigator tự truy vấn DB theo `principal_id`, không mang dữ liệu từ context cha sang) và gọi `safe_dump(handoff)` khi ghi log nhằm loại bỏ hoàn toàn `parent_secret`, `raw_headers` và `ticket`[cite: 11]. Trace ghi lại các sự kiện `handoff`, `investigator` (chỉ gồm `lookup_order`, `refunded_vnd`, `policy_count`), `quote`, `crash` (nếu gặp `InjectedCrash` trước khi `raise` tiếp) và `decision` (`status`, `proposal_amount`, `reason`)[cite: 11].
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

MockLLM không phải model sản xuất; latency là `unavailable`.

...

## 8. Tài liệu tham khảo

...
