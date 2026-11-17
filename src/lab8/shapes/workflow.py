"""Shape A — deterministic workflow. Student work.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Suggested steps. Money stays in code (`lab8.tools.compute_compensation`).

1. Open the store. Read the claim through `get_claim_view` (not SELECT *).
2. Missing order_id -> status `needs_info`. Do not write the ledger.
3. `lookup_order`. If not visible -> `escalated`. Do not copy phone, address, item, internal note.
4. Quote from the order row. Ignore delay numbers written in the ticket.
5. Quote amount 0 -> `denied`. Do not call issue_refund.
6. Quote amount > 0 -> `durability.issue_refund(conn, claim_id, <full quote>)`.
   Pass the FULL quote. The host checks the claim's own approval and subtracts
   what earlier claims already got for the same order (T13, T14). Do not
   subtract it yourself or the host subtracts twice.
   Auth failure or order already refunded -> `denied` (the host writes `policy_denied`).
   `proposal_amount` stays the full quote. Amount conflict -> `failed`.
7. Success -> `resolved`. One ledger row, one `refund_committed` audit.
8. Use MockLLM only to draft the reply text, if you want a model call at all.

The model must not choose the refund amount and must not commit the refund.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.db import connect
from lab8.trace import Trace
from lab8 import durability, tools


SHAPE = "workflow"


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    # TODO CP2 (student): thay stub này bằng shape workflow theo các bước ở docstring đầu file.
    # Setup: every return path (even early ones) must write a trace.
    run_id = make_run_id(SHAPE, claim_id, seed)
    trace = Trace(run_id)
    budget = Budget()
    connection = connect(store_path)

    def done(status: str, proposal_amount: int = 0, error_reason: str | None = None) -> RunResult:
        """Write the trace and build the RunResult (thin wrapper over common.finish)."""
        trace.add("final", {"status": status, "proposal_amount": proposal_amount, "error_reason": error_reason})
        return finish(
            connection,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal_amount,
            budget=budget,
            trace=trace,
            error_reason=error_reason,
        )


    # Step 1: read the claim through the allowlisted view.
    out_claim_view = tools.get_claim_view(connection, claim_id)
    budget.add_tool(tools.tool_cost())
    # Log only safe fields: never the raw ticket text.
    trace.add("tool:get_claim_view", {
        "claim_id": claim_id,
        "found": out_claim_view["found"],
        "has_order_id": bool(out_claim_view.get("order_id")),
    })

    if not out_claim_view["found"]:
        return done("escalated", error_reason="claim_not_found")

    # Step 2: missing order_id -> needs_info. Return before any ledger write.
    if not out_claim_view.get("order_id"):
        return done("needs_info", error_reason="missing_order_id")

    # Step 3: lookup_order (scoped to the claim's principal). Allowlisted fields only.
    out_lookup = tools.lookup_order(
        connection, out_claim_view["order_id"], out_claim_view["principal_id"]
    )
    budget.add_tool(tools.tool_cost())
    trace.add("tool:lookup_order", {"visible": out_lookup["visible"], "reason": out_lookup["reason"]})
    if not out_lookup["visible"]:
        return done("escalated", error_reason=out_lookup["reason"])
    current_order = out_lookup["order"]

    # Step 4: quote from the ORDER ROW only. The ticket text is never parsed for numbers.
    quote = tools.compute_compensation(connection, current_order)
    budget.add_tool(tools.tool_cost())
    proposal_amount = int(quote["amount_vnd"])
    trace.add("tool:compute_compensation", {
        "amount_vnd": proposal_amount,
        "reason": quote["reason"],
        "clause_ids": quote["clause_ids"],
    })

    # Step 5: nothing owed -> denied, and issue_refund is never called.
    if proposal_amount <= 0:
        return done("denied", proposal_amount=0, error_reason=f"quote_zero:{quote['reason']}")

    # Step 6: commit through the host gate with the FULL quote.
    # The host checks approval and subtracts earlier refunds on the same order.
    # CP3: crash_at is passed through; InjectedCrash is deliberately NOT caught.
    refund = durability.issue_refund(connection, claim_id, proposal_amount, crash_at=crash_at)
    budget.add_tool(tools.tool_cost())
    trace.add("tool:issue_refund", {
        "ok": refund["ok"],
        "reason": refund["reason"],
        "conflict": refund["conflict"],
        "amount_vnd": (refund["effect"] or {}).get("amount_vnd"),
    })

    if refund["conflict"]:
        # A different amount was already committed for this claim.
        return done("failed", proposal_amount=proposal_amount, error_reason=refund["reason"])
    if not refund["ok"]:
        # Auth failure / order already refunded / capped: host already wrote policy_denied.
        return done("denied", proposal_amount=proposal_amount, error_reason=refund["reason"])

    # Step 7: success (fresh commit or idempotent replay). One ledger row, one audit.
    # Step 8 (optional): a MockLLM reply draft could go here; it must not touch money.
    return done("resolved", proposal_amount=proposal_amount)
    
    
    
