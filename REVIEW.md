# ECC self-review

Scope: all original pointer_lab runtime, demo/mutation helpers, tests, frozen report/error fixtures, input sample and their callers. Baseline was research-only with no runtime. Read complete admission/evaluation/CLI/helpers/tests and reviewed correctness, trust boundaries, data preservation, bounded work, error delivery, licensing and verification. Implementing-agent review, not independent review. No Git diff/commit or hosted review exists because a new repository was expressly excluded.

## Findings and corrections

MEDIUM: exact-type admission in pointer_lab/contract.py `_walk` originally used `kind not in (dict, list, ...)`. A custom metaclass __eq__ ran six times on rejected input, violating the no-hooks contract. The concrete regression `test_metaclass_equality_never_called` failed by assertion before the fix; before/after logs are preserved. Current identity guards are at contract.py:61 and :70. Focused regression and full normal/optimized suites pass afterward.

LOW: the first scripts/demo_reports.py version used separate argparse/output handling whose failures could expose a traceback rather than the primary CLI's fixed errors. Before final acceptance it was replaced by a thin checked-CLI wrapper. The demo full-report/exclusive-reuse test requires complete status 1 and fixed failure status 2; optimized children verify the same behavior. No claim that the earlier helper was accepted.

Four initial Bandit B105 findings at the numeric pointer-part bounds and `-0`/`-` markers are verified false positives: these are resource numbers/grammar sentinels, not authentication material. Three rule-specific source annotations retain explanatory comments, resulting in four skipped findings. Initial scanner JSON and final JSON/log are retained. No global suppression or confirmed vulnerability dismissal.

The native integer bound uses ordered comparisons rather than abs on arbitrarily large preconstructed integers. The global walker rejects non-builtins before operations, counts aliases per occurrence and restricts recursion. Duplicate JSON names and lexical number/depth rules cover unselected branches before schema/lookup. All selected values are copied only after admission. The checked CLI uses exclusive outputs, explicit optional-path presence and sanitized dirty output/error sinks; actual real-pipe tests guard interpreter exit120 regressions.

The final source-receipt helper was read and executed against saved evidence; all preliminary 43 entries independently rehashed without mismatch. It verifies fixed fixture identity, accepted suite totals, current mutation source hashes and each raw mutant log digest/assertion marker. Targeted credential signatures return no values. The mutation helper now rejects a fresh output nested inside copied source directories; a focused manual guard check confirmed no directory was created. This prevents accidental recursive self-copy and leaves current runtime/tests unchanged. Verification-helper output/tracebacks are for trusted operator use; the application/demo reuse the fixed-error CLI. No further defect found in those helper paths after inspection.

## Final disposition

No remaining actionable defect found in the reviewed scope after focused fixes and affected checks. Critical/high: 0. Medium: 1 fixed. Low: 1 fixed. Scanner: 4 false-positive matches narrowly explained. Local result is ready for coordinator review, not merge/deployment/publication. Residual limits are in SECURITY.md and VALIDATION.md; review does not certify safety or completeness.
