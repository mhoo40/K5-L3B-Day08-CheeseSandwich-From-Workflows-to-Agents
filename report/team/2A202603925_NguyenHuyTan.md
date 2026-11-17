# Báo cáo cá nhân — 2A202603925_NguyenHuyTan

## 1. Thông tin thành viên

- Họ tên: Nguyễn Huy Tấn
- MSSV: 2A202603925
- Email: 26ai.tannh@vinuni.edu.vn
- GitHub: Besoi2004

## 2. Phần việc phụ trách

- Shape C `orchestrator` (`src/lab8/shapes/orchestrator.py`): orchestrator điều phối, investigator chỉ có tool đọc.
- Handoff giữa orchestrator và investigator: dựng bằng `lab8.handoff.make_handoff`, chỉ mang field trong allowlist.
- Bảo mật trace của orchestrator: không lộ `CANARY_SECRET_*`, ticket hay thông tin cá nhân trên mọi nhánh return.

## 3. Đóng góp cụ thể

**Commit chính (nhánh `shape-orchestrator`, PR #1):**

- `0ba0110` — add orchestrator shape
- `a5d5c69` — add orchestrator handoff test

**Test đã thêm:** `src/tests/test_orchestrator_handoff.py`, 28 test, chạy trong cổng host `pytest -q`:

- `test_orchestrator_trace_has_no_secret_or_pii` (14 claim): trace có `run_id` khớp `RunResult`, không chứa `CANARY_SECRET_`, `parent_secret`, `raw_headers`, nguyên văn ticket, hay 43 giá trị SĐT / địa chỉ / ghi chú nội bộ / tên hàng / tên khách lấy từ dữ liệu.
- `test_orchestrator_handoff_is_allowlisted_and_readonly` (14 claim): handoff trong trace chỉ có key thuộc `ALLOWED_FIELDS`, `facts` thuộc `FACT_KEYS`, tool thuộc `READONLY_TOOLS`, `claim_id` đúng claim được giao.

**Quyết định kỹ thuật:**

1. **Handoff với `facts={}`.** Investigator tự đọc DB qua `lookup_order`, nên không cần chuyển dữ kiện nào từ parent. Không có gì đi qua ranh giới thì không thể lộ secret qua handoff.
2. **Không ghi claim view vào trace.** `get_claim_view` có trường `ticket` (chữ người dùng). Trace chỉ ghi: handoff đã sanitize, view đơn đã qua allowlist của `lookup_order`, `refunded_vnd`, quote và quyết định.
3. **Tiền do code tính.** Lấy quote từ `compute_compensation` của investigator trên dòng order trong DB, không lấy số ngày trễ hay số tiền từ ticket hoặc MockLLM. Không dùng khối `REFERENCE_WEAKNESS` của swarm.
4. **Truyền quote đầy đủ vào `durability.issue_refund`.** Không tự trừ `refunded_vnd`; host áp trần theo đơn. Shape tự trừ thì host trừ thêm lần nữa và T14 fail.
5. **Quote > 0 luôn đi qua host.** Shape không tự từ chối, để khi approval hỏng / approval của claim khác / đơn đã hoàn đủ thì host ghi audit `policy_denied`.
6. **Crash:** truyền `crash_at` vào `issue_refund`; khi `InjectedCrash` thì ghi trace rồi `raise` lại, không nuốt lỗi.
7. **Mọi nhánh return đi qua `finish()`** để `refund_effects` và `committed_audit_count` lấy từ ledger, trace luôn được ghi (kể cả `needs_info`, `escalated`, `failed`).

Ánh xạ nhánh → `status`: claim không tồn tại → `failed`; thiếu `order_id` → `needs_info`; không xem được đơn → `escalated`; quote ≤ 0 → `denied` (không gọi host); host chấp nhận → `resolved`; host báo conflict → `failed`; host từ chối → `denied` với `proposal_amount` là quote đầy đủ.

## 4. Bằng chứng

- PR: https://github.com/mhoo40/K5-L3B-Day8-dfgh-From-Workflows-to-Agents/pull/1
- Commit: https://github.com/mhoo40/K5-L3B-Day8-dfgh-From-Workflows-to-Agents/commit/0ba0110 và https://github.com/mhoo40/K5-L3B-Day8-dfgh-From-Workflows-to-Agents/commit/a5d5c69

Kết quả chạy trong `src/`:

| Lệnh | Kết quả |
| --- | --- |
| `python -m pytest -q -m student -o addopts= -k orchestrator` | 62 passed (T01–T14 × 5 seed, T11, T12) |
| `python -m pytest -q` (cổng host) | 82 passed |
| `python -m pytest -q tests/test_orchestrator_handoff.py` | 28 passed |
| Crash ở `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint` rồi chạy lại 2 lần trên C-001 | Crash xảy ra thật; sau resume vẫn 1 refund 35.000 và 1 audit `refund_committed` |
| Grep `CANARY_SECRET_` trên 62 trace `R-orchestrator-*` | 0 file |

Trích một trace (`R-orchestrator-C-001-s11`): các event chỉ gồm `handoff` (8 field allowlist, `facts: {}`), `investigator` (view đơn O-107 với 7 field an toàn), `quote` (35.000, `SHIP-LATE-03`), `decision` (`resolved`).

## 5. Công cụ AI đã dùng

- **Công cụ:** Claude Code.
- **Dùng vào việc:** đọc và tóm tắt đề bài, contract và luật nghiệp vụ; gợi ý cấu trúc `orchestrator.py` dựa trên `swarm_reference.py` (bỏ khối `REFERENCE_WEAKNESS` và lời gọi model "peer"); viết file test `test_orchestrator_handoff.py`; chạy test và kiểm tra tiến độ các nhánh của nhóm.
- **Cách tự kiểm tra:**
  - Đối chiếu từng nhánh return với bảng output contract trong `docs/contracts.md`.
  - Chạy ma trận student cho orchestrator (62/62) và cổng host sau mỗi thay đổi.
  - Mở và đọc trực tiếp file trace để chắc chỉ có field đã qua allowlist.
  - Kiểm tra test có bắt được lỗi thật: tạm thêm `trace.add("debug", claim)` thì test secret fail; đổi `raise` thành `pass` trong khối `InjectedCrash` thì T12 fail; hoàn tác bằng `git checkout` thì xanh lại.
  - Không dùng AI để tạo số liệu benchmark, run id hay commit; mọi số trong báo cáo lấy từ output lệnh đã chạy.

## 6. Tự đánh giá

**Làm được:**

- Shape orchestrator qua đủ 62 test public và cả ba điều kiện must-pass (approval, secret, crash).
- Test security nằm trong cổng host, nên nếu sau này có ai sửa orchestrator làm lộ secret thì cổng đỏ ngay.
- Hoàn thành sớm, push nhánh và mở PR để nhóm gộp.

**Hạn chế:**

- Test secret mới quét trace của orchestrator, chưa áp cho workflow và single.
- Bộ crash suite chính thức (`lab8.crash_test`) chỉ chạy host và swarm; bằng chứng crash cho orchestrator là T12 và phần tự kiểm, chưa có test chính thức riêng.
- Orchestrator tốn thêm lời gọi model (`plan`) và bước handoff so với workflow, nên cost/success cao hơn; chưa tối ưu phần này.
