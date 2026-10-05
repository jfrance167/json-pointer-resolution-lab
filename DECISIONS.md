# Decisions

- Approved scope: PLAN.md stages 1–5, coordinator October 5 03:51 entry; local implementation/evidence/docs only, no new repository/install/publication. File-hash save points replace new Git commits because that operation is explicitly excluded. The relevant Git workflow skill cannot widen approval.
- Build original stdlib plain-pointer code. Candidate general APIs support broader semantics; a wrapper would complicate this precise teaching profile. No external code/test/grammar adoption or new runtime dependency.
- Keep URI-fragment decoding separate and deferred. Plain percent text stays literal, no media-type or wrapper assumptions, no implicit normalization.
- Reject duplicate keys globally and restrict numbers before decoding; invalid common admission wins over unknown schema. Whole references are validated before any lookup.
- Count shared acyclic native subtrees per occurrence and reject active-ancestor cycles. Exact-type **identity** checks avoid custom metaclass equality hooks; detached snapshots avoid caller-input mutation.
- Prefer fixed per-row unresolved reasons and omit value on failure. Present null/false/zero remain successes. Reports preserve raw/decoded token evidence rather than conflating representations.
- Enforce an output cap with a measured, reachable repeated-root overflow. Document redundant scalar/UTF-8/batch bounds honestly.
- Narrow B105 suppressions cover only numeric pointer-part caps and syntax markers, with retained initial findings and comments; no global Bandit skip or false clean-unsuppressed claim.
