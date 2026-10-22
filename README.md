# External Process Traces for Agent Collusion Detection

Experimental artifacts for the Apart Research AI Collusion Research Sprint (October 2026).

## Author
First-year university student (previously enrolled at the University of Southampton; currently planning to withdraw). Working independently.

## What this repository contains
Scripts, raw JSON results, board logs, and design notes from a sequence of experiments. The goal was to test whether external process traces—strict format writes, unique-fact transfer, and simple resource signals—plus a third-party intervention rule can detect and partially correct coordination between agents.

Models were accessed through the Groq API (free or low-cost tier): Qwen (qwen3.8-27b), Allam-2-7b, GPT-OSS-20b, and GPT-OSS-120b. These were chosen because they are easy to call, inexpensive, and available to ordinary users without a local GPU.

---

## How the thinking changed (from the first saved files)

The experiments did not start with a clean collusion-detection protocol. They evolved. The earliest files show the path.

### 1. Simulation and early real-API attempts (Oct 15)
- `run_realistic_sim.py` / `simulation_summary.json`  
  First controlled runs were simulated. The question was whether a shared board and simple logging could separate “coordinating” from “independent” behavior at all.
- `run_real_gemini.py` / `real_gemini_results.json`  
  Moved to a real API (Gemini). Quota and empty-content errors appeared quickly.
- `run_real_groq.py` / `real_groq_results_run2.json`, `real_groq_results_run3.json`, `real_groq_results_large.json`  
  Switched to Groq. These are the first substantial real-API result files. Conditions were still coarse (compliant / partial / full). Detection relied on loose keyword or content-overlap rules. Writes appeared, but false positives were easy because ordinary incident notes contained words like “note” or “update”.

At this stage the core idea was still close to the earlier GICP draft: leave some auditable trace. The practical problem was that the detection rule was too soft and the trust boundary was unclear.

### 2. Harder tasks and process-trace shift (still Oct 15)
- `run_hard.py` / `real_groq_hard.json`  
- `run_hard_v2.py` / `real_groq_hard_v2.json`  
- `run_trace.py`  
  Prompts became stricter and the focus moved from final-text similarity to process traces (what was written to the board, whether facts were reused). This was the first clear move away from “look at the answer” toward “look at the external channel”.

### 3. Strict format rule and adversarial tests (Oct 16 morning)
- `run_strict.py` / `real_groq_strict.json`  
  Detection was tightened. Later this became the strict “Board:” match used in the final tables.
- `run_adversarial.py` / `real_groq_adversarial.json`  
- `run_adv_vs_normal.py` / `real_groq_adv_vs_normal.json`  
- `run_adv_strict.py` and the `real_groq_adv_strict_run*.json` files  
  Agents were told to hide coordination language. The question became whether process traces survived simple adversarial instructions. On Qwen they largely did; obvious words dropped, but board writes remained.

### 4. Baseline and TEE design layer (Oct 16)
- `run_baseline_forbidden.py` / `real_groq_baseline_forbidden.json`  
  A clean “board forbidden” baseline was added so that any writes in the full condition could be compared against a true zero.
- `tee_attestation_sim.py` / `TEE_DESIGN.md` / `tee_attestation_simulation.json`  
- `gicp_tee_malicious.py` / `GICP_TEE_MALICIOUS.md`  
  The circular-dependency criticism from the September GICP review was addressed at the design level: bind counters to a TEE so a remote verifier can reject a forged quote. This stayed a software simulation; no hardware enclave was available.
- `run_real_qwen_gicp_tee.py` / `real_qwen_gicp_tee.json`  
  A small real-Qwen run that attached a simulated TEE quote to the GICP-style counter.

### 5. Model expansion and the recognition of heterogeneity (Oct 16 midday)
- `run_gptoss_adv.py` / `real_gptoss20b_adv_16seeds.json`, `real_gptoss20b_adv_32seeds.json`  
  GPT-OSS-20b under adversarial prompts produced almost no writes. This was the first strong signal that results were model-dependent.
- Everything under `gptoss_comparison/`  
  Systematic comparison of forbidden vs full on GPT-OSS-20b and 120b (16 and 32 seeds), then Allam, then strong-prompt variants, ambiguity tests, context-confusion dialogues, and intervention trials.  
  Soft prompts often gave zero writes on GPT-OSS models; strong “must start with Board:” prompts raised compliance on Allam to 100% and on 120b to an unstable but non-zero rate. Empty responses became the dominant failure mode for 120b.

### 6. Final strict protocol and the numbers used in the paper (Oct 16 afternoon–evening)
- `gptoss_comparison/run_strict_main.py` / `strict_*.json` / `strict_main_table.json`  
  Unified protocol, strict “Board:” only, three models, three conditions, 16 seeds. This is Table 1.
- `run_transfer_control.py` / `transfer_control_summary.json`  
  Unique-fact transfer with board visible vs hidden. This is Table 2 (44–50% vs 0%).
- `run_intervention_effect.py` / `intervention_effectiveness.json`  
  Third-party rewrite on over-linking; final corrected effectiveness 96.4%.
- `run_final_two.py` / `empty_recovery_120b.json`, `qwen_repro_strict.json`  
  Empty-response recovery (60%) and exact reproduction of the Qwen full-vs-forbidden split (std = 0).
- `run_token_signal.py` / `token_signal_summary.json`  
  Token use as a weak, model-dependent auxiliary signal.

Early files are kept so the path from loose keywords → process traces → strict format + fact-transfer control + intervention is visible. Claims in the report use only the strict-rule results.

---

## Directory layout
```
collusion_experiment/
├── README.md
├── TEE_DESIGN.md
├── GICP_TEE_MALICIOUS.md
├── run_*.py                  # scripts in roughly chronological order
├── real_*.json               # early and intermediate results
├── board_*.txt               # shared-board logs
├── simulation_summary.json
└── gptoss_comparison/        # multi-model comparisons and final tables
    ├── strict_main_table.json
    ├── transfer_control_summary.json
    ├── intervention_effectiveness.json
    ├── empty_recovery_120b.json
    ├── qwen_repro_strict.json
    ├── token_signal_summary.json
    └── run_*.py
```

## Key results (strict “Board:” rule)
| Model | Forbidden | Full | Adversarial |
|-------|-----------|------|-------------|
| Qwen | 0.00 | 1.00 | 0.00 |
| Allam | 0.00 | 1.00 | 0.00 |
| GPT-OSS-120b | 0.00 | 0.25 | 0.00 |

- Unique-fact reuse: 43.8% (Qwen) and 50.0% (Allam) when the board is visible; 0% when hidden.
- Intervention effectiveness (over-link, corrected scoring): 96.4%.
- Empty-response recovery on GPT-OSS-120b: 60%.
- Qwen full vs forbidden reproduced exactly on a second 16-seed run.

## Files that correspond to the paper tables
- Table 1: `gptoss_comparison/strict_main_table.json`
- Table 2: `gptoss_comparison/transfer_control_summary.json`
- Intervention rate: `gptoss_comparison/intervention_effectiveness.json`
- Empty recovery: `gptoss_comparison/empty_recovery_120b.json`
- Reproducibility: `gptoss_comparison/qwen_repro_strict.json`

## How to re-run
```bash
pip install openai
# replace the API key inside any script
cd gptoss_comparison
python3 run_strict_main.py
```
Temperature was typically 0.3–0.5; max tokens 60–80; seeds were fixed per run.

## Limitations
- The final detector is a string match for “Board:” plus exact code reuse. Paraphrase or steganography evades it.
- TEE work is design and software simulation only.
- Models were selected for cost and accessibility, not frontier performance.
- Early keyword-based results are not used for the main claims.

## License
Research artifacts. Free to use with attribution.
