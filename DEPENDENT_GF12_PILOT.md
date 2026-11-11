# Dependent GF12 arithmetic pilot

**NEEDS_EVIDENCE: prepared source only; native experiment has not run.**

This separate manual workflow tests the genuine changed-operand sequence over
GF(2^12), polynomial 0x1053 (x^12+x^6+x^4+x+1):

1. Z ^= A*B
2. A ^= Z*C, using the updated Z
3. A ^= Z*C
4. Z ^= A*B, using the restored A

Steps 3/4 are the exact reverse of 1/2. Every multiplication uses a new public
schoolbook generator, not private decoder source. The independent reference
forms a carryless integer product and reduces it by polynomial long division;
the emitter instead forms monomial residues by successive shift/reduce.
All 144 basis products are checked. Source provenance for the official field
convention is retained in GF12_PARITY_PILOT.md at the preceding pilot revision.

## Correctness and complete phase argument

Each field MAC has the form (x,y,t)->(x,y,t XOR x*y), so it is an involution
for arbitrary initial t, including dirty or entangled targets. Operands and
target are disjoint within a MAC. The second step reads changed Z; reversing
it restores A before the last step reads A again. Thus VU is reversed by UV.

For each monomial, CCX computes the control product into clean private scratch,
CX fanout changes only the dirty target, HMR resets scratch with outcome m,
and the conditioned CZ cancels its (-1)^(m*x_i*y_j) phase. The cancellation
holds pointwise for every input and every measurement history, independently
of target contents. Operands may change *between* MACs without invalidating
that per-term identity. Every valid MAC returns private scratch to zero.
This also proves the required coherent relative-phase behavior, not merely
classical output equality. All-zero/all-one transcript checks are additional
finite edge checks; the algebraic argument supplies the all-history claim.

## Exactly one fixed-seed native batch

One composite circuit, seed 7, 256 shots per backend / 512 total. Every shot
contains the four-step primary sequence. The fixture has 200 enabled and 56
disabled rows, 144 operand-basis pairs, extra dense data and dirty targets.
The circuit is 85 qubits: the 49-qubit arithmetic core, a 12-bit read-only
original-Z reference used only by the dependency negative, and two 12-bit
public intermediate probes. Probes are outputs, not private scratch.

Five disjoint data modes are selected by explicit classical input flags:

| Mode | Behavior and required detection |
|---|---|
| 0 | Valid sequence: restore A/B/C/Z and clean private scratch |
| 1 | Wrong product: flip low Z bit after first MAC; restoration must fail |
| 2 | Wrong dependency: second step reads original Z; output must disagree |
| 3 | Missing phase repair: omit first term's CZ; recorded phase must expose it |
| 4 | Incomplete cleanup: leave a final borrowed AND; scratch must be detected |

All modes are simulated together, not extra native runs. Faults are intentional
and must match independently computed fault equations, including their complete
phase. The unchanged correct mode must satisfy the actual interface. An
unexpected arithmetic, phase, count, parity or cleanup mismatch is terminal.
A missing negative detection is also terminal: no second seed or retry.

All 720 HMR instruction outcomes use distinct classical bits; all 727 classical
bits, all quantum outputs and exact binary phases are dumped and hashed.
A separate Boolean gate/transcript interpreter checks every operation's value,
phase and executed count; closed-form finite-field equations separately check
the two recorded forward stages and final inverse/fault outcomes. Native
official Kickmix and engine must agree on every bit, phase, opcode/charged
count and reaction depth. Gates are real X/CX/CCX/CZ/HMR and classical condition
stack operations, so a full phase bit is exact; no fractional-phase tolerance.

Source-only predictions, **not achieved native costs**: 721 static CCX,
115,240 executed CCX and 115,200 executed HMR per backend. This is a tooling
fixture, not a competitive multiplier or a scoring candidate.

## Guard, identities and evidence

Both successful workflows, their manifests and archives remain unchanged.
The new controller differs from the proven GF12 controller only in isolated
paths and workflow identity. The worker retains the same resource bootstrap
and comparison API, with new input layout/dimensions and the new fixture.

The same pinned Python 3.12.13 image and exact official Kickmix 1.0.0,
NumPy 2.1.3 and kickmix-engine 0.6.0 wheel hashes are retained. Engine source
is b455a8a6120b515219b49cd469f83a230cf4989f; engine wheel SHA-256 is
76f02ccec00ab9782d6aaca0b9d179d2174dfea80db1fa625aa8369e0e11d178.
Complete source identities are in DEPENDENT_GF12_SHA256SUMS.json, and exact
image/wheel/module/circuit identities enter the execution receipt.

Fresh memory-OOM, task, scratch-ENOSPC, kernel-CPU and wall-termination controls
must pass before simulator import. Same resource boundary: 512 MiB hard memory,
zero additional swap, one CPU, 16 tasks, 16 MiB writable tmpfs, kernel worker
CPU hard limit 20 s with fork denied, aggregate CPU early stop 25 s / measured
ceiling 30 s; controller deadline 50 s, outer timeout 58 s, measured completion
and cleanup below 60 s. Network-disabled, nonroot, read-only containers with
no capabilities or host socket. Host image/download orchestration remains
outside simulator cgroup CPU/memory accounting, as in the demonstrated guard.

Only workflow_dispatch, standard ubuntu-24.04, contents:read, pinned actions,
no secrets/persisted credentials, first run/attempt only. Receipt directory
evidence-dependent; artifact dependent-gf12-pilot-receipts. No science or
resource control is automatically retried. The owner dispatches main once.
No private project file or accepted circuit is checked out or uploaded.

## Exit from synthetic testing

If the single run and independent raw-transcript audit pass, close this synthetic
admission series. Do not automatically propose or authorize another toy run.

The next operational gate is ONE real, independently source-reviewed arithmetic
rewrite delivered by research, with a stated complete width/charged-cost
advantage and dirty-target/cleanup/phase contract. Use the accelerated engine as
a research differential backend against unchanged official Kickmix on that
bounded kernel, caching only by exact circuit/runtime/source identities. Price
its complete DQI impact using actual call counts before requesting a large run.

Only already-public, cleared source may enter this public sandbox. A private
PhaseForge kernel requires an explicitly authorized private execution route;
it must never be uploaded here merely to use the free runner. If no qualified
real source candidate exists, continue scientific source work and stop CI toys.
Candidate selection/execution needs separate ADMIN authority; this pilot does
not grant it. Original full verifiers remain authoritative for qualification.

No full decoder, original full verifier, submission, paid service, accepted
artifact change or scoring-HOLD change is part of this experiment.
