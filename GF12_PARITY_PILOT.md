# GF12_PARITY_PILOT

Status: **NEEDS_EVIDENCE — source prepared; no native GF12 pilot executed.**

This is a new manually dispatched workflow in the public sandbox. The first successful workflow, source manifest and archived evidence remain byte-for-byte unchanged. No private project file, circuit, scientific array or credential is an input.

## Field and independent reference

Modulus **4179 = 0x1053 = x^12+x^6+x^4+x+1**, coefficient bit k represents x^k, little-endian words.
Public primary definition and explicit degree-12 assertion:
- [Official Kickmix field test](https://github.com/quantumlib/Qualtran/blob/9a0c11a4ee7697c082fbf8f2e1e8bf4a71fcb453/kickmix/src/kickmix/util/gf2_field.test.cc)
- [Official field representation](https://github.com/quantumlib/Qualtran/blob/9a0c11a4ee7697c082fbf8f2e1e8bf4a71fcb453/kickmix/src/kickmix/util/gf2_field.h)
- [Official default-polynomial implementation](https://github.com/quantumlib/Qualtran/blob/9a0c11a4ee7697c082fbf8f2e1e8bf4a71fcb453/kickmix/src/kickmix/util/gf2_field.cc)

That upstream revision documents the public field convention; it is not asserted to be the source revision used to build the pinned 1.0.0 wheel. The actual simulator binary identity is fixed independently below.

The new emitter builds 23 monomial residues by shift/reduce. A separate classical reference forms a carryless product and performs high-to-low polynomial long division. Every one of the 144 basis products is compared. Because the emitted function is bilinear in A/B and affine XOR in Z, this compact source check establishes its value map for arbitrary 12-bit operands and arbitrary initial accumulation words. This is not an optimized multiplier or a score candidate.

Each term uses CCX(A_i,B_j,scratch), CNOT fanout into accumulator, HMR(scratch,m), then CZ(A_i,B_j) conditioned on m. Scratch begins/ends zero. The HMR factor (-1)^(m A_i B_j) is canceled by the conditional CZ for every history, independently of the dirty accumulator. This pointwise identity also covers coherent superpositions/entanglement of operands and targets with private scratch initially clean. Reversing the term order implements the logical inverse with fresh, repaired measurements.

## Exactly one batch per backend

One composite fixture, simulator seed **7**, exactly **256 shots per backend (512 total)**. No additional native negative-control runs or repeats.

Every shot tests a valid conditional MAC, saves the intermediate dirty-target result in 12 output probes, then executes the reverse-order MAC and checks restoration. Primary inputs are preserved and the sole private scratch qubit must be zero. Deterministic data cover all 144 monomial pairs, additional dense operands and nonzero initial targets, plus disabled classical controls.

Three disjoint shot groups also execute one deliberate faulty branch:
1. Wrong product: flip the low product bit.
2. Missing phase repair: omit exactly one HMR-conditioned CZ.
3. Dirty-target reset: HMR a declared accumulation bit, rather than private scratch.

The unaffected group checks zero phase. Faulted groups must display their prescribed value/phase defects, while their *complete* observed phase must equal the independently derived fault equation. Intentional defects are expected controls, not an unexpected mismatch to ignore. Unexpected backend, oracle or count mismatch fails immediately. If a fixed-seed control shows no defect, the experiment fails without another seed.

**Source expectations:** 85 qubits; 725 classical bits; 720 static CCX; 200 enabled/56 disabled primary shots; **77,184 executed CCX per backend**, including conditional work. These are not yet achieved native measurements. The 720 HMR term outcomes and one dirty-reset outcome are retained in distinct classical bits.

Both simulators receive identical quantum/classical inputs. Complete quantum outputs, all 725 mapped classical registers, exact binary phase, rounded phase units, all opcode/charged counts and reaction depth must match. All gates are real X/CX/CCX/CZ/HMR plus classical condition stack, so exact phase is 0 or 1 half-turn; comparing the full phase bit is exact here, not an approximation to 128-bit fractional phase.

A separate 256-way Boolean gate interpreter replays the actual measurement transcript and checks outputs, phase, skipped measurements and executed operation counts. An additional closed-form field oracle checks the MAC/inverse and predicted faults. Packed raw outputs/transcripts from both backends and their hashes are retained for read-only replay.

## Integrity and containment

Engine v0.6.0 source `b455a8a6120b515219b49cd469f83a230cf4989f`.
Engine Linux wheel SHA-256 `76f02ccec00ab9782d6aaca0b9d179d2174dfea80db1fa625aa8369e0e11d178`.
Official Kickmix 1.0.0 wheel `cc26abcd5efa5e72f373148d5cca2ffa43e158a724e94c213b97622f23c6241a`.
NumPy 2.1.3 wheel `2312b2aa89e1f43ecea6da6ea9a810d06aae08321609d8dc0d0eda6d946a541b`.
Python 3.12.13 image registry digest `python@sha256:3cd9086bdb30f7c9bc08a3fa621d9842e0d3f6f9291aeb4677e0547817c10b12`, Linux image ID `sha256:3eb66c6a8a2399cdf305afe7f680ea1e3aad64e9a6684cd6e46baf6b8b701ec8`.
All new source hashes: GF12_SHA256SUMS.json.

Controller is separately copied from the demonstrated first controller. Diff changes only isolated paths, workflow identity and stronger immutable dependency/image pins. Memory/CPU/wall/process/scratch/network/privilege/cleanup logic is unchanged. Worker bootstrap/resource controls are unchanged. Native worker is new and has not been executed.

The fresh CI run must repeat all five containment controls before simulator import: memory OOM, task ceiling, scratch ENOSPC, CPU termination and wall termination, with complete cleanup.

Same limits: cgroup-v2 **512 MiB memory, zero extra swap, one CPU, 16 tasks, 16 MiB writable tmpfs**; single thread group, fork denied, kernel20s worker CPU cap; aggregate25s early stop/30s measured ceiling; controller50s deadline, outer58s timeout, measured completion/cleanup below60s. Public orchestration is outside simulator cgroup CPU/memory accounting, as in the first audited run. Network-disabled nonroot read-only containers, no capabilities or host socket.

Only workflow_dispatch; standard ubuntu-24.04; contents:read; pinned checkout/upload actions; no secrets/persisted credentials; first run/attempt only. Separate evidence-gf12 directory and gf12-parity-pilot-receipts artifact. First workflow is neither edited nor dispatched.

## Operational gate

Source-only AST, bilinear-reference and symbolic-transcript checks may be run without simulators. They are not native PASS evidence. No installation or native simulator execution occurs on the Mac.

The owner should dispatch **GF12 field arithmetic parity (one manual run)** on main **once**, after reviewing the committed source. Do not rerun. If the connector/CLI cannot dispatch, use the public repository's Actions page; no automatic trigger is added.

After that run, audit the actual artifact/logs, measured resources, exact counts, raw parity and cleanup before changing this status to PASS. A synthetic field PASS would support bounded research use only, not full DQI qualification, repetition/statistical equivalence or official score equivalence. No task verifier, Kaggle action or change to any scientific hold is authorized.

