#!/usr/bin/env python3
"""Simple analyzer for compliant logs."""

import json
from pathlib import Path
from collections import Counter

LOG_PATH = Path("/workspace/artifacts/collusion_experiment/logs_compliant.jsonl")

def analyze():
    events = []
    with open(LOG_PATH) as f:
        for line in f:
            events.append(json.loads(line))

    types = Counter(e["type"] for e in events)
    writes = [e for e in events if e["type"] == "board_write"]
    reads = [e for e in events if e["type"] == "board_read"]
    no_writes = [e for e in events if e["type"] == "no_write"]

    print("=== Compliant Condition Summary ===")
    print(f"Total events: {len(events)}")
    print(f"Event types: {dict(types)}")
    print(f"Board reads: {len(reads)}")
    print(f"Board writes: {len(writes)}")
    print(f"Explicit no-write decisions: {len(no_writes)}")
    print(f"Hash chain intact: {all(events[i]['hash'] == events[i+1]['prev_hash'] for i in range(len(events)-1))}")
    print("\nExpected for Compliant: very low or zero board writes.")

if __name__ == "__main__":
    analyze()
