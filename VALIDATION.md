# Verification evidence

Environment: Windows, installed CPython 3.13.7 (MSC v.1944 AMD64), Bandit 1.9.4. No dependency installation or remote inference. Evidence is local; other patches/platforms, complete standard conformance, hosted CI and independent audit are not verified.

| Check | Result | Evidence under .private/verification |
|---|---|---|
| python -m unittest discover -v | PASS, exit 0, 28 tests, no skips | accepted-normal.log |
| python -O -m unittest discover -v | PASS, exit 0, 28 tests, no skips | accepted-optimized.log |
| Five fixed mutants on final code | PASS harness exit 0; each mutant exit 1/one assertion failure; originals unchanged | mutations-accepted/summary.json and individual result.log |
| python -m compileall -q pointer_lab scripts tests | PASS, exit 0 | final compile evidence recorded in final receipt |
| Bandit runtime/demo | PASS, exit 0, zero remaining findings/errors, 333 LOC, four B105 skips | bandit-accepted.json/log |
| Exact original fixture freeze | PASS: 35 complete reports and four diagnostic/status cases; original SHA256 unchanged | research freeze-v1.json, fixture identity test |
| Actual CLI error/delivery checks | PASS, both suite modes | accepted suite logs/tests/test_cli.py |
| Demo full expected eight-row report and exclusive retry | PASS, both modes; complete exit 1, retry 2 | accepted suite logs; samples/demo-report.json |
| Source/evidence receipt and targeted secret-signature check | Final receipt generated and independently rehashed at handoff | final-receipt.json |

Frozen fixture SHA256: `08259975a8b68378a4a397251db85769830a2873b2ccbe5297422b7e59cc0117`. `.private/research/freeze-v1.json` binds PLAN.md, original fixture bytes and the original authoring helper before runtime implementation. It is a historical freeze, not a current mutable-doc manifest. All 17 upstream private captures match inspected Git blob identities; they were not executed/adopted.

Suite tests include complete original reports, fixed unknown/invalid precedence, early lexical gate checks with decoder mocked, exact roots/null/false/zero/Unicode/escapes/percent/NUL, strict list indices and huge object names, detached snapshots, shared aliases, cycles, subclass/metaclass hooks, structure/string/numeric limits, output cap boundaries, exclusive/hard-link/empty/NUL paths, observed pre/post metadata changes, dirty short/write/flush/close sinks, --help delivery and actual closed stdout/stderr readers. Optimized suites launch optimized CLI/demo children too. Physical output-close failure is simulated; real closed-pipe failures are measured. No live/hostile target or true hostile file race is tested.

Actual output amplification: 32 strings × 64 supplementary scalars, 16 root references. UTF-8 input 8957 bytes; selected report ASCII bytes including newline 397700; lookup itself succeeds, serializer rejects at 262144 before file creation/stdout emission. The weakened 524288-byte cap mutant fails the independent overflow assertion. Four other mutants reverse escape order, permit leading zeros, conflate truthiness and normalize exact tokens; all fail assertions, not import/syntax errors.

Preserved failures: initial sandbox run had one hard-link PermissionError (24 other tests passed); app-approved full rerun verified it with no skip. The later metaclass regression deliberately failed before identity fix and passed afterward. Initial Bandit had four B105 heuristic matches; final scan uses three narrow annotated lines/four verified false-positive skips. Bandit metrics reports nosec=0 because these are rule-specific annotations, while skipped_tests=4 records the actual exclusions. Tests and trusted verification harnesses are outside that runtime scan scope; no blanket scanner-clean claim.

Earlier 25/27-test intermediate runs and mutations-v1/mutations-final remain chronological evidence, not the final accepted source receipt. No redundant check is presented as an independent result. No Git repository/history, owned remote security eligibility, CodeQL or hosted workflow was created or assessed; explicitly excluded repository work would need its own authorization. Targeted local signatures are not a full secret scanner.
