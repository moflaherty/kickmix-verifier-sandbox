# Public Kickmix verifier sandbox

One manual, synthetic-only comparison of official Kickmix1.0.0 and kickmix-engine0.6.0. This repository contains **no competition circuits, private scientific inputs, credentials or production checkout**.

Status: **PREPARED, NOT EXECUTED.** No scientific PASS, performance gain or container-enforcement result is claimed before a completed run.

The workflow has only `workflow_dispatch`; there are no push, pull-request, timer or reusable-workflow triggers. It uses a standard public Ubuntu runner, read-only contents permission, no persisted checkout credentials, no secrets and no larger runner. It admits only the first workflow run and first attempt. Do not click Re-run or create a second dispatch after a failure.

## What one run does

- Resolves and records the official Python3.12.13 Docker image's immutable digest before container execution.
- Creates a disposable cgroup-v2/systemd **resource slice**, not a background service or scheduled task:512MiB memory, zero additional swap, oneCPU,16tasks.
- Uses network-disabled, nonroot, read-only containers with all capabilities dropped and no host socket. Writable `/tmp`15MiB plus `/dev/shm`1MiB is16MiB total.
- Stacks a seccomp rule onto Docker's default profile: fork/vfork and process clones are denied; native threads are permitted. The production worker is one thread group with kernel20CPU-second hard RLIMIT_CPU. Aggregate cgroup usage is monitored with a25CPU-second early stop, leaving reserve below30; phase1 control CPU is charged too. Wall admission50s leaves cleanup reserve below60s. The outer timeout is58s. Any measured overrun fails; no limit is automatically relaxed.
- Demonstrates OOM enforcement, process/thread ceiling, kernelCPU stop, wall kill and child cleanup **before downloading or importing either simulator**.
- Fetches official Kickmix1.0.0/NumPy2.1.3 release metadata from PyPI and verifies selected LinuxCPython3.12 wheels by their published SHA256. Downloads engine0.6.0 at fixed published SHA256`76f02ccec00ab9782d6aaca0b9d179d2174dfea80db1fa625aa8369e0e11d178`, sourcecommit`b455a8a6120b515219b49cd469f83a230cf4989f`. Wheels are safely extracted without installers or setup scripts; dependencies are mounted read-only.
- Runs the five-qubit toy at fixed seeds7/11 and compares every quantum/classical bit, exact128-bit and rounded64-bit phase, charged/all opcode counts, rotation hierarchy counts and reactiondepth. Checks missing phase fixup, data-dependent dirtyR, wrong output and deliberately wrong seed. At most2816backendshots, no task verifier.

The toy's input x spans0..3. Its correct phase is1/16turn only forx3, all input qubits are preserved and private scratch is clean. Wrong seed is detected using classical outcomes/counts even if a corrected quantum output remains identical. This is sampled simulator parity, **not proof of arbitrary-input equivalence for all circuits**.

## Receipts and failure behavior

`parity-pilot-receipts` includes source/image/wheel pins, actual cgroup limits and counters, per-control exits/OOM flags, cleanup, per-case exact mismatches and execution times/peakRSS. The parent's memory.peak includes the deliberate OOM test; pilot processRSS is separately reported. Runner/registry provisioning is not simulator execution; total controller wall time is still bounded by its deadline. No performance claim may use admission/control measurements as simulator speed.

The run fails closed on unavailable cgroups/systemd controls, provenance/dependency mismatch, exceeded wall/CPU/memory/PID boundaries, missed negative control, leftover processes or semantic mismatch. No science stage is retried after failure. If the run fails, retain the receipt and review it before any new authorization. A passing toy only justifies considering a separately bounded research comparison; original task verifiers remain authoritative.

API comparison details were informed by the public Apache2.0 kickmix-engine parity examples; upstream license/attribution is retained. The code is intentionally independent of any private project paths or data.
