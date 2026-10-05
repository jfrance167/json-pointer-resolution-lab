# Proposed plan: JSON Pointer resolution lab

Status: stages 1–5 approved by the coordinator's October 5 03:51 successor entry under Jake's direct delegated authority. Tier 3 bounded portfolio/security learning lab. This document is the coordinator-requested plan; tasks/todo.md tracks ordered stages. No new repository is authorized.

## Purpose and success

Demonstrate how an explicitly supplied plain pointer resolves into a synthetic JSON value. Make root versus empty member, escape order, exact member identity, strict array indexing and present-versus-absent values observable. Success means a bounded inert API/CLI, independent fixed expectations, meaningful mutation detection, normal/optimized checks, reviewed code and honest limitations. It is a learning profile, not a claim of general JSON or RFC conformance.

Use original Python standard-library code after approval. A strict admission module feeds token parsing, then a read-only evaluator, then a bounded ASCII JSON report. A CLI adds regular-file I/O without collection, privileges or ambient configuration. Tests depend on frozen independent fixtures rather than generated resolver expectations. README and an original license/AI disclosure finish the local artifact. Alternatives and inspected candidates are in RESEARCH.md.

## Exact proposed admission profile

Profile/schema identifier: `pointer-lab/1`. Input is one UTF-8 JSON object with exactly `schema`, `document`, `pointers`. Schema is an ASCII string of 1–64 characters limited to letters, digits, slash, period, underscore and hyphen. pointers is a list of 1–16 objects, each containing exactly `label` and `pointer`. Labels are unique ASCII letters/digits/underscore/hyphen, 1–32 characters. Pointer strings may be empty. Duplicate pointers with distinct labels are allowed and processed in supplied order.

The raw file limit is 32768 bytes. Reject a BOM, invalid UTF-8, trailing content, duplicate object keys at any nesting level, nonfinite values, fractions/exponents, `-0`, and integers outside ±(2**53−1). Numeric lexemes are limited to 32 characters before conversion. These numeric restrictions are a deliberately narrower JSON profile, not RFC6901 requirements. JSON backslash escapes are decoded once by the JSON parser; there is no second backslash interpretation. A duplicate spelling produced through JSON escapes also fails. The duplicate hook covers unselected branches.

Only exact built-in dict/list/str/int/bool/None types are admitted by the direct API. bool is distinguished from int before integer admission. Object keys must be exact strings. Strings reject surrogates and Unicode noncharacters; empty text, controls, formatting/default-ignorable, unassigned and private-use scalars are otherwise retained. There is no normalization, case folding, trimming or Unicode-version-dependent classification beyond these explicit scalar checks. Raw numeric spelling cannot be recovered by the direct parsed-object API; that limitation is documented.

Depth is at most 8 containers along any root-to-leaf path, counting the envelope itself. Document limits are 512 value nodes (the document root counts once; each object value and array element counts recursively), 64 container nodes, 128 scalars/512 UTF-8 bytes for each document key or string value, and a total of 2048 scalars/8192 UTF-8 bytes across all document keys/string values. Keys contribute to text totals but are not value nodes. Numbers/bool/null contribute value nodes but no text totals. Count every logical occurrence of a shared acyclic container in the direct API; reject an active-ancestor cycle. This avoids rejecting benign aliases while bounding repeated traversal. The implementation may not invoke arbitrary object hooks.

Each pointer is limited to 256 scalars/1024 UTF-8 bytes and 8 tokens. Raw and decoded tokens each have a 128-scalar/512-byte bound. Batch pointer totals are 4096 scalars/16384 bytes. Labels/schema have their separate bounds; they do not contribute to document or pointer totals. Limits are checked before lookup. Some byte limits may be redundant under scalar limits and must be reported honestly if so.

Validate the full document, envelope, all reference shapes, scalar/size limits and plain-pointer syntax before resolving any reference or classifying an unknown schema. A valid but unknown schema gives unsupported status; invalid common admission wins over unsupported. No report rows are emitted before whole-input admission completes. Unknown schema handling does not assert unknown-format semantics.

## Token and resolution contract

An empty pointer selects the entire document, including scalar/null roots. Otherwise require leading `/`, split on literal slash, validate every tilde is followed by 0 or 1, and replace `~1` with slash before `~0` with tilde, exactly once. Preserve original pointer text, raw tokens, decoded tokens and decoded-token code points in each report. Do not percent-decode: `/%41` selects a literal `%41` member. A hash-prefixed fragment is invalid plain-pointer syntax. NUL remains permitted scalar text and is escaped in serialized output.

At a dict, use the decoded string as an exact key and check membership explicitly. Numeric-looking names, empty names and `-` are valid object names. At a list, accept only ASCII `0` or a nonzero ASCII digit followed by ASCII digits. Leading zeros, signs, spaces and other Unicode digits do not index a list. `-` is a distinct nonexistent end marker. Compare decimal length/text against the last valid index before converting to int; do not perform unbounded integer conversion or coerce object keys.

Each pointer stops at its first unresolved token; other admitted pointers still run. Fixed reason categories: `missing-member`, `invalid-array-index`, `array-index-out-of-range`, `array-end-marker`, `cannot-traverse-scalar`. Report the zero-based failing token index. Do not report an invented failing index for root success. A successful row has `resolved: true`, `value_type` (object/array/string/integer/boolean/null), and the selected `value`; an unresolved row has `resolved: false`, its reason/index, and no `value` field. Actual null, false, zero, empty string/list/dict remain successful values. Selected values are detached built-in JSON snapshots, so changing a result cannot mutate the supplied document.

Reports include the profile and applied limits, a plain-pointer representation declaration and an explicit synthetic/local-only assumption. No authentication, access-control or identity-safety claim. Value and token text are evidence intended for the report; diagnostics do not echo documents, paths or exception text.

## Output and CLI

Serialize the entire report as ASCII JSON with nonfinite output disabled before emitting anything. Cap output at 262144 bytes including its newline. Exceeding the cap is an admission/output failure, not a truncated result. A planned genuine overflow case uses a document array of 32 strings, each containing 64 supplementary scalars, selected by 16 empty pointers. Its 2048 scalars/8192 UTF-8 bytes fit document limits, but repeated ASCII escaping exceeds the output cap. Measure this in implementation tests rather than claiming it has already run.

CLI accepts one named regular input file and optional exclusive fresh output path. Bounded pre/post file checks, no output overwrite, alias/hardlink safeguards and short/flush/close-write handling follow reviewed prior patterns. stdout stays machine-readable; stderr uses fixed bounded ASCII diagnostics. Exit 0: complete/all pointers resolved. Exit 1: complete/at least one unresolved. Exit 2: invalid input, resource/output limit or I/O failure. Exit 3: supported common shape with unknown schema. --help write failures are checked too. stdout and a newly created failing output may be partial on physical I/O failure; no atomic-write or hostile filesystem-race guarantee is claimed.

## Threat model and scope

Untrusted synthetic input can exploit parser defaults, duplicate names, nesting, large numbers, Unicode ambiguity, truthiness errors, oversized repeated selections and diagnostic leakage. Whole admission, exact built-in types, independent caps, explicit membership, exact code points, bounded serialization and fixed diagnostics address these within the local lab. Original JSON values still deliberately appear in requested reports. A hostile filesystem, concurrent API mutation, memory exhaustion outside stated bounds, real private documents and production authorization are outside the model.

Exclude mutation/JSON Patch, JSONPath/eval, custom mapping/attribute traversal, external references, schema/URL/file resolution, collection, live targets, real identifiers/documents, installation, network services, new repositories, publication, merge and spending. URI-fragment decoding is assessed in RESEARCH.md and deferred. No future extension is implicitly authorized.

## Independent oracle design

Freeze original synthetic values and expected outcomes before resolver code. For a toy object containing an empty-name null; arr = [false, 0, empty string]; names `a/b`, `/`, `~1`; obj with `01` and `-`; distinct composed/decomposed accent names; and literal `%41`, `A` and NUL names:

| Pointer | Fixed expected distinction |
|---|---|
| empty text | Whole original document, detached |
| `/` | Present null |
| `/arr/0`, `/arr/1`, `/arr/2` | Present false, integer zero, empty string |
| `/a~1b`, `/~1`, `/~01` | Slash-containing name, slash name, literal tilde-one name |
| `/obj/01`, `/obj/-` | Exact object members |
| `/arr/01`, `/arr/+1`, `/arr/１` | Invalid array index |
| `/arr/-`, `/arr/3`, `/absent` | End marker, out of range, missing member |
| `/arr/0/x` | Cannot traverse boolean, failing token 2 |
| Composed and decomposed accent references | Different exact members |
| `/%41`, `/A`, slash plus NUL | Different literal names; inert escaped output |

Also freeze empty arrays/objects, scalar roots, adjacent empty tokens, backslash names, huge numeric object names versus huge list indices, and repaired positives for unresolved cases. Invalid tilde anywhere, duplicate keys in unselected branches, late invalid reference, unsupported schema with late malformed reference, and exact/over resource boundaries must show whole-input behavior. An unknown schema with valid common admission alone returns unsupported. No expectations are derived by the resolver under test.

Meaningful assertion mutants: reverse escape substitution order; permit leading-zero list indices; use truthiness to classify selected values; normalize object keys/tokens; weaken the genuine output cap. Run separately against targeted independent assertions, preserve failure logs and confirm original source unchanged. Mutants may not pass merely through syntax/import failures. Normal and python -O runs must agree; runtime admission must not depend on assert.

## Ordered stages and definitions of done

1. Contract/fixtures: freeze exact fields, limits, ordering, fixed oracles and license/source references before code. Verify expected cases manually against sources and originals. Dependencies: implementation approval. No borrowed code/ABNF/data unless exact notices and bindings are reviewed first.
2. Admission/API: implement strict JSON/direct built-in admission, token parser and detached read-only resolution. Verify roots, false/null/zero, escape order, exact Unicode, index grammar, cycles/aliases and whole-input rejection with frozen cases. Dependencies: stage 1.
3. CLI/demo: add checked bounded I/O and ASCII report; demonstrate synthetic successes, unresolved references, invalid and unsupported input. Verify exclusive output, alias/hardlink, short writes/help failures, actual closed pipe, output overflow and optimized child behavior. Dependencies: stage 2.
4. Verification/review: run focused full suites normally and optimized, meaningful mutants, compile and installed Bandit without broad suppressions. Apply ECC self-review to actual code/callers/tests, fix findings and rerun affected checks. Save exact runtime, raw results, source/fixture hashes and remaining limits. This is a self-review unless independent review actually occurs. Dependencies: stage 3.
5. Documentation/handoff: README setup/demo/security/limitations/learning/license/AI disclosure, concise STATE/DECISIONS/LEARNING, verification receipt and relevant vault milestone. No repository creation or hosted CI is included; if separately authorized later, apply Jake's repository baseline then. Dependencies: verified stage 4.

Appropriate checks will be run once and repeated after consequential changes, not to inflate evidence. Initial target is installed CPython 3.13.7 on Windows; other patches/platforms remain unverified. No arbitrary coverage target or full-standard conformance claim. Current research captures are for assessment only and must stay separate from original implementation and adopted licensing material.

## Approval boundary

The coordinator's October 5 03:51 entry approves stages 1–5 after plan/source/capture/vault review. Preserve prior labs and parent/shared records. Its addendum requires pre-decoder lexical depth/numeric gates, explicit global/native alias/node counts, complete independent report/status/error oracles before code, actual output amplification, dirty/both-failing/help sinks and five assertion mutants. No new repository, installation, fragments, external references or publication is included.

## Approved contract freeze addendum

Global native admission precedes field interpretation: at most 563 value nodes, 82 containers, 8 container levels, 8192 total string/key scalars and 32768 total string/key UTF-8 bytes. Each global string/key is at most 1024 scalars/4096 UTF-8 bytes. Count shared acyclic subtrees at each logical occurrence; cycles fail against active ancestors. Doc counters and stricter field limits remain separate. No equality, iteration, string, copy or mapping hook is invoked on a non-built-in type. Types of keys are checked before sets/lookups. Only bounded, admitted builtins are copied for snapshots. Direct API rejects unknown shapes globally before applying schema logic; concurrent caller mutation is outside the model.

Fixed exception reasons/status: `invalid input` (exit 2) covers bytes/UTF-8/JSON/lexical/shape/type/scalar/duplicate/reference/numeric failures, `resource limit` (2) covers admitted structure/text/output caps, `unsupported schema` (3) follows full common admission, `I/O or output delivery failed` (2) covers CLI file/path/write failures, `invalid command arguments` (2) covers parser errors. Diagnostic JSON is exactly status error or unsupported, plus reason, ending in newline. Mixed invalid causes are not given a within-category ordering guarantee; every invalid/resource category wins over unsupported and any lookup. Syntax rejection is whole-batch invalid; semantic index/missing failures are ordinary per-row unresolved results.

Exact report top-level fields: profile, representation (`plain-pointer`), assumption (`synthetic local values; no authorization or identity-safety verdict`), limits, rows. Rows preserve label/pointer/raw_tokens/decoded_tokens/token_codepoints in supplied order plus resolved and success value_type/value or failure reason/failing_token_index. Limits names/values and independent full reports are frozen in fixtures/oracles.json before runtime code. A JSON-string encoder may mechanically format manually specified expectations; it must not derive expected resolutions or tokens by running a resolver.
