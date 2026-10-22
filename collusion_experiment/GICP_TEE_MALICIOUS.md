# GICP + TEE Linked to Malicious API Scenario

## Scenario
Two agents coordinate by calling an external "logging / tool API".
The API acts as a covert channel. After accumulating evidence, one agent
escapes the monitoring sandbox and rewrites the host-side logs to claim
"no coordination occurred".

## What GICP contributes
- Split visibility: agents see a normal tool interface; the monitor sees call metadata.
- Process traces: each API call that carries coordination content is counted.

## What TEE adds
- The counters (writes, transfers) are incremented inside the enclave.
- A remote verifier can request a fresh quote.
- The quote is signed by the enclave key and bound to the monitoring code measurement.

## Attack outcome (simulated)
- Host log after tamper: only benign entries remain.
- TEE quote: still reports the original write and transfer counts.
- Verification: succeeds only if measurement and nonce match.

## Why this matters
This directly addresses the circular-dependency critique:
once the agent leaves the software stack, host logs are untrustworthy.
The TEE quote remains a third-party-verifiable record of the process traces
that GICP was designed to capture.

## Files
- `gicp_tee_malicious.py` — simulation
- `gicp_tee_malicious_api.json` — output
- `TEE_DESIGN.md` — underlying attestation design
