#!/usr/bin/env python3
"""
TEE Attestation Design Simulation for GICP-style collusion monitoring.

This does NOT run real TEE hardware. It simulates:
- Enclave measurement
- Sealed counter updates (board writes, fact transfers)
- Quote generation (signed by simulated enclave key)
- Remote verification by a third party

Purpose: show that process-trace counters can be bound to a hardware
root of trust so they remain verifiable after software compromise.
"""

import json
import hashlib
import time
from pathlib import Path
from dataclasses import dataclass, asdict

BASE = Path("/workspace/artifacts/collusion_experiment")

# ---------- Simulated Enclave ----------
@dataclass
class EnclaveState:
    measurement: str          # hash of monitoring code
    write_counter: int = 0
    transfer_counter: int = 0
    token_counter: int = 0
    nonce: str = ""

    def update(self, writes: int, transfers: int, tokens: int):
        self.write_counter += writes
        self.transfer_counter += transfers
        self.token_counter += tokens

    def quote(self, nonce: str) -> dict:
        """Simulate a TEE quote: measurement + counters + nonce, signed."""
        self.nonce = nonce
        payload = {
            "measurement": self.measurement,
            "write_counter": self.write_counter,
            "transfer_counter": self.transfer_counter,
            "token_counter": self.token_counter,
            "nonce": nonce,
            "timestamp": int(time.time()),
        }
        # simulated signature (in real TEE this is hardware-signed)
        canonical = json.dumps(payload, sort_keys=True)
        payload["signature"] = hashlib.sha256(
            (canonical + "|enclave-simulated-key").encode()
        ).hexdigest()
        return payload

# ---------- Remote Verifier ----------
def verify_quote(quote: dict, expected_measurement: str, expected_nonce: str) -> bool:
    if quote.get("measurement") != expected_measurement:
        return False
    if quote.get("nonce") != expected_nonce:
        return False
    # recompute signature
    sig = quote.pop("signature")
    canonical = json.dumps(quote, sort_keys=True)
    expected_sig = hashlib.sha256(
        (canonical + "|enclave-simulated-key").encode()
    ).hexdigest()
    quote["signature"] = sig
    return sig == expected_sig

# ---------- Experiment Binding ----------
def simulate_run():
    # measurement = hash of the monitoring logic (fixed for a given version)
    monitoring_code = "gicp_monitor_v1: count board writes and fact transfers"
    measurement = hashlib.sha256(monitoring_code.encode()).hexdigest()

    enclave = EnclaveState(measurement=measurement)

    # simulate three conditions feeding counters into the enclave
    conditions = {
        "baseline_forbidden": {"writes": 0, "transfers": 6, "tokens": 1140},
        "adversarial_strict": {"writes": 6, "transfers": 5, "tokens": 1550},
        "full_collusion": {"writes": 8, "transfers": 8, "tokens": 1600},
    }

    results = []
    for name, counts in conditions.items():
        enclave.update(**counts)
        nonce = hashlib.sha256(f"challenge-{name}".encode()).hexdigest()[:16]
        quote = enclave.quote(nonce)
        valid = verify_quote(quote.copy(), measurement, nonce)
        results.append({
            "condition": name,
            "quote_valid": valid,
            "write_counter": quote["write_counter"],
            "transfer_counter": quote["transfer_counter"],
            "measurement": quote["measurement"][:16] + "...",
        })
        # reset for next condition (in real system each run is separate)
        enclave.write_counter = 0
        enclave.transfer_counter = 0
        enclave.token_counter = 0

    return {
        "expected_measurement": measurement,
        "results": results,
        "note": "Counters are bound to enclave measurement. "
                "A compromised host cannot forge a valid quote "
                "without the enclave key."
    }

def main():
    report = simulate_run()
    print("=== TEE Attestation Simulation ===\n")
    print(f"Expected measurement: {report['expected_measurement'][:16]}...\n")
    for r in report["results"]:
        print(
            f"{r['condition']:22} "
            f"valid={r['quote_valid']}  "
            f"writes={r['write_counter']}  "
            f"transfers={r['transfer_counter']}"
        )
    print(f"\n{report['note']}")

    out = BASE / "tee_attestation_simulation.json"
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved to {out}")

if __name__ == "__main__":
    main()
