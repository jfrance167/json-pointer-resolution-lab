# JSON Pointer Resolution Lab

Resolve supplied plain JSON Pointers into bounded synthetic JSON values, with an explicit distinction between a missing value and a present null, false, zero or empty value. Reports retain each original pointer, raw/decoded tokens, decoded code points, selected snapshots or the first unresolved token.

This local learning lab uses only Python's standard library. It does not collect documents, mutate JSON, follow external references or query networks. The profile is intentionally smaller than general JSON/RFC6901: integer-only numeric values, strict input limits and no URI-fragment mode.

## Run

From this folder, with Python 3.13:

```powershell
python -m pointer_lab samples/demo.json
python -m pointer_lab samples/demo.json --output fresh-report.json
python -m scripts.demo_reports --output another-fresh-report.json
```

The demo intentionally exits **1** because three references are unresolved; its eight rows also include successful null, false, zero, tilde-one and exact decomposed-name selections. Exit 0 means every reference resolved, 1 means a complete report has unresolved rows, 2 means invalid/limit/I/O failure, and 3 means full common admission succeeded with an unknown schema. Existing output files are never overwritten. No installation or pip command is needed.

Minimal input:

```json
{"schema":"pointer-lab/1","document":{"a":null},"pointers":[{"label":"example","pointer":"/a"}]}
```

An empty pointer selects the document root. `/` selects an empty object member. `~1` decodes to slash before `~0` decodes to tilde; therefore `/~01` selects a member named `~1`. Object names use exact code points: `01` is a valid member name, while `/01` cannot index an array. Percent text is literal in this mode, and `-` selects no concrete array value. These distinctions follow [RFC6901](https://www.rfc-editor.org/rfc/rfc6901.html); this is not a full-conformance claim.

## Architecture and API

`pointer_lab.contract.parse(bytes)` performs bounded lexical gates, strict JSON parsing and full admission. `pointer_lab.model.analyze(envelope)` admits exact built-in JSON structures and returns `(report, exit_code)`; it raises fixed `LabError` or `Unsupported` failures. `render(report)` serializes an already validated report; it is not an admission API for arbitrary caller objects. The CLI adds bounded regular-file reads, exclusive output creation and checked delivery. `scripts.demo_reports` reuses that CLI. `scripts.mutation_check` is a trusted local verification helper, not a document-processing service.

All documents/references are checked before lookup or unknown-schema classification. Duplicate decoded JSON keys anywhere, fractions/exponents/nonfinite values, negative-zero spelling, unsafe integers, invalid scalars, invalid escapes, unsupported types, cycles and over-limit input are rejected. JSON escaping is decoded once; original numeric spelling is unavailable to the native parsed-object API. Shared acyclic containers count at each logical occurrence. Selected snapshots are detached from input and from one another. Concurrent caller mutation is outside the contract.

## Limits and security model

The raw input cap is 32 KiB and container depth is eight including the envelope. Documents have at most 512 value nodes, 64 containers and 2048 total string/key scalars; each document key/string has at most 128 scalars. Up to 16 references have at most 256 scalars and eight tokens each. Exact global accounting, UTF-8 byte limits, ASCII labels, integer bounds, diagnostics and ordering are specified in PLAN.md and frozen fixtures/oracles.json. Byte caps at four bytes per allowed scalar are redundant safety assertions under the scalar rules; batch pointer caps equal the per-pointer maximum times reference count. Global text limits also exceed the maximum admitted known-envelope text. They still bound malformed/native structures before field interpretation. No independent coverage of an impossible over-bound state is claimed.

The output cap is 256 KiB including newline. A genuine admitted 8957-byte repeated-root input produces 397700 ASCII report bytes and is rejected before delivery. Successful report values/tokens intentionally contain the supplied synthetic evidence, escaped as inert JSON. Error diagnostics omit document/path/OS exception details. Dirty stdout/stderr and help failures return controlled status 2, including actual closed-pipe tests.

This model addresses bounded parser work, ambiguity, incorrect absence checks and report amplification. It does not provide authorization, authentication, account/identity safety, visual-confusable detection, a Unicode normalization policy, hostile filesystem-race containment or an atomic stdout transaction. Physical write failures can leave partial stdout or a partial newly created output file. Use synthetic inputs only; no production/private document support is claimed.

## Verification

```powershell
python -m unittest discover -v
python -O -m unittest discover -v
python -m compileall -q pointer_lab scripts tests
python -m scripts.mutation_check fresh-mutation-directory
python -m bandit -r pointer_lab scripts/demo_reports.py
```

Observed on Windows, CPython 3.13.7: **28 normal and 28 optimized tests, no skips**, 35 frozen complete expected reports plus four fixed error cases, actual normal/optimized CLI children, hard-link/exclusive/empty-path checks and real closed pipes. Five mutants independently fail targeted assertions. Bandit 1.9.4 scans 333 runtime/demo lines with zero remaining findings/errors and four narrowly documented B105 false-positive skips at three annotated lines. Tests and the trusted mutation/receipt harnesses are outside that runtime SAST scope. The first sandbox hard-link denial, intermediate scanner findings and demonstrated metaclass-hook regression are preserved.

VALIDATION.md, REVIEW.md and the private final source/evidence receipt record the checks and limits. ECC review was performed by the implementing agent, not independently. Other Python patches/platforms, complete RFC conformance, hosted CI and supply-chain/advisory audits are unverified. No repository was initialized, no dependencies installed, and no public/remote action occurred.

## Sources, license and learning

RESEARCH.md compares actual pinned Python/JavaScript candidate source, tests, licensing, dependencies and CI. No external candidate implementation, grammar or test data was adopted; their private captures remain research material. Original synthetic oracles were specified and hashed before runtime code. Own previously reviewed lab patterns inform admission/I/O handling.

Original lab code and original fixtures are MIT-licensed; see LICENSE and NOTICE.md. Codex assisted design, implementation, tests, review and documentation; Jake retains manual review and publication decisions. One local Ollama label draft was corrected, another was discarded for an incorrect escape instruction. Worker output is not verification evidence. No remote inference or new spending was used.

LEARNING.md explains absence, representation boundaries and exact-type checks. Optional exercise: add an object member named `01` and compare its resolution with the same text applied to an array.

## Publication status

See [publication review](PUBLICATION.md) for the October 5 source snapshot, fresh local checks, evidence boundaries and current hosted-check distinction.
