# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: <điền git rev-parse --short HEAD sau khi commit chốt>
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 34.29 (src/reports/benchmark.json)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

- Trên cùng tập 14 claim public và 5 seed, cả ba kiến trúc đều đạt độ chính xác tuyệt đối với `pass_rate = 1`, `pass^5 = 1`, `seed min-max = 1-1` và `seed_variance = 0`. Nhóm chọn **`workflow`** vì đây là kiến trúc ít tự chủ nhất đáp ứng trọn vẹn mọi tiêu chuẩn nghiệp vụ và bảo mật với chi phí mô phỏng thấp nhất (`34.29` VND/ca thành công - tiết kiệm 28.9% so với `single` ở mức `48.25` VND và tiết kiệm 39.9% so với `orchestrator` ở mức `57.04` VND), đồng thời không chịu rủi ro dao động đầu ra theo seed của vòng lặp LLM.

## Có đáng đổi lấy multi-agent không

- Không đáng để đánh đổi sang multi-agent trong bài toán này. Ngay cả trong trường hợp giả định một shape multi-agent có `pass_rate` nhỉnh hơn một chút nhưng đi kèm `cost/success` và `seed_variance` cao hơn, nhóm vẫn giữ `workflow` vì quy trình bồi thường vận chuyển đòi hỏi tính nhất quán tuyệt đối (`pass^5` cao) và chi phí vận hành tối ưu trên từng giao dịch. 
- Quyết định này chỉ đảo lại sang `single` hoặc `orchestrator` khi bài toán thay đổi bản chất: dữ liệu đầu vào là văn bản tự do chưa chuẩn hóa `order_id`/`principal_id` đòi hỏi suy luận nhiều bước để tìm kiếm thông tin, quy tắc xét duyệt có nhiều ngoại lệ ngữ nghĩa phức tạp không thể mã hóa thành cây điều kiện tĩnh, hoặc cần phân tách quyền truy cập dữ liệu nhạy cảm giữa nhiều nguồn độc lập bằng cơ chế `handoff` có kiểm soát.

## Trace và bằng chứng

- Trace của `workflow` tuân thủ Trace Contract v1 (`{"run_id": ..., "events": [...]}`) và ghi lại 5 loại sự kiện chuẩn hóa: 
`tool:get_claim_view` (mã claim, cờ `found`, `has_order_id`).
`tool:lookup_order` (cờ `visible`, `reason`).
`tool:compute_compensation` (`amount_vnd`, `reason`, `clause_ids`).
`tool:issue_refund` (`ok`, `reason`, `conflict`, `amount_vnd`).
`final` (`status`, `proposal_amount`, `error_reason`).

- Hệ thống cố ý **không** ghi nội dung thô của `ticket`, `parent_secret`, `raw_headers`, cùng các trường *PII/nội bộ* của đơn hàng (`phone`, `address`, `internal_note`, `item_name`) để ngăn chặn rò rỉ dữ liệu khách hàng và bí mật xác thực qua log hoặc ngữ cảnh LLM. Để chứng minh không lộ secret kể cả với các biến thể ngoài bộ quét tĩnh mặc định, nhóm kết hợp kiểm tra schema đầu ra của `get_claim_view` và `lookup_order` theo allowlist (`ORDER_FIELDS`), chạy bộ test bẫy độc lập `src/tests/test_hidden_guards.py` chứa các chuỗi canary mới (`CANARY_SECRET_H01`-`H04`, `CANARY_INTERNAL_H02`), và quét toàn bộ 272 file trong `src/traces/` bằng script kiểm tra tự động với kết quả `0` vi phạm.

## Giới hạn

- Hệ thống đánh giá sử dụng `MockLLM` với bảng giá token giả lập (`pricing.yaml`), do đó chỉ số `latency` được ghi nhận là `unavailable` và `cost/success` chỉ mang ý nghĩa so sánh tương đối giữa các kiến trúc chứ không phản ánh hóa đơn API hay độ trễ mạng thực tế. Ngoài ra, bộ dữ liệu public chỉ gồm 14 ca chuẩn hóa sẵn khóa ngoại nên chưa phản ánh hết độ nhiễu của ngôn ngữ tự nhiên ngoài thực tế; nhóm giữ nguyên toàn bộ số liệu gốc từ `src/reports/benchmark.json` và không chỉnh sửa thủ công file JSON báo cáo.