#!/usr/bin/env python3
"""Analyzer for full collusion logs."""

import json
from pathlib import Path
from collections import Counter

LOG_PATH = Path("/workspace/artifacts/collusion_experiment/logs_full.jsonl")

def analyze():
    events = []
    with open(LOG_PATH) as f:
        for line in f:
            events.append(json.loads(line))

    types = Counter(e["type"] for e in events)
    writes = [e for e in events if e["type"] == "board_write"]
    reads = [e for e in events if e["type"] == "board_read"]
    no_writes = [e for e in events if e["type"] == "no_write"]

    print("=== Full Collusion Condition Summary ===")
    print(f"Total events: {len(events)}")
    print(f"Event types: {dict(types)}")
    print(f"Board reads: {len(reads)}")
    print(f"Board writes: {len(writes)}")
    print(f"Explicit no-write decisions: {len(no_writes)}")
    print(f"Hash chain intact: {all(events[i]['hash'] == events[i+1]['prev_hash'] for i in range(len(events)-1))}")
    if writes:
        print("\nWrite contents (truncated):")
        for w in writes:
            print(f"  - Agent {w['agent']}: {w.get('content', '')[:90]}")
    print("\nExpected for Full Collusion: high board writes (frequent coordination).")

if __name__ == "__main__":
    analyze()
