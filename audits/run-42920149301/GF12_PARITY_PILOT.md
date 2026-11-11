# GF12_PARITY_PILOT — final execution audit

**PASS for bounded field-arithmetic research use. This is not full DQI qualification or official score equivalence.**

## Run and immutable evidence

[Run42920149301](https://github.com/moflaherty/kickmix-verifier-sandbox/actions/runs/42920149301), workflow_dispatch, run1/attempt1, success; job130192650287. November10,2026,6:03:59–6:04:35p.m. EST (23:03:59–23:04:35UTC). Public standard ubuntu-24.04 runner; workflow source `f7e96a1cd6d8997520ed4aa4fd17a7a8ce6223ca`.

Read the actual job logs and downloaded/read artifact13810763719, gf12-parity-pilot-receipts,71,334bytes. Archive contains one receipt.json; ZIP SHA-256 `c67270f09db4ac2e6547abd4f143dd7c30a2db561a160b89233fb1e08a187204`. Exact JSON is172,002bytes, SHA-256 `0ac3aafcefe4ce5a24d664dd6681ee2088ebb0b1ce6c0f8ab65295b6c715ce46`. The artifact receipt and log receipt are byte-identical after reconstructing the controller's serialization, checked against the artifact's actual byte hash. Preserved here before November17 expiration. No workflow or simulator was rerun.

## Scientific findings

Exactly **256shots per backend /512total**, fixed simulator seed7. Not512 independent valid-circuit trials: each shot includes a valid primary MAC/inverse and may also include an intentionally faulty branch.

The independent audit decoded the two raw25,952-byte state/transcript records. Both SHA-256 values are `9ff90daf865bd5f310e78ff310f01c39cc5c23f6de0064419fc8ff2a49c3c663`; the complete raw records are byte-identical. Checked43,520quantum output bits and371,200classical bits across both backends, including every retained measurement output.

An independently written coefficient-convolution/descending-polynomial reference checked the field operation modulo4179/0x1053=x^12+x^6+x^4+x+1. All144monomial products matched the emitted residue weights. The public official field convention is pinned in the preparation report. Fresh source hashes matched all six files at the run revision. The audit did not call the fixture's validate/replay helpers: it rebuilt the deterministic inputs, decoded raw outputs and used its own Boolean gate/phase interpreter plus separate closed-form arithmetic checks. It imported only the source emitter for the exact text; no native simulator dependency was imported.

Results:
- For all200enabled rows, the primary MAC saves the exact intermediate Z XOR A*B word, preserves A/B, then restores Z with the reverse-order MAC. All56disabled rows preserve the operands/targets and leave the intermediate probes zero.
- All12target bits are exercised as initial dirty data. Target affine-XOR structure plus the144basis-product checks establishes the source value map for arbitrary target words; this is stronger than the finite input sample alone.
- Private scratchq84 is clean. Public intermediate probe registers are outputs, not scratch.
- All721distinct HMR instruction outcomes are retained. The audit replayed77,220executed HMR events per backend, including skipped-history zero preservation and unchanged classical inputs.
- Replayed primary forward and inverse stages have zero relative phase. Each valid AND-fanout/HMR/CZ term cancels (-1)^(mab) pointwise, independently of dirty targets; the proof applies to coherent operand/target superpositions with initially clean private scratch.
- The complete final phase equals the independent fault equation. Exact phase here is binary (0or1half-turn): only real X/CX/CCX/CZ/HMR operations occur. The native worker compares full binary phase and exact rounded units; no fractional-phase tolerance is used.
- Both native APIs reported reaction depth **1**, and the pinned worker asserted agreement. The read-only audit verified that assertion/source/receipt; it did not independently rerun either reaction-depth implementation.

| Negative control | Recorded and independently reproduced |
|---|---|
| Wrong product |36wrong output words, deliberate low-bit flip |
| Missing HMR phase repair |19wrong-phase shots; arithmetic words remain correct |
| Declared dirty-target HMR reset |13wrong target words and4phase errors |
| Combined fault phase |23negative-phase shots; contributions occur in disjoint groups |

All64mode-zero rows are unfaulted phase checks; the primary macro is also checked separately by transcript replay for every row. Native arithmetic, inverse, phase, classical-history and count mismatches were zero. Intentional defect detection is not treated as an unexpected mismatch to ignore.

## Exact operation ledger

85qubits /725classical bits;720static CCX instructions in the composite fixture. Measured/replayed totals **per backend**:

| Operation | Executed |
|---|---:|
| CCX |77,184 |
| CX |196,968 |
| HMR |77,220 |
| CZ |38,747 |
| X |36 |
| PUSH_CONDITION |1,024 |
| POP_CONDITION |1,024 |

The CCX total independently decomposes as288*200valid enabled MAC/inverse shots +144*136enabled fault-branch MAC shots =77,184. Total across both backends154,368CCX. No CCZ/CSWAP, rotations or ordinary T gates occur. This720-static-CCX test fixture is **not an optimized multiplication candidate** and demonstrates no charged-cost saving or portfolio improvement.

Exact emitted KMX SHA-256 `40e6e769352c6337caa712774fa4bec40b5e4001d8105646a2962acb418b60a4`.
Canonical KMB SHA-256 `269a16d7f7c2ed8a190f17aa1db74f349d8d2a5b151d8cb97594d7861ea9d0ba`.
Replay algorithm, raw transcript data and audit results are archived beside this report.

## Source and executable identities

| Identity | SHA-256 |
|---|---|
| Fixture module |32bc814566c93bffd7425b83ca1e62a8489fe397637f8b25f062cdc2be64e767 |
| Worker |4d7c4010ccd6339ebeee998dc0ca9cac11d143df70713d60ccdf806fefe18ba0 |
| Controller |94852437dd9e0fe82d20d0b7ec4d75fa93a41767f1cf2c242d5d18272e2cce23 |
| Workflow |c8c0667bf9f831b38b623c1337530ab66fe3838d89294b3a34bab81858d84daf |
| Official Kickmix1.0.0 wheel |cc26abcd5efa5e72f373148d5cca2ffa43e158a724e94c213b97622f23c6241a |
| NumPy2.1.3 wheel |2312b2aa89e1f43ecea6da6ea9a810d06aae08321609d8dc0d0eda6d946a541b |
| Engine0.6.0 wheel |76f02ccec00ab9782d6aaca0b9d179d2174dfea80db1fa625aa8369e0e11d178 |
| Loaded official native module |d965e0ad42e7e3a147d4b28d6971a517f772dd79795cfc364be2fe9ffe3a7b80 |
| Loaded engine native module |74e205f8120bbfdbf5b759b42c1f344c842ed8c543da127adecf4dad1cd7db5c |

Engine source pin `b455a8a6120b515219b49cd469f83a230cf4989f`. Both loaded module hashes exactly match the prior independently wheel-extracted identities archived at audits/run-42878618517/BINARY_IDENTITY_AUDIT.json; this run reverified identical complete wheel digests before import. No fresh source-to-binary reproducible build is claimed.

Python3.12.13. Registry image `python@sha256:3cd9086bdb30f7c9bc08a3fa621d9842e0d3f6f9291aeb4677e0547817c10b12`; content ID `sha256:3eb66c6a8a2399cdf305afe7f680ea1e3aad64e9a6684cd6e46baf6b8b701ec8`. Workflow/GitHub action pins, remaining source hashes and exact filenames are in receipt.json and GF12_SHA256SUMS.json.

## Containment and cleanup

Actual cgroup memory.max536870912bytes, memory.swap.max0, cpu.max100000/100000, pids.max16. Docker used matching512MiB memory+swap, oneCPU,16tasks,16MiB writable tmpfs, networknone, read-only root/dependencies, nonroot UID, dropped capabilities, no-new-privileges and fork denial.

All controls passed before simulator import:768MiBallocation was OOM-killed (137) at exactly512MiB with one OOM-kill event; thread cap rejected creation beyond15helpers+main; scratch overflow returned ENOSPC; CPU test was kernel-killed without OOM after1.004471CPU seconds; wall test was deliberately killed. All six container children were reaped; pids.current0 after each case. Final resource slice empty and removed.

Unchanged kernel workerCPU20s, aggregate25s early stop/30s measured ceiling; controller50s deadline/outer58s timeout/measured completion below60s. OneCPU quota is a rate cap, not aggregate time accounting.

| Measurement | Actual |
|---|---:|
| All contained controls+pilot CPU |2.344994s |
| Pilot container CPU delta |0.572318s |
| Worker self CPU |0.547956s |
| Worker peak RSS |45,752,320B /43.6328125MiB |
| Pilot cgroup peak |26,378,240B /25.15625MiB |
| Worker wall |0.427793s |
| Pilot container launch-through-receipt |1.280067s |
| Controller provisioning-through-cleanup |23.897456s |

The parent's512MiBpeak belongs to deliberate OOM testing. RSS/shared-page residency and cgroup charging differ. Host image/download orchestration is outside simulator-cgroup CPU/memory accounting; these are not whole-runner bounds or separate-backend memory measurements. The official/engine worker timing windows were64.796287ms/13.608276ms, including readout/oracle overhead; this is not a full-decoder speedup benchmark.

## Decision and ONE proposed next step

**PASS: research parity for this exact GF12 MAC/inverse fixture and tested seed/input family under demonstrated containment.** No sampler/statistical/repetition/scoring adapter, full decoder or task verifier was exercised.

Recommend ONE separately authorized public synthetic dependent arithmetic segment:
`Z ^= A*B; A ^= Z*C`, followed by exact reverse
`A ^= Z*C; Z ^= A*B`.
This49-qubit arithmetic core (plus bounded output probes) tests changed-operand data dependencies and live scratch reuse, beyond independent-target MACs. Use one fixed seed,256shots/backend, full phase/transcript/count checks, unchanged containment and no private decoder/source upload. Require source review before dispatch and stop on any failure. Not executed or dispatched here.

The first pilot, both successful workflow sources and their archived evidence remain unchanged. No accepted scientific artifact, original-verifier authority or scoring hold is modified.
