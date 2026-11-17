# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Google Research (2026), *Towards a Science of Scaling Agent Systems* (https://research.google/blog/ — nghiên cứu thực nghiệm / benchmark đa tác vụ agent) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Với các tác vụ có chuỗi phụ thuộc tuần tự chặt chẽ (sequential dependencies), việc mở rộng sang kiến trúc multi-agent/thêm tác nhân điều phối không cải thiện độ chính xác mà làm tăng chi phí điều phối (coordination overhead) trên mỗi tác vụ thành công. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Giới hạn trên các benchmark có luồng dữ liệu phụ thuộc tuần tự (bước sau cần kết quả bước trước) và giới hạn ngân sách token/bước gọi công cụ; không áp dụng cho bài toán tìm kiếm diện rộng có thể phân rã song song độc lập. |
| HYPOTHESIS | Nếu đổi shape A->B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi chuyển từ `workflow` (A) sang `orchestrator` (C — thêm lớp điều phối `handoff` và investigator), `pass_rate` và `pass^5` sẽ giữ nguyên ở mức `1.000` (do bài toán claim phụ thuộc tuần tự chặt chẽ), nhưng `cost/success` sẽ tăng khoảng 50%–70% do chi phí gọi thêm MockLLM lập kế hoạch/soạn thảo và đóng gói handoff. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Biến giữ cố định: `MockLLM`, tập tool đọc/ghi (`tools.py`, `durability.py`), 5 seeds (`11,22,33,44,55`), corpus `data/public_claims.jsonl` (14 claims), bảng giá `pricing.yaml` và hàm chấm `trial_pass`. Biến duy nhất thay đổi: kiến trúc điều phối từ tuyến tính không LLM (`workflow`) sang mô hình điều phối + investigator (`orchestrator`). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: lãng phí chi phí điều phối (over-orchestration overhead) mà không tăng hiệu quả giải quyết claim. Đo bằng cặp chỉ số `pass^5`, `seed_variance` và `cost_per_success_vnd` trong `src/reports/benchmark.json`. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `src/reports/benchmark.json`
**Đúng với giả thuyết.** Trên cùng 14 claims × 5 seeds, cả `workflow`, `single` và `orchestrator` đều đạt `pass_rate = 1`, `pass^5 = 1`, `seed_variance = 0`, nhưng `cost/success` tăng từ `34.29` VND (`workflow`) lên `57.04` VND (`orchestrator`) — tức tăng *+66.3%* (+22.75 VND/ca) mà không mang lại thêm bất kỳ ca pass nào. Điều này xác nhận bài toán xử lý claim mang tính tuần tự chặt chẽ (`get_claim_view` -> `lookup_order` -> `compute_compensation` -> `issue_refund`), nên thêm tầng điều phối multi-agent chỉ làm đội chi phí.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
