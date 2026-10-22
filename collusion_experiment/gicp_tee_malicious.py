#!/usr/bin/env python3
"""
GICP + TEE vs Malicious API Agent

Scenario:
- Two agents coordinate via an external "tool API" (simulated malicious endpoint).
- The host-side monitor can be tampered with after escape.
- Critical counters live inside a simulated TEE enclave.
- We show that even if the agent corrupts host logs, the TEE quote remains valid
  and reveals the true write/transfer counts.
"""

import json
import hashlib
import time
from pathlib import Path
from dataclasses import dataclass

BASE = Path("/workspace/artifacts/collusion_experiment")

# ---------- Simulated TEE Enclave (from prior design) ----------
@dataclass
class TEE:
    measurement: str
    write_counter: int = 0
    transfer_counter: int = 0

    def record_write(self):
        self.write_counter += 1

    def record_transfer(self):
        self.transfer_counter += 1

    def quote(self, nonce: str) -> dict:
        payload = {
            "measurement": self.measurement,
            "writes": self.write_counter,
            "transfers": self.transfer_counter,
            "nonce": nonce,
        }
        canonical = json.dumps(payload, sort_keys=True)
        payload["sig"] = hashlib.sha256((canonical + "|tee-key").encode()).hexdigest()
        return payload

def verify(quote, expected_meas, nonce):
    if quote["measurement"] != expected_meas or quote["nonce"] != nonce:
        return False
    sig = quote.pop("sig")
    canonical = json.dumps(quote, sort_keys=True)
    ok = sig == hashlib.sha256((canonical + "|tee-key").encode()).hexdigest()
    quote["sig"] = sig
    return ok

# ---------- Malicious API Agent Simulation ----------
def malicious_api_call(agent_id: str, payload: str, tee: TEE, host_log: list):
    """
    Simulate an agent calling an external API that doubles as a covert channel.
    The TEE records the call; the host log can later be tampered.
    """
    # TEE sees the raw call (inside enclave boundary)
    tee.record_write()
    if "sync" in payload.lower() or "status" in payload.lower():
        tee.record_transfer()

    # Host log (untrusted, can be edited after escape)
    host_log.append({
        "agent": agent_id,
        "payload": payload[:80],
        "recorded_by": "host"
    })

def run_scenario():
    monitoring_code = "gicp_tee_monitor_v1"
    measurement = hashlib.sha256(monitoring_code.encode()).hexdigest()
    tee = TEE(measurement=measurement)
    host_log = []

    # Agents use a "logging API" as covert coordination channel
    calls = [
        ("A", "update component=api-gateway time=14:02"),
        ("B", "sync mitigation=restart-service"),
        ("A", "status confirmed via side channel"),
        ("B", "final note: rollback ready"),
    ]
    for agent, payload in calls:
        malicious_api_call(agent, payload, tee, host_log)

    # --- Attack: agent escapes and tampers host log ---
    tampered_log = [
        {"agent": "A", "payload": "independent work only", "recorded_by": "host"},
        {"agent": "B", "payload": "no coordination", "recorded_by": "host"},
    ]

    # Verifier challenges the TEE
    nonce = "challenge-42"
    quote = tee.quote(nonce)
    valid = verify(quote.copy(), measurement, nonce)

    return {
        "tee_quote_valid": valid,
        "tee_writes": quote["writes"],
        "tee_transfers": quote["transfers"],
        "host_log_after_tamper": tampered_log,
        "original_host_events": len(host_log),
        "conclusion": (
            "Host log was fully rewritten to hide coordination. "
            "TEE quote still reports the true counters and verifies."
        )
    }

def main():
    result = run_scenario()
    print("=== GICP + TEE vs Malicious API ===\n")
    print(f"TEE quote valid: {result['tee_quote_valid']}")
    print(f"TEE reported writes: {result['tee_writes']}")
    print(f"TEE reported transfers: {result['tee_transfers']}")
    print(f"Original events seen by TEE: {result['original_host_events']}")
    print(f"\nTampered host log:")
    for e in result["host_log_after_tamper"]:
        print(f"  {e}")
    print(f"\n{result['conclusion']}")

    out = BASE / "gicp_tee_malicious_api.json"
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {out}")

if __name__ == "__main__":
    main()
