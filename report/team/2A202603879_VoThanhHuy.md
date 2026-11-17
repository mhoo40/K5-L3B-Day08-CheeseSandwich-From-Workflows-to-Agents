# Báo cáo cá nhân — 2A202603879_VoThanhHuy

## 1. Thông tin thành viên

- **Họ tên:** Võ Thanh Huy
- **MSSV:** 2A202603879
- **Email:** 26ai.huyvt2@vinuni.edu.vn
- **GitHub:** https://github.com/VThanh-Huy

## 2. Phần việc phụ trách

Tôi phụ trách xây dựng và kiểm thử **kiến trúc B — Single Agent** trong Lab Day 8: From Workflows to Agents.

**Module phụ trách:** `src/lab8/shapes/single.py`

Các công việc chính:

- **CP2 — Single Agent:** Xây dựng luồng xử lý khiếu nại bằng một Agent, sử dụng vòng lặp ReAct để quyết định việc gọi công cụ dựa trên kết quả quan sát.
- **CP3 — Ledger và Crash:** Tích hợp cơ chế ghi nhận hoàn tiền thông qua Host, hỗ trợ retry và xử lý crash nhằm tránh hoàn tiền trùng.
- **CP4 — Safety:** Kiểm tra các điều kiện an toàn liên quan đến approval, bảo mật trace và cơ chế chống hoàn tiền trùng.
- **CP5 — Benchmark:** Chuẩn bị đánh giá hiệu quả Single Agent thông qua tỷ lệ xử lý đúng, độ ổn định giữa các seed và chi phí mô phỏng.

## 3. Đóng góp cụ thể

### 3.1. Triển khai Single Agent

Triển khai chức năng `run_claim()` trong `single.py`, sử dụng các thành phần có sẵn của hệ thống Lab.

Luồng xử lý chính:

1. Tiếp nhận claim và kiểm tra dữ liệu đầu vào.
2. Sử dụng ReAct loop để lựa chọn và gọi các công cụ tra cứu.
3. Tra cứu thông tin đơn hàng, chính sách và lịch sử hoàn tiền.
4. Sử dụng công cụ tính toán bồi hoàn theo quy tắc nghiệp vụ.
5. Chuyển yêu cầu hoàn tiền hợp lệ tới Host để kiểm tra và ghi nhận.
6. Trả về `RunResult` và ghi trace phục vụ kiểm tra.

Các công cụ liên quan gồm `lookup_order`, `lookup_policy`, `lookup_refund_history` và `compute_compensation`.

### 3.2. Quyết định kỹ thuật

- Sử dụng một Agent thay vì nhiều Agent để giảm độ phức tạp của việc điều phối.
- Giới hạn vòng lặp ReAct ở tối đa 8 bước để tránh xử lý kéo dài không kiểm soát.
- Sử dụng MockLLM để kiểm thử có thể tái tạo bằng seed, không phụ thuộc vào API mô hình bên ngoài.
- Ưu tiên dữ liệu đơn hàng và chính sách làm căn cứ xử lý, thay vì tin trực tiếp thông tin khách hàng tự khai.
- Không để Agent trực tiếp ghi tiền; hành động hoàn tiền phải thông qua Host và cơ chế kiểm soát của hệ thống.
- Tích hợp `crash_at` để hỗ trợ kiểm thử phục hồi sau sự cố.

### 3.3. Kiểm thử

Chạy các bài kiểm thử public dành cho Single Agent.

**Kết quả ghi nhận:**

- Single Agent: 62/62 public tests đạt.
- Host Test: 54 passed, 248 deselected.
- Kết quả kiểm thử tổng hợp: 122 passed, 120 failed, 60 deselected. Các bài failed được liệt kê thuộc Workflow và Orchestrator, không thuộc Single Agent.
- Đã chạy thử xử lý claim và kiểm tra một trường hợp chạy lại với cơ chế chống hoàn tiền trùng.

**Commit chính:**

- Nhánh Git: VoThanhHuy
- File thay đổi chính: `src/lab8/shapes/single.py`

## 4. Bằng chứng

### 4.1. Kết quả chạy Single Agent

**Run ID:** `R-single-C-012-s11`

Các thông tin ghi nhận:

| Chỉ số | Kết quả |
|---|---|
| Claim ID | C-012 |
| Shape | single |
| Seed | 11 |
| Status | resolved |
| Proposal amount | 35.000 VNĐ |
| Refund status | committed |
| Committed audit count | 1 |
| Model calls | 5 |
| Tool calls | 5 |
| Input tokens | 104 |
| Output tokens | 20 |
| Cost estimate | 53.68 |
| Error reason | null |

Kết quả cho thấy Single Agent xử lý thành công C-012 và database ghi nhận một khoản hoàn tiền 35.000 VNĐ.

### 4.2. Kiểm thử public

Bộ kiểm thử `tests/test_public_matrix.py` được sử dụng để đánh giá các kiến trúc trên nhiều claim và seed.

Kết quả ghi nhận không có bài kiểm thử Single Agent thất bại trong danh sách lỗi. Các lỗi còn lại thuộc hai kiến trúc khác đang được triển khai.

### 4.3. Bằng chứng bổ sung

- File code: `src/lab8/shapes/single.py`
- Trace: `src/traces/R-single-C-012-s11.json`
- Crash report: `src/reports/crash.json`
- Benchmark riêng: `src/reports/benchmark_single.json` 

## 5. Công cụ AI đã dùng

**Công cụ:** ChatGPT.

**Mục đích sử dụng:**

- Tìm hiểu sự khác nhau giữa Workflow, Single Agent, Orchestrator và Swarm.
- Giải thích kiến trúc ReAct, MockLLM, trace, seed và cơ chế gọi công cụ.
- Hỗ trợ phân tích yêu cầu kỹ thuật của CP2, CP3, CP4 và CP5.
- Gợi ý triển khai `single.py`, hướng dẫn chạy thử và phân tích lỗi.
- Giải thích kết quả pytest, trace và các chỉ số benchmark.

**Cách tự kiểm tra kết quả AI:**

- Đối chiếu hướng dẫn với source code và tài liệu của repository.
- Trực tiếp chạy chương trình trong môi trường Python cục bộ.
- Sử dụng pytest để kiểm tra tính đúng đắn thay vì chỉ tin vào code được AI gợi ý.
- Đọc kết quả JSON và trace để kiểm tra trạng thái xử lý, số tiền hoàn và số lượt ghi nhận.
- Phân tích danh sách test failed để xác định đúng module phát sinh lỗi, tránh kết luận sai về phần việc của mình.

## 6. Tự đánh giá

Qua Lab Day 8, hiểu hơn về cách xây dựng một Single Agent và sự khác biệt giữa Agent có khả năng lựa chọn công cụ với Workflow được lập trình theo thứ tự cố định.

Phần khó nhất là hiểu cách phối hợp giữa ReAct loop và Host xử lý hoàn tiền. Ban đầu chủ yếu tập trung vào việc Agent có chạy thành công hay không. Sau khi kiểm thử, nhận ra một hệ thống có thể chạy thành công về mặt kỹ thuật nhưng vẫn trả về kết quả sai nghiệp vụ hoặc vi phạm điều kiện an toàn.

**Kết quả đạt được:**

- Triển khai và chạy được kiến trúc Single Agent.
- Vượt qua 62 bài kiểm thử public của kiến trúc B.
- Biết sử dụng trace, pytest và kết quả chạy để kiểm tra hành vi hệ thống.
- Hiểu cách sử dụng seed để tái tạo thử nghiệm và đánh giá độ ổn định.

**Hạn chế và hướng cải thiện:**

Cần tìm hiểu sâu hơn về cơ chế ra quyết định của LLM thật so với MockLLM.