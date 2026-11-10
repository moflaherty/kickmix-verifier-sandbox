# Fast-verifier CI pilot

Decision: NEEDS_EVIDENCE. Prepared source is not an execution receipt.

Environment: public repository moflaherty/kickmix-verifier-sandbox, standard
GitHub-hosted ubuntu-24.04, manual workflow_dispatch only, contents:read.
No private repository checkout, private input, secret, competition artifact,
production environment, paid runner or simulator installation on the Mac.

Engine source: manwithacat/kickmix-engine v0.6.0 at
b455a8a6120b515219b49cd469f83a230cf4989f.
Linux CPython wheel SHA-256:
76f02ccec00ab9782d6aaca0b9d179d2174dfea80db1fa625aa8369e0e11d178.
Official simulator: unchanged Kickmix 1.0.0; NumPy 2.1.3; Python 3.12.13.
PyPI wheel names/digests and the Docker content digest are resolved, checked
and written into the receipt before third-party import. Failure is terminal.

The complete contained experiment shares a 512 MiB/zero-swap resource slice,
one CPU, 16-task ceiling and 16 MiB writable tmpfs. Kernel CPU limits apply
to one thread group (fork is prohibited); aggregate CPU monitoring stops at
25 seconds, with a 30-second measured ceiling. The controller uses a 50-second
deadline and an outer 58-second timeout with cleanup reserve under 60 seconds.
Public image/wheel provisioning occurs outside the simulator container;
container/cgroup metrics do not measure the entire GitHub runner's resources.

Before simulator import, synthetic controls must demonstrate OOM termination,
task exhaustion, scratch ENOSPC, CPU termination, wall termination and full
cleanup. Each gate fails closed. No measured enforcement claim is made yet.

The five-qubit fixture compares quantum/classical outputs, HMR histories,
exact phase, rotation counts, conditional gate counts, Toffoli counts and
reaction depth at fixed seeds 7 and 11. Negative controls remove a phase
correction, reset a dirty target, flip an output and use the wrong seed.
The experiment has a maximum 2,816 backend shots and executes no task verifier.

Results belong in evidence/receipt.json and the Actions receipt artifact.
Report actual simulator RSS separately from the deliberate OOM control peak.
A PASS would support only further bounded research comparisons. It would not
qualify a competition circuit or replace the unchanged official verifier.

Dispatch route: the available GitHub connector has no workflow_dispatch write
operation. No dispatch is claimed merely because this workflow is committed.
If the local authenticated CLI cannot connect, the repository owner must
select Actions / Kickmix parity pilot / Run workflow once, using main.
Do not rerun a failed or completed pilot without fresh authorization.
