# FAST_VERIFIER_CI_PILOT — verified execution audit

**SYNTHETIC_PILOT_PASS. GO for another bounded research comparison; no full-task qualification.**

[Run 42878618517](https://github.com/moflaherty/kickmix-verifier-sandbox/actions/runs/42878618517), owner-dispatched, run/attempt 1/1, completed/success. November 10, 2026, 1:46:42–1:47:34 p.m. EST (18:46:42–18:47:34 UTC). Job 130048568906: standard ubuntu-24.04 / Ubuntu 24.04.5, image 20261101.360.1. Contents/metadata read-only; checkout authentication removed before the experiment. No simulator rerun during audit.

## Integrity

Source commit: `f2b1ef7c61ac85519dcfee187786fd0b2e4163e2`. All seven source hashes independently recomputed from that public revision matched the receipt. The fixture literal matched its hash.

Artifact 13793086925: parity-pilot-receipts, 4,087 bytes.
ZIP SHA-256: `ff62e66753bc267793727554dd8a50f8124601540af15cb4ea87cb94d0078706`.
Exact receipt.json SHA-256: `c1973c7999ef792766825efa16cbffe8a82a74f9514b8c02760151031cca90b9`.
The actual artifact receipt exactly matches the JSON in the job log. Exact receipt bytes are preserved here before the original artifact's November 11 expiry.

Engine source v0.6.0: `b455a8a6120b515219b49cd469f83a230cf4989f`.
The audit independently fetched the two published simulator wheels without executing them, checked their complete SHA-256 and located the matching loaded native-module bytes. NumPy's recorded wheel digest independently matched versioned PyPI metadata; runtime acquisition verification is in the controller receipt. This is binary-identity verification, not a reproducible source-to-wheel build attestation.

| Identity | SHA-256 |
|---|---|
| Workflow | 33888279ffa5cbfe11637d53e336fae11300f29101f30d0f1dbbade586296a6d |
| Controller | e8a18e90bd0b4891d38ebbd33c6d7168caadde4b3745b7dd059d53490b77b650 |
| Worker | d37332235ba9048f01500dfb6340774bb05e163e6bdde2410e756545ce04a3b8 |
| Five-qubit fixture literal | 2babf1769a120bcdaa7bc4d8dca86b2de660f02a471d63aacf6c08ffeb5ef9cd |
| Kickmix 1.0.0 cp312 wheel | cc26abcd5efa5e72f373148d5cca2ffa43e158a724e94c213b97622f23c6241a |
| NumPy 2.1.3 cp312 wheel | 2312b2aa89e1f43ecea6da6ea9a810d06aae08321609d8dc0d0eda6d946a541b |
| Engine 0.6.0 abi3 wheel | 76f02ccec00ab9782d6aaca0b9d179d2174dfea80db1fa625aa8369e0e11d178 |
| Loaded official native module | d965e0ad42e7e3a147d4b28d6971a517f772dd79795cfc364be2fe9ffe3a7b80 |
| Loaded engine native module | 74e205f8120bbfdbf5b759b42c1f344c842ed8c543da127adecf4dad1cd7db5c |

Python 3.12.13. Image content ID: `sha256:3eb66c6a8a2399cdf305afe7f680ea1e3aad64e9a6684cd6e46baf6b8b701ec8`.
Registry digest: `python@sha256:3cd9086bdb30f7c9bc08a3fa621d9842e0d3f6f9291aeb4677e0547817c10b12`.
Full wheel filenames, other source pins and binary matching paths: receipt.json and BINARY_IDENTITY_AUDIT.json.

## Scientific result

Five same-seed comparisons × 256 shots × two backends = 2,560 shots. Additional engine-only wrong-seed run = 256. **Total 2,816 = 1,280 official + 1,536 engine shots.** This is not 2,816 valid-circuit shots.

Base seeds 7 and 11 passed analytic input-preservation, expected phase and clean-scratch checks. Every compared quantum/classical output, exact 128-bit phase, rounded phase, final HMR outcome, conditional opcode count, charged Toffoli count, rotation hierarchy and reaction depth agreed. Classical registers were compared through the engine's original-bit map. Reaction depth 4; executed CCX totals 380/374 for seeds 7/11.

Defective same-seed circuits also agreed across simulators but correctly failed the analytic oracle:

| Negative control | Detection |
|---|---|
| Missing phase correction | 29 wrong-phase shots, classical output correct |
| Dirty reset | 73 wrong-phase shots, final scratch zero |
| Wrong output | 256 wrong output bits/shots |
| Wrong seed 11→12 | 360 differing classical bits, three differing opcode-count entries, differing Toffoli scalar |

Thus backend agreement alone is not treated as a correctness oracle, nor clean scratch as proof of quantum correctness. Full per-shot arrays were not persisted; this read-only audit verifies the pinned comparison implementation and recorded assertions rather than independently rerunning outcomes. A fixed-seed pilot does not prove all circuits, arbitrary dirty inputs or all measurement histories.

Base KMB SHA-256: `5114223ee16a45ff420478eb0029f2abcc3c43274a60e176e57c9e28e5d42ead`.

## Containment and cleanup

Actual cgroup memory.max=536870912, memory.swap.max=0, cpu.max=100000/100000, pids.max=16. Docker additionally used memory512m/memory+swap512m, one CPU, network none, read-only root, nonroot UID, dropped capabilities, no-new-privileges and read-only toy/dependency mounts. Scratch: /tmp15MiB + /dev/shm1MiB. Fork was denied before third-party imports.

| Control | Evidence |
|---|---|
| 768MiB allocation | OOMKilled=true, exit137; oom_kill 0→1; peak exactly512MiB |
| Task cap | 15 helper threads plus main; further creation rejected; pids.events max0→1; exit0 |
| Scratch cap | Oversized write returned ENOSPC; exit0 |
| Kernel CPU control | Exit137 without OOM; 1.003391 CPU seconds |
| Wall control | Expected stop; exit137; 0.732436s launch-through-receipt for0.6s trigger |
| Cleanup | Every child reaped, pids.current0 after each case, final cgroup empty and removed |

All five controls ran before simulator download/import. Pilot kernel CPU hard limit20s applies to one thread group; fork cannot multiply it. Pre-pilot contained CPU1.977185s; aggregate watchdog25s, measured ceiling30s. One-CPU quota is a rate cap, not the aggregate time limit. Controller deadline50s, outer timeout58s, measured completion/cleanup ceiling60s.

| Resource | Actual |
|---|---|
| All contained controls + pilot CPU | 2.591784s |
| Pilot container CPU delta | 0.614599s |
| Pilot worker self CPU | 0.586825s |
| Worker reported peak RSS | 46,321,664B =44.1758MiB |
| Pilot container memory.peak | 26,755,072B =25.5156MiB |
| Pilot worker wall interval | 0.434463s |
| Pilot container launch-through-receipt | 0.783396s |
| Controller provisioning-through-cleanup | 37.901430s |

RSS includes resident shared mappings; cgroup page charging differs, so these metrics need not agree. The common parent's512MiB peak is the deliberate OOM control, not simulator demand. Host registry/download orchestration is outside simulator cgroup accounting; measurements are not whole-runner CPU/memory bounds. Complete Actions setup/teardown is distinct from controller time.

Paired API timings: official6.955216ms, engine1.135580ms. Tiny single-run timings are not a full-task speedup claim. No separate-backend memory benchmark was performed.

## Decision and next step

GO for limited research-tool evaluation, not general adoption or full PhaseForge qualification. Propose ONE separately authorized public synthetic GF(2^12) multiply–accumulate comparison: source reviewed, dirty outputs, inverse cleanup, explicit phase checks, one fixed seed,256shots/backend, same containment, no private decoder/task inputs. Stop on any mismatch. This next experiment was not executed.

No rerun, scoring submission, accepted-artifact change or full task verification occurred. Original verifiers remain authoritative. This pilot does not change any scientific qualification or scoring hold.
