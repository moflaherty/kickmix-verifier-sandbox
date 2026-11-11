# DEPENDENT_GF12_V2_FINAL_AUDIT — PASS / synthetic series CLOSED

## Immutable run and artifact

[Run42946165082](https://github.com/moflaherty/kickmix-verifier-sandbox/actions/runs/42946165082), workflow_dispatch, run1/attempt1, source `ba3e859f457993faad783490486537c629dafec6`, job130279388937, completed/success. November10,2026,9:27:37–9:28:12p.m. EST (November11,02:27:37–02:28:12UTC).

Actual logs and artifact13822817686, dependent-gf12-v2-receipts, were read. The first temporary transfer link had expired (HTTP403); a renewed authenticated file transfer succeeded. This was an artifact transfer only, not a workflow/science retry.

The **exact original ZIP** is archived here as artifact.zip: **97,359bytes**, SHA-256 `5f606464c3ccc85e40c1068fde58575a6d284510b6cb63c421580242a0619eb3`; its binary Git blob SHA-1 is `d4cf6c26ccb74b84e27acce8a0cbb8d0a4fca291`, independently computed from those same downloaded bytes. The ZIP has one receipt.json: **213,836bytes**, SHA-256 `9f645f48397b8fe3c50e07c853de9e190862df62f5aa7fc9cecef0fc5ab3670d`. Its exact bytes match the logged receipt's serialization. Both are preserved before the original artifact's November17,9:28p.m.EST expiry.

## Independent scientific replay

**256shots per backend /512total, fixed seed7.** Every row includes the dependent four-step sequence; selected disjoint modes contain intentional faults. This is not512unfaulted trials.

The independent audit never imported a native compiler/simulator and did not call the fixture's validate/replay helpers. It used the pinned emitter only to obtain exact source text, independently rebuilt deterministic inputs, independently convolved/reduced field polynomials modulo0x1053, decoded all raw states, and used its own gate/measurement replay plus closed-form stage equations.

All144monomial products matched. All43,520quantum output bits and372,224original-interface classical bits across the two backends matched the expected valid/faulted behavior. At all four recorded stages the changed-operand field equations and actual HMR-dependent phase were reproduced. Valid rows restore A/B/C/Z and private scratch; disabled rows preserve inputs and leave probes zero. Probe words are public outputs, not private scratch.

Every valid monomial AND/fanout/HMR/conditioned-CZ cancels (-1)^(mab) pointwise with clean private scratch. Dirty targets do not enter that correction. Reversing the dependent MACs restores A before it is used to undo Z. Thus the source's valid operator has exact coherent relative-phase/inverse semantics for every history; the finite native test corroborates this implementation on the recorded histories, not all conceivable simulator behavior.

### Classical-map closure

Observed native metadata now exactly matches the source prediction:
-727original indices,726compact slots; onlyb3omitted, inverse[3]=-1.
-Original input IDs[0,1,2,4,5,6] map to compact[0,146,292,725,147,2].
-All720HMR output indicesb7..b726 present, unique and decoded;115,200executed HMR events/backend.
-b3's51nonzero initial rows preserved. Official output directly records it; the engine adapter carries it by the source-proven untouched-bit identity. It is **not falsely described as an observed compact engine slot**. The raw schema identifies the omitted original bit; this marker denotes the program's omission even on the directly read official record.
-Native map SHA-256 `9fb4ee2972e5f48b5a5a8e5198ec441a8a7445280f10b171bf6e36ac83fccac9`.
-Native compact classical-dump SHA-256 `fefd8463155640f4ee816032dc91bb3fa8381ed49089dc123ee39a3c1ffb137c`, independently reproduced by re-packing observed mapped outputs.
-Each expanded26,016-byte output/transcript record SHA-256 `750f68339dfa9f8cd01f0fb20ef477e7e4befc6e736686fe7f12534374114d88`. Original and expanded engine records are byte-identical, including the explicitly carried bit.

All native phase, classical-history, output, opcode-count and reaction-depth mismatch counters were zero. Exact phase is binary for this real-gate fixture; no approximate fractional tolerance is used.

### Four intentional scientific defects

| Fault | Actual independently reproduced detection |
|---|---:|
| Wrong product |40wrong final words |
| Wrong updated-operand dependency |40wrong restorations |
| Missing phase repair |5wrong-phase shots |
| Incomplete cleanup |12dirty-scratch shots |

The full phase vector contains exactly5negatives, matching the omitted-repair equation. Every other phase was predicted, including faulted arithmetic branches. All52mode-zero rows are unfaulted checks (40enabled/12disabled); the full set has200enabled/56disabled rows, with40enabled rows in each of five modes.

### Exact cost ledger per backend

| Operation | Executed count |
|---|---:|
| CCX |115,240 |
| CX |295,200 |
| HMR |115,200 |
| CZ |57,996 |
| X |40 |
| PUSH_CONDITION |1,024 |
| POP_CONDITION |1,024 |

CCX=576*200enabled four-MAC sequences+40intentional cleanup CCX. Width85Q/727original classical bits;721static CCX. Both native APIs report **reaction depth3**, with equality asserted in the pinned worker. This audit verified that native-source assertion and receipt, not a fresh native depth calculation. No rotations, ordinary T, CCZ or CSWAP occur. These composite fixture counts are not a competitive decoder cost.

KMX SHA-256 `bb9dd1c546c28f5fb7785046ff3187ebf1a6641759daf16e7b782c4eeb258e23`.
KMB SHA-256 `c8c5c5ad577c962a59c3c5f55a82ab5f3121ce590aa5e2dbd3b369633da0f423`.

## Source/executable integrity

All11source hashes recomputed from the executed revision match. Wheel digests and loaded native-module bytes were independently checked again by downloading public wheels as data only, hashing them and inspecting their ZIP entries. No wheel was installed or executed during audit.

| Identity | SHA-256 |
|---|---|
| Worker |84f37ebfbd4533f955608564e2b680ffe44f69d21e209c56ec42010079b3b43b |
| Guard |d5c37d0a22f0765a45c57620b8a42f620ea047a1afbf456d36a54729cc46bcf7 |
| Mapping helper |4bed719a769ef591df127663b20bf102942408b539b6048cfebe7fb55f4b89a6 |
| Kickmix1.0.0 wheel |cc26abcd5efa5e72f373148d5cca2ffa43e158a724e94c213b97622f23c6241a |
| NumPy2.1.3 wheel |2312b2aa89e1f43ecea6da6ea9a810d06aae08321609d8dc0d0eda6d946a541b |
| Engine0.6.0 wheel |76f02ccec00ab9782d6aaca0b9d179d2174dfea80db1fa625aa8369e0e11d178 |
| Loaded official module |d965e0ad42e7e3a147d4b28d6971a517f772dd79795cfc364be2fe9ffe3a7b80 |
| Loaded engine module |74e205f8120bbfdbf5b759b42c1f344c842ed8c543da127adecf4dad1cd7db5c |

NumPy's published wheel metadata matched; runtime controller verified its bytes. Engine source `b455a8a6120b515219b49cd469f83a230cf4989f`. Python3.12.13; immutable image `python@sha256:3cd9086bdb30f7c9bc08a3fa621d9842e0d3f6f9291aeb4677e0547817c10b12`, content ID `sha256:3eb66c6a8a2399cdf305afe7f680ea1e3aad64e9a6684cd6e46baf6b8b701ec8`. All remaining source pins, native mapping arrays and loaded binary identities are in receipt.json/audit_input.json. No reproducible source-to-wheel build is claimed.

## Resource containment and cleanup

Actual cgroup: memory.max536870912bytes, memory.swap.max0, cpu.max100000/100000, pids.max16. Matching Docker memory+swap512MiB, oneCPU,16tasks, writable tmpfs16MiB, networknone, read-only root/code/dependencies, nonroot, dropped capabilities, no-new-privileges and fork denial.

Before simulator import: OOM negative killed at512MiB, exactly one OOM-kill event; PID negative hit15helper threads+main and incremented limit events; scratch overflow ENOSPC; CPU negative kernel-killed without OOM; wall negative killed as intended. All six container children reaped, pids.current0 after every case, final slice empty and removed.

| Resource | Actual |
|---|---:|
| All contained controls+pilot CPU |2.339718s |
| Pilot contained CPU |0.575056s |
| Worker CPU |0.551720s |
| Worker peak RSS |45,342,720B /43.2421875MiB |
| Pilot cgroup peak |25,427,968B /24.25MiB |
| Worker wall |0.434600s |
| Controller provisioning/cleanup wall |23.444794s |

Guard limits remain512MiB/zero swap/oneCPU/30aggregate CPU seconds/60wall seconds/16tasks/16MiB scratch, including kernel worker cap and earlier stops. Parent512MiBpeak is the deliberate OOM test. RSS residency and cgroup page charging differ. Host provisioning is outside simulator-cgroup CPU/memory accounting; these are not whole-runner resource bounds or separate-backend memory measurements. Official/engine timing windows66.274038ms/13.348470ms include readout/oracle overhead and do not establish a full-decoder speedup.

## Final scope and exit

**PASS for this source-pinned dependent GF12 research fixture. SYNTHETIC PILOT SERIES CLOSED.** Previous successes, the v1failure/skip evidence and all workflow/source locks remain unchanged. No new toy or native job is authorized or prepared.

No full decoder, sampler/statistical confidence/repetition/scoring adapter or task verifier was exercised. Original verifiers remain authoritative; no competition score equivalence or improvement follows.

ONE concrete research handoff: source-only contract/cost/provenance intake of the actual public **42-CCX/36-core-qubit/zero-private-workspace GF12 mul_xor0** at:
[M4-on-Github/Quantum_Circuits ba83a1cac7a82dcde29c28575b3c9838a109ba15, field.py:486](https://github.com/M4-on-Github/Quantum_Circuits/blob/ba83a1cac7a82dcde29c28575b3c9838a109ba15/src/dqi/pro_q2_897/exp/arithmetic/field.py#L486).
Its42terms follow seven interpolation points times six GF8 base terms; each emits one CCX, surrounded by CX conjugations with no allocation. This is a **real competitive reference kernel, not a newly improving implementation**. It already matches the retained42Tbaseline. The source-complete54CCXalternative is a known loss and must not be promoted.

Before any real-kernel run, an independent source reviewer must bind tensor/builder/field dependencies, complete CX/width/control/inverse/phase behavior and applicable reuse terms. The module's circ alias is official Kickmix, as the same revision's generate.py:44–45 documents. The subdirectory has an Apache2.0 grant and attribution; its NOTICE also discloses an unlicensed earlier design-lineage caveat, so no blanket eligibility/reuse clearance is asserted. No third-party code was imported into this sandbox by this audit.

This is the next source-review step, **not another synthetic experiment or automatic native authorization**. Improving candidates must beat that fully charged baseline or show a genuine schedule/width benefit before requesting scarce full-verifier resources. No new lower-cost source-complete derivative was established by the available research evidence. Private PhaseForge kernels/arrays must not be uploaded here; any private execution route needs explicit authorization.

Protected portfolio and scoring holds are unchanged.
