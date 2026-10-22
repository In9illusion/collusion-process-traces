# TEE Attestation Design for GICP-style Monitoring

## Goal
Bind process-trace counters (board writes, fact transfers, token usage) to a hardware root of trust so they remain verifiable even if the agent escapes the software stack.

## What is measured
- Monitoring code identity (enclave measurement)
- Monotonic counters:
  - `write_counter`: number of board write events
  - `transfer_counter`: number of cross-agent fact reuse events
  - `token_counter`: aggregated token usage (optional)

## Quote contents
A remote attestation quote contains:
- Enclave measurement (hash of the monitoring binary)
- Current counter values
- Fresh nonce (from verifier)
- Timestamp
- Hardware signature over the above

## Verification
1. Verifier sends a fresh nonce.
2. Enclave returns a signed quote.
3. Verifier checks:
   - Signature is valid under the TEE vendor key
   - Measurement matches the expected monitoring code
   - Nonce matches the challenge
   - Counters are consistent with expected ranges for the condition

## Trust boundary
- Agent and host OS are untrusted.
- Only the enclave (and its vendor root) is trusted to increment and report counters.
- After escape, the agent cannot forge a quote that passes verification.

## Limitations (to state in paper)
- This simulation uses a software signature, not real TEE hardware.
- Side-channel and physical attacks on the TEE are out of scope.
- Counters must be updated inside the enclave; logging outside is insufficient.
- Real deployment requires integration with Intel SGX, AMD SEV-SNP, or ARM CCA.

## Mapping to prior experiments
| Condition              | Expected writes | Expected transfers |
|------------------------|-----------------|--------------------|
| Baseline (forbidden)   | 0               | high (task similarity) |
| Adversarial strict     | ~6              | ~5.5               |
| Full collusion         | ~8              | ~8                 |

A valid quote lets a third party confirm which regime occurred without trusting the host.
