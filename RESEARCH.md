# JSON Pointer resolution lab: research

Research date: 2026-10-05. This is the preserved research-stage assessment, not implementation authorization. The coordinator subsequently approved PLAN.md stages 1–5 at 03:51; current implementation/verification state is in STATE.md. Installation, new repository and third-party execution remain excluded.

## Recommendation

Build an original, dependency-free Python standard-library evaluator for a small, read-only plain-pointer profile. Defer the URI-fragment representation extension. The strongest inspected Python candidate is useful for general applications, but adapting its broader mutation, custom-object, sentinel and diagnostic contracts would obscure this lab's learning goals. This recommendation concerns fit; it does not certify either candidate safe.

## Reuse search

Read relevant JSON canonicalization and Unicode policy project/research notes, the selected vault's Home and Codex Integration notes, shared STARTUP guidance and the authoritative coordinator successor record. A bounded source/document search for JSON Pointer, RFC6901 and resolver names, excluding private evidence, dependencies, firmware and GLPI material, found no standalone evaluator to reuse. This was a relevant bounded search, not an exhaustive workspace or vault audit.

The existing Unicode and canonicalization labs offer reviewed patterns for whole-input admission, duplicate-key hooks, depth/numeric bounds, fixed diagnostics and bounded file/output handling. Adapt those ideas only after approval; preserve both labs and shared helpers. No cross-lab runtime dependency is proposed.

Connected GitHub repository search worked. It returned stefankoegl/python-json-pointer as the strongest direct Python fit, plus broader JSONPath, source-position tools and an archived mirror. Public primary-source access identified swaggerexpert/json-pointer as a useful URI-fragment comparison. No candidate code was executed.

## Primary standard and runtime sources

[RFC6901](https://www.rfc-editor.org/rfc/rfc6901.html), sections 3–8, defines the syntax and evaluation used here. Empty text selects the root; slash-prefixed tokens can be empty. Validate tilde escapes and decode `~1` before `~0`, exactly once. Member comparison preserves code-point identity without normalization. Array indices use ASCII decimal grammar without leading zeros; `-` names no concrete element. JSON decoding precedes pointer interpretation. Errors need an application contract.

The RFC's URI-fragment representation adds UTF-8 and percent encoding, and requires the media type to declare that fragment syntax. JSON alone does not imply it. This warrants a separate input mode and separate malformed-byte policy; the proposed first version does not decode fragments. NUL is allowed in pointer text and will remain escaped in reports. These are standard facts, not claims of complete conformance.

[Python 3.13 JSON documentation](https://docs.python.org/3.13/library/json.html) documents repeated-name and nonfinite-value defaults and decoder hooks. This lab will override those permissive defaults, bound input before parsing and replace exception messages with fixed diagnostics. The online page currently describes 3.13.16; local prior-lab evidence used CPython 3.13.7. No new implementation has been tested on either version.

## Candidate: python-json-pointer

Repository: [stefankoegl/python-json-pointer](https://github.com/stefankoegl/python-json-pointer). Inspected tree: `3e8b834d10027bab8613091bdcc8c7ad67434264`. Files read: README, LICENSE.txt, setup.py, requirements-dev.txt, jsonpointer.py, tests.py and .github/workflows/test.yaml. Private research captures preserve the source and license; they are not an adopted dependency.

Source reports version 3.1.1 and Python >=3.10. setup.py declares no runtime install requirements. Development requirements are unpinned wheel, setuptools, coverage and flake8. Imports use standard-library facilities. Repository metadata was nonarchived with a push timestamp of 2026-10-03T21:15:29Z; this is activity evidence, not a release or maintenance guarantee.

The constructor validates escapes and leading slash, and unescape applies the correct order. Array checks use fullmatch; leading zeros are rejected. Mapping tokens remain strings, including large numeric names. Tests cover specification examples, bounds, string traversal, huge numeric indices and leading zeros. The general API supports mutation and custom indexable objects. A sequence `-` lookup returns an EndOfList sentinel, intentionally tested; it does not select a concrete JSON value. Default verbose exceptions can include the document, also explicitly tested. These are API choices that require a wrapper for the proposed narrow lab, not demonstrated vulnerabilities.

The inspected CI configuration runs lint and coverage on Python 3.10–3.14 using mutable action version tags. Its existence does not establish passing checks. Open-issue metadata included CLI argument reports and a mutation feature request. A direct fetch of issue 43's body failed with a connector transport error; its title remains a reporter claim and was not reproduced. No current release, advisory, Scorecard or complete issue audit was performed.

Actual LICENSE.txt is three-clause BSD despite GitHub's ambiguous license metadata. Any source/test reuse must preserve its copyright, conditions and disclaimer. The recommendation is original implementation, not a fork or copied test suite.

## Candidate: swaggerexpert/json-pointer

Repository: [swaggerexpert/json-pointer](https://github.com/swaggerexpert/json-pointer). Inspected tree: `977e88545d9b6a31db0bfa8abf992454e7fc1926`. Files read: package.json, LICENSE, NOTICE, URI-fragment representation, unescape, evaluator, JSON realm, fragment/evaluation tests and test workflow. No npm installation or lifecycle hook was run.

Source reports 3.0.2, Node >=12.20.0 and a runtime dependency on apg-lite ^1.0.5, with broader build/test/release tooling. Metadata was nonarchived with a 2026-09-29T21:03:44Z push timestamp. Its separate fragment helpers illustrate the representation boundary well. The inspected decoder permits a missing hash prefix and returns the original fragment on malformed percent/UTF-8 decoding; tests explicitly exercise that fallback. A future strict extension should define its own rejection behavior rather than inherit this silently.

The evaluator uses grammar parsing, strict object/array defaults, own-property checks and safe index handling. Strict array hyphen, absent entries, leading zeros and scalar traversal have tests. General realms and relaxed modes exceed this lab's scope. The test workflow uses Node 24 and npm ci/npm test with mutable action tags. Other workflow names and a lockfile were present but their security results/dependency advisories were not audited. No CI pass or supply-chain safety claim is made.

The actual license is Apache-2.0. NOTICE additionally credits RFC-derived grammar/text under IETF Simplified BSD terms. Adopting those files would require preserving both applicable sets of notices and modification attribution. No such adoption is proposed.

## Separate URI-fragment assessment

A useful extension would need an explicit mode, required wrapper syntax, strict percent triplets, strict UTF-8, one decoding pass, byte limits before decoding and media-type assumptions. Cases must distinguish literal percent names from decoded names, malformed encodings and encoded slash separators. It introduces no network need, but adds another admission surface and ambiguity. Defer it until independently planned and approved; plain mode rejects hash-prefixed input and never percent-decodes. The inspected JavaScript candidate remains comparison material only.

## Worker and uncertainty record

The installed local Ollama helper drafted three learning labels in one bounded loopback call; raw response, metadata and Codex corrections are in .private/research. It omitted one requested distinction, which the reviewed plan restores. No remote inference, billing, provider probing or free-account eligibility assumptions were needed.

Source assessment supported a small original build. It is not exhaustive research, an independent security review, a complete RFC conformance verdict or proof of dependency safety. Approval was pending at the original research handoff and was subsequently recorded at 03:51. PLAN.md defines the approved profile, threat model, fixed oracles and stages.

All 17 private candidate captures were hashed after saving and matched their inspected GitHub blob identities. .private/research/capture-hashes.json records byte lengths, SHA256 and Git blob SHA1. This is capture-integrity evidence, not authenticated provenance, execution validation or permission to adopt code. The research vault milestone was saved and copy-hash verified; its location/hash are in STATE.md.
