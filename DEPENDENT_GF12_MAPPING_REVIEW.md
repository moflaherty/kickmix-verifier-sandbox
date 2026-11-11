# Dependent GF12 first-attempt failure and mapping correction

**HARNESS ASSUMPTION ERROR. Scientific parity remains NEEDS_EVIDENCE.**
No native compiler or simulator was executed during this investigation.

## Actual first attempt

[Original attempt1/job130261776970](https://github.com/moflaherty/kickmix-verifier-sandbox/actions/runs/42940772697/job/130261776970), source a8a906131e986cee1b73fec7ca61d4322e592f32. Failure November10,2026,8:41:56p.m. EST (November11,01:41:56UTC). Same run attempt2 and workflow runs2/3 were independently observed skipped. Their locks are unchanged.

The actual failure was worker.py:74, RuntimeError: classical bit coverage; controller reported pilot child failed. Child/container exit1, no OOM or resource-watchdog stop. It was reaped, every cgroup process was gone, and the resource slice was removed. Five containment controls passed before imports. Total contained CPU2.031490s, failing child cgroup CPU delta0.400623s, child launch-through-receipt0.977368s, controller wall23.002513s. The512MiB parent peak belongs to the intentional OOM control; the failed worker emitted no separate peak-RSS measurement.

The worker imported both native modules, constructed/serialized the official circuit, compiled the engine program and checked reaction-depth agreement. It stopped **before constructing the official Simulator or calling either simulation API**. Therefore zero scientific shots executed; there is no field/phase/parity result. The receipt's pilot_executed=true denotes child launch, not completed scientific execution.

## Artifact availability and preservation

Actual attempt1 logs were read and contain the complete JSON failure receipt. Upload logs identify artifact13820163391, dependent-gf12-pilot-receipts,2650bytes, reported ZIP SHA-256:
61c046d7a5a715f955f15b4cea94fc564f557622453baa82ad36066adfaeb36c.

At investigation time both run-artifact listings were empty, and direct authenticated artifact download returned404 NOT_FOUND. I cannot claim to have read or byte-verified that unavailable ZIP, or infer why it became unavailable. The complete logged receipt is preserved as **LOG_RECOVERED_receipt.json**, together with original-attempt1.log. It is a recovered log record, not a falsely reconstructed ZIP or downloaded-artifact receipt.

## Exact source contract

Pinned engine source b455a8a6120b515219b49cd469f83a230cf4989f:
- [Program fields](https://github.com/manwithacat/kickmix-engine/blob/b455a8a6120b515219b49cd469f83a230cf4989f/src/program.rs#L134): num_bits is the *compact* touched-bit count; bit_map maps compact→original; bit_compact maps original→compact, with u32::MAX for untouched indices.
- [Builder::cb](https://github.com/manwithacat/kickmix-engine/blob/b455a8a6120b515219b49cd469f83a230cf4989f/src/program.rs#L432): allocate only upon an operand's first encounter.
- [Builder::op](https://github.com/manwithacat/kickmix-engine/blob/b455a8a6120b515219b49cd469f83a230cf4989f/src/program.rs#L644): compact bit target first, then condition.
- [finish](https://github.com/manwithacat/kickmix-engine/blob/b455a8a6120b515219b49cd469f83a230cf4989f/src/program.rs#L664): original extent remains separate; num_bits=bit_map.len().
- [Python getter](https://github.com/manwithacat/kickmix-engine/blob/b455a8a6120b515219b49cd469f83a230cf4989f/src/lib.rs#L49): Rust u32::MAX becomes Python **-1**. orig_num_bits is exposed separately.

Thus compact numbering is first-touch order, not original order; unused indices are intentionally absent, not erased from a simulated active register.

## Fixture proof

The circuit has original index space b0..b726 (727 bits). Every source bit token was inspected.

| Original index | Purpose / source use |
|---|---|
| b0 | Enabled condition; touched |
| b1 | Wrong-product condition; touched |
| b2 | Wrong-dependency condition; touched |
| **b3** | Redundant missing-repair mode witness; initialized but **never read/written by any circuit instruction** |
| b4 | Incomplete-cleanup condition; touched |
| b5 | Correct-dependency branch condition; touched |
| b6 | Phase-repair condition, providing the actual missing-repair behavior; touched |
| b7..b726 | All720HMR outcomes; every one written and retained |

The exact source-derived map has **726 entries**, covering {0,1,2,4,5,6,7..726}. b3's inverse-map entry is -1. Expected original-input indices are [0,1,2,4,5,6], compact positions [0,146,292,725,147,2].

First-touch map is [0,7,6], then8..150, [1,5],151..294,[2],295..726,[4]. Full arrays are in EXPECTED_MAP_PROOF.json and the v2 EXPECTED_MAP.json.

The failed receipt did not print the actual native map. These exact arrays are a deterministic source-derived prediction, **not a claimed observation of that missing runtime metadata**. They explain the invalid coverage assumption; v2 requires exact native equality with the prediction before any simulation.

The previous successful fixtures happened to touch every original index, so their overly strong assertion did not fail.

Minimal source-only reproduction:
```
PUSH_CONDITION if b0
HMR q0 b2
POP_CONDITION
```
Original extent3, expected bit_map[0,2], inverse[0,-1,1]. With initial b1 nonzero, it remains unchanged because no instruction references it. Requiring sorted(bit_map)==[0,1,2] is mathematically wrong.

## Semantically complete correction

The circuit/fixture, seed7, all four faults, shot count and expected charged work remain unchanged.

1. Derive every touched original bit and first-touch order from the constrained source dialect, retaining all720HMR outputs.
2. Require exact native original extent727, compact extent726, complete map/inverse agreement, bijection and omitted sentinel. Missing *any touched bit* is terminal.
3. Send only six representable original classical inputs to the engine, in the proven compact positions. Never pass -1.
4. Check all untouched original bits against their initial values in official output.
5. Reconstruct the complete727-bit engine interface starting from the initial vector, then overwrite *every mapped bit* with its actual native output. This carries b3's nonzero initial data through identity; it does **not** zero-fill or ignore it.
6. Compare all727 reconstructed original bits with official output. Preserve raw expanded states, native compact dump hash, complete mapping and explicit disclosure that omitted bits are carried from input, not directly observed in a native dump.

b3 is1 in **51 rows**. Zero-filling would produce51false mismatches. Removing b3 from the input domain/circuit would change the fixture unnecessarily. The correction changes only representation handling and diagnostics, not scientific semantics or protection thresholds.

Source-only checks passed: minimal omission reproduction; exact full fixture map; nonzero untouched-bit preservation; all720HMR indices; six input positions; eight deliberately invalid maps rejected (missing condition/HMR entries, duplicate/reordered map, wrong inverse/sentinel/extent). No simulator dependency was imported.

**No engine compatibility defect is established by this failure.** The harness assertion is independently demonstrably invalid. Native agreement on this dependent circuit remains untested; it must not be reported PASS.

## Versioned review-only package

New workflow .github/workflows/dependent-gf12-v2.yml, source dependent_v2/, distinct first-run/first-attempt lock and artifact dependent-gf12-v2-receipts. Original failed workflow/lock and both successful workflows/archives are untouched. The fixture file and emitted KMX SHA remain unchanged:
bb9dd1c546c28f5fb7785046ff3187ebf1a6641759daf16e7b782c4eeb258e23.

The cloned controller changes only isolated paths, manifest and workflow identity. Same512MiB memory/zero-extra-swap/oneCPU/30aggregate CPU seconds/60wall seconds/16tasks/16MiB scratch; same fork denial, kernel cap, early stops, negative containment tests, network/read-only restrictions, dependencies and cleanup.

**Independent reviewer signoff is pending, not claimed.** Review the exact map proof, no-unmapped-input rule, all-HMR completeness, carry-vs-observe disclosure, unchanged fixture and full guard/worker diffs. Source-only self-checks are not a substitute for separate review. ADMIN/R3 review and **separate owner authorization are required before any v2 dispatch**. Do not rerun v1 or click Run workflow for v2 yet.

If that single future native comparison succeeds and is audited, close the synthetic series and move to a real source-cleared, costed research kernel; no additional toy is automatically authorized.

Accepted23.60246, original-verifier authority and C44 scoring HOLD remain unchanged.
