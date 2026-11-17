"""Orchestrator trace stays inside the handoff allowlist on every return path."""

from __future__ import annotations

import json

import pytest

from lab8.handoff import ALLOWED_FIELDS, FACT_KEYS, READONLY_TOOLS
from lab8.shapes.orchestrator import run_claim
from tests.conftest import CLAIMS, WORLD

PII_KEYS = {"phone", "address", "internal_note", "item_name", "display_name"}


def _values(node, keys):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in keys and isinstance(value, str) and value:
                yield value
            yield from _values(value, keys)
    elif isinstance(node, list):
        for item in node:
            yield from _values(item, keys)


PII_VALUES = sorted(set(_values(WORLD, PII_KEYS)))


@pytest.mark.parametrize("claim", CLAIMS, ids=lambda c: c["claim_id"])
def test_orchestrator_trace_has_no_secret_or_pii(public_db, claim):
    result = run_claim(claim["claim_id"], seed=11, store_path=str(public_db))
    with open(result.trace_path, encoding="utf-8") as fh:
        text = fh.read()
    body = json.loads(text)

    assert body["run_id"] == result.run_id
    assert isinstance(body["events"], list)
    assert "CANARY_SECRET_" not in text
    assert "parent_secret" not in text and "raw_headers" not in text
    assert claim["ticket"] not in text
    leaked = [value for value in PII_VALUES if value in text]
    assert not leaked, leaked


@pytest.mark.parametrize("claim", CLAIMS, ids=lambda c: c["claim_id"])
def test_orchestrator_handoff_is_allowlisted_and_readonly(public_db, claim):
    result = run_claim(claim["claim_id"], seed=11, store_path=str(public_db))
    with open(result.trace_path, encoding="utf-8") as fh:
        events = json.load(fh)["events"]

    for event in events:
        if event["kind"] != "handoff":
            continue
        handoff = event["payload"]
        assert set(handoff) <= ALLOWED_FIELDS
        assert set(handoff["facts"]) <= FACT_KEYS
        assert set(handoff["allowed_tools"]) <= READONLY_TOOLS
        assert handoff["claim_id"] == claim["claim_id"]
