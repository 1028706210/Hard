# Task 41-RMT-PRE Remote Runner Viability Gate Implementation Plan

**Status:** `CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE`  
**Do not execute:** E2B Provider work、Remote Runner prototype、Firecracker、20 项 hostile-code matrix、cross-submission、host-secret、control-plane/runtime-socket 或 hostile path bypass。不得创建 E2B Account/API Key/Sandbox/Template。该计划仅保留供未来多人在线/不可信代码版本重新授权时参考。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove or block a remote, per-submission isolated .NET 10.0.100 execution path without implementing the production CSharpRunner or falling back to a local untrusted process.

**Architecture:** The Hard API prototype client submits an authenticated job to a trusted Remote Runner control plane. The control plane creates one immutable, network-denied sandbox per submission, injects source and private tests into an ephemeral workspace, returns only sanitized results, and destroys all per-run state.

**Tech Stack:** Hard API-compatible Python prototype client, authenticated TLS service channel, provider-specific isolated sandbox adapter, immutable .NET SDK 10.0.100 runtime/image, pytest security fixtures, structured JSON evidence.

**Spec:** `docs/superpowers/specs/2026-08-29-remote-runner-service-architecture.md`

## Global Constraints

- This is a PRE gate, not the production `CSharpRunner` implementation.
- Start from `6246473bf565be308c1505921ec1219beb30803c` in an isolated prototype worktree only after formal dispatch.
- Do not modify `apps/api/src/**`, `apps/web/src/**`, `content/**`, public OpenAPI, production data, backups, exports, or the protected shared worktree.
- Never run untrusted C# on the local Hard host, including as a fallback.
- Exact sandbox SDK is `.NET SDK 10.0.100`; floating SDK tags fail the gate.
- User-code sandbox network is `NONE`; only Hard API → trusted control plane is allowed.
- Do not create paid or long-lived resources, production credentials, or unauthenticated public endpoints without separate user authorization.
- A provider/resource/auth prerequisite that cannot be satisfied inside the authorization boundary produces `BLOCKED`, not a weakened prototype.

---

## Planned prototype file map

- Create `tools/remote_runner_prototype/README.md`: runbook, authorization boundary, setup/teardown and evidence index.
- Create `tools/remote_runner_prototype/protocol.py`: internal job/result data contracts and validation; not a public API.
- Create `tools/remote_runner_prototype/client.py`: authenticated prototype client with explicit remote-only behavior.
- Create `tools/remote_runner_prototype/service.py`: trusted control-plane orchestration boundary.
- Create `tools/remote_runner_prototype/sandbox.py`: provider adapter interface and selected ephemeral sandbox implementation.
- Create `tools/remote_runner_prototype/sanitize.py`: result allowlist and host-path/secret redaction.
- Create `tools/remote_runner_prototype/tests/`: protocol, security, isolation, cleanup, concurrency and fail-closed tests.
- Create `tools/remote_runner_prototype/fixtures/`: Hello World, bypass probes, secret sentinels, hidden tests and output/timeout probes.
- Create `tools/remote_runner_prototype/evidence/`: non-secret JSON results, timing/cost table and final verdict. Do not store credentials, provider tokens or hidden-test bodies.

## Internal prototype interfaces

```python
@dataclass(frozen=True)
class RemoteJobRequest:
    job_id: str
    source_utf8: str
    stdin_utf8: str
    hidden_tests_ciphertext: bytes
    timeout_ms: int
    output_limit_bytes: int
    sdk_version: Literal["10.0.100"]

@dataclass(frozen=True)
class SanitizedRemoteResult:
    job_id: str
    status: Literal["passed", "tests_failed", "compile_error", "runtime_error", "timeout", "output_limit", "infrastructure_error"]
    stdout_safe: str
    stderr_safe: str
    diagnostics: tuple[str, ...]
    tests_passed: int
    tests_failed: int

class SandboxProvider(Protocol):
    def create(self, *, job_id: str) -> SandboxHandle: ...
    def execute(self, handle: SandboxHandle, request: RemoteJobRequest) -> RawSandboxResult: ...
    def destroy(self, handle: SandboxHandle) -> CleanupEvidence: ...
```

`client.py` must have no local runner implementation and no branch that starts `dotnet`, `cmd`, PowerShell or another user-code process on the Hard host.

### Task 1: Authorization and provider viability preflight

**Files:**
- Create: `tools/remote_runner_prototype/README.md`
- Create: `tools/remote_runner_prototype/evidence/provider-preflight.json`

**Interfaces:**
- Consumes: the authorization boundary in the architecture spec.
- Produces: a non-secret provider/resource decision that either permits a disposable prototype or stops with `BLOCKED`.

- [ ] Record provider/runtime candidate, region/location, isolation primitive, authentication method, endpoint exposure, retention, teardown method and whether an existing authorized account/token is required.
- [ ] Record all expected charges. If any persistent charge, purchase, long-lived server, production credential or unauthenticated public endpoint is required, stop before resource creation and return `BLOCKED: USER_AUTHORIZATION_REQUIRED`.
- [ ] Confirm the candidate can enforce per-submission filesystem and network isolation at the provider/hypervisor/runtime layer, not by scanning C# source.
- [ ] Confirm the candidate can expose an authenticated TLS control-plane endpoint without exposing sandbox networking.
- [ ] Save the non-secret decision in `provider-preflight.json`; never store tokens or hidden tests.
- [ ] Commit only after formal dispatch with message `docs(remote-runner): record prototype provider preflight`.

### Task 2: Lock the internal protocol and fail-closed client

**Files:**
- Create: `tools/remote_runner_prototype/protocol.py`
- Create: `tools/remote_runner_prototype/client.py`
- Create: `tools/remote_runner_prototype/tests/test_protocol.py`
- Create: `tools/remote_runner_prototype/tests/test_no_local_fallback.py`

**Interfaces:**
- Consumes: `RemoteJobRequest` and `SanitizedRemoteResult` defined above.
- Produces: validated remote-only request/result serialization and an authenticated client transport interface.

- [ ] Write tests rejecting missing/invalid job IDs, SDK versions other than `10.0.100`, negative limits, oversized fields and unknown result statuses.
- [ ] Write a test that makes the remote service unavailable and asserts `infrastructure_error` without invoking `subprocess`, `dotnet` or any local execution adapter.
- [ ] Implement the dataclasses and strict JSON serialization with an explicit field allowlist.
- [ ] Implement a remote-only client that requires an HTTPS endpoint and injected service credential, rejects unauthenticated/plaintext endpoints, sets bounded connect/read deadlines and returns `infrastructure_error` on service failure.
- [ ] Run `pytest tools/remote_runner_prototype/tests/test_protocol.py tools/remote_runner_prototype/tests/test_no_local_fallback.py -q`; require all tests PASS.
- [ ] Commit only after formal dispatch with message `test(remote-runner): lock authenticated fail-closed protocol`.

### Task 3: Build the disposable control plane and sandbox adapter

**Files:**
- Create: `tools/remote_runner_prototype/service.py`
- Create: `tools/remote_runner_prototype/sandbox.py`
- Create: `tools/remote_runner_prototype/sanitize.py`
- Create: `tools/remote_runner_prototype/tests/test_lifecycle.py`
- Create: `tools/remote_runner_prototype/tests/test_sanitization.py`

**Interfaces:**
- Consumes: validated `RemoteJobRequest` and selected provider from Task 1.
- Produces: one sandbox per job, immutable SDK identity evidence, cleanup evidence and `SanitizedRemoteResult`.

- [ ] Write lifecycle tests requiring a new sandbox/workspace/TEMP identity for every job and unconditional `destroy()` in success, compile failure, runtime failure, timeout, output-limit and infrastructure-error paths.
- [ ] Write sanitization tests containing hidden-test markers, remote host paths, service endpoints, tokens and provider metadata; require all markers absent from the public result.
- [ ] Implement the provider adapter so only per-run workspace/TEMP are writable, runtime/image is immutable, no shared writable cache exists and runtime control sockets are not mounted.
- [ ] Verify and record immutable image/runtime hash plus in-sandbox `dotnet --version == 10.0.100`; reject floating tags or mismatches before code execution.
- [ ] Implement private hidden-test injection through the trusted control plane and deletion during unconditional teardown.
- [ ] Run lifecycle and sanitization tests; require all tests PASS and evidence for every teardown path.
- [ ] Commit only after formal dispatch with message `feat(remote-runner): prototype isolated sandbox lifecycle`.

### Task 4: Execute the 20-item security and viability matrix

**Files:**
- Create: `tools/remote_runner_prototype/tests/test_security_matrix.py`
- Create: `tools/remote_runner_prototype/tests/test_cross_submission.py`
- Create: `tools/remote_runner_prototype/tests/test_network_denied.py`
- Create: `tools/remote_runner_prototype/fixtures/`
- Create: `tools/remote_runner_prototype/evidence/security-matrix.json`

**Interfaces:**
- Consumes: the real remote sandbox adapter, not a mock sandbox.
- Produces: raw per-case PASS/BLOCKED evidence for all 20 required checks and the adapted Task 41-PRE bypass matrix.

- [ ] Add Hello World, `--no-restore`, workspace R/W, host sentinel, A→B isolation, Internet/LAN/Hard/control-plane/metadata/socket probes, timeout, output flood, child-process, hidden-marker and diagnostic-path fixtures.
- [ ] Add adapted absolute-path, `..`, `Path.GetFullPath`, encoded path, `System.IO`, Reflection, Delegate and Dynamic probes against remote host sentinels and unauthorized mounts.
- [ ] Run each probe inside a real per-submission sandbox and record expected versus actual result, sandbox ID, workspace ID, immutable image hash and cleanup ID without storing secrets.
- [ ] Run two submissions concurrently; require distinct sandbox/workspace/TEMP identities, correct individual results and no cross-read.
- [ ] Mark the entire gate `BLOCKED` immediately on any secret read, cross-submission read, network/control-plane/socket access, hidden-test leak, cleanup failure or local fallback.
- [ ] Save the complete result as `security-matrix.json` and commit only after formal dispatch with message `test(remote-runner): verify isolation security matrix`.

### Task 5: Measure reliability, latency and resource cost

**Files:**
- Create: `tools/remote_runner_prototype/tests/test_reliability.py`
- Create: `tools/remote_runner_prototype/evidence/performance-and-cost.json`

**Interfaces:**
- Consumes: successful and failed remote jobs plus provider usage metrics.
- Produces: sandbox creation, build/run, total latency, cleanup, concurrency and approximate per-run cost evidence.

- [ ] Measure sandbox creation, build/run, total latency and cleanup separately for Hello World and one failing job.
- [ ] Measure the same timings with at least two concurrent jobs.
- [ ] Record CPU, memory, storage/network allocation and the provider pricing assumptions used for an approximate per-run cost; do not create paid persistent resources to improve the measurement.
- [ ] Stop the service or invalidate the endpoint and prove the client returns `infrastructure_error` without local fallback.
- [ ] Destroy all disposable resources and record teardown verification.
- [ ] Commit only after formal dispatch with message `test(remote-runner): record viability and cost evidence`.

### Task 6: Produce the gate report and stop

**Files:**
- Create: `tools/remote_runner_prototype/evidence/final-report.md`
- Modify: `tools/remote_runner_prototype/README.md`

**Interfaces:**
- Consumes: provider preflight, lifecycle, security matrix, performance/cost and cleanup evidence.
- Produces: one final `PASS` or `BLOCKED` verdict; it does not unlock Task 41 by itself.

- [ ] Verify all 20 required cases and the adapted Task 41-PRE remote matrix have explicit evidence; missing evidence means `BLOCKED`.
- [ ] Report exact provider/runtime, immutable image digest/hash, SDK output, authentication model, endpoint exposure, data retention, cost, resource IDs in non-sensitive form and teardown result.
- [ ] Report `Remote Runner Prototype = PASS/BLOCKED` separately from `Task 41-RMT-PRE = PASS/BLOCKED`.
- [ ] State whether paid/long-lived infrastructure or real credentials would be required for the next step; do not create them.
- [ ] State explicitly that Task 41, Task 42–46 and Phase G remain frozen pending independent security retest and controller registration.
- [ ] Run `rg -n "TODO|TBD|Bearer |token=|password=|hidden-test-body" tools/remote_runner_prototype`; any secret, placeholder or hidden body blocks delivery.
- [ ] Commit only after formal dispatch with message `docs(remote-runner): report viability gate result`, then stop without implementing `CSharpRunner`.

## Acceptance sequence after this plan

```text
Task 41-RMT-PRE report
→ Remote Runner Prototype verdict
→ independent security retest by Testing & Audit
→ adapted Task 41-PRE remote matrix replay
→ controller registration
→ only then Task 41 may become READY FOR DISPATCH
```
