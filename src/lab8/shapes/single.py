"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
python -m lab8.run --shape single --claim-id C-001 --seed 11 --db data/test-workflow-C001.sqlite
"""

from __future__ import annotations

from lab8.schemas import RunResult
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import not_implemented
from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace

def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:

    conn = connect(store_path)

    try:
        budget = Budget()
        trace = Trace(make_run_id("single", claim_id, seed))

        def end(status, amount=0, reason=None):
            return finish(
                conn,
                shape="single",
                claim_id=claim_id,
                seed=seed,
                status=status,
                proposal_amount=amount,
                budget=budget,
                trace=trace,
                error_reason=reason,
            )

        # 1. Đọc claim
        claim = get_claim_view(conn, claim_id)
        budget.add_tool(tool_cost())

        if not claim["found"]:
            trace.add("decision", {"status": "failed"})
            return end("failed", reason="unknown_claim")

        if not claim.get("order_id"):
            trace.add("decision", {"status": "needs_info"})
            return end("needs_info", reason="missing_order_id")

        order_id = claim["order_id"]
        principal_id = claim["principal_id"]

        # 2. Bộ nhớ tạm của Agent trong một lần chạy
        state = {
            "order": None,
            "policy_checked": False,
            "history_checked": False,
            "quote": None,
            "error": None,
        }

        # 3. Hàm quyết định hành động tiếp theo
        def decide(observation):
            last_tool = observation.get("last_tool")
            result = observation.get("last_result") or {}

            # Lưu kết quả từ công cụ vừa gọi
            if last_tool == "lookup_order":
                if result.get("visible"):
                    state["order"] = result["order"]
                    trace.add("order", {
                        "visible": True,
                        "delay_days": result["order"]["delay_days"],
                    })
                else:
                    state["error"] = result.get("reason", "not_visible")

            elif last_tool == "lookup_policy":
                state["policy_checked"] = True
                trace.add("policy", {
                    "count": len(result.get("policies") or [])
                })

            elif last_tool == "lookup_refund_history":
                if result.get("visible"):
                    state["history_checked"] = True
                else:
                    state["error"] = result.get("reason", "not_visible")

            elif last_tool == "compute_compensation":
                state["quote"] = result
                trace.add("quote", {
                    "amount_vnd": result["amount_vnd"],
                    "reason": result["reason"],
                })

            # MockLLM: mô phỏng một lượt quyết định
            complete(
                budget,
                seed=seed,
                purpose="decide",
                prompt=f"{claim_id}|{last_tool}|{list(state)}",
            )

            # Chọn hành động dựa trên quan sát
            if state["error"]:
                return {"final": {
                    "status": "escalated",
                    "reason": state["error"],
                }}

            if state["order"] is None:
                return {
                    "tool": "lookup_order",
                    "args": {
                        "order_id": order_id,
                        "principal_id": principal_id,
                    },
                }

            if not state["policy_checked"]:
                return {"tool": "lookup_policy", "args": {}}

            if not state["history_checked"]:
                return {
                    "tool": "lookup_refund_history",
                    "args": {
                        "order_id": order_id,
                        "principal_id": principal_id,
                    },
                }

            if state["quote"] is None:
                return {
                    "tool": "compute_compensation",
                    "args": {"order": state["order"]},
                }

            return {"final": {
                "status": "quoted",
                "quote": state["quote"],
            }}

        # 4. Chạy vòng ReAct, tối đa 8 bước
        result = run_react(
            conn,
            budget,
            observation={"claim": {"claim_id": claim_id}},
            decide=decide,
            max_steps=8,
        )

        if result["stopped"] != "final":
            trace.add("decision", {"status": "failed"})
            return end("failed", reason="step_cap")

        final = result["final"]

        if final.get("status") == "escalated":
            trace.add("decision", {"status": "escalated"})
            return end("escalated", reason=final.get("reason"))

        quote = final["quote"]
        amount = int(quote["amount_vnd"])

        if amount <= 0:
            trace.add("decision", {"status": "denied"})
            return end("denied", reason=quote.get("reason"))

        # 5. Host là nơi duy nhất được ghi tiền
        outcome = issue_refund(
            conn,
            claim_id,
            amount,
            crash_at=crash_at,
        )

        trace.add("host", {
            "ok": outcome["ok"],
            "reason": outcome["reason"],
        })

        if not outcome["ok"]:
            status = "failed" if outcome["conflict"] else "denied"
            return end(status, amount, outcome["reason"])

        return end("resolved", amount)

    finally:
        conn.close()
