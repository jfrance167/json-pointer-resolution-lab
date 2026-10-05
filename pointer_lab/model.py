"""Plain-pointer evaluation only after complete admission; no mutation or queries."""
import json
import re
from .contract import LIMITS, SCHEMA, LabError, Unsupported, validate


def _snapshot(value):
    # Only admitted builtins reach this copier, so no deepcopy/user hooks execute.
    if type(value) is dict:
        return {key: _snapshot(child) for key, child in value.items()}
    if type(value) is list:
        return [_snapshot(child) for child in value]
    return value


def _member_token(token):
    return token


def _select(document, decoded):
    current = document
    for index, original_token in enumerate(decoded):
        token = _member_token(original_token)
        if type(current) is dict:
            if token not in current:
                return None, "missing-member", index
            current = current[token]
        elif type(current) is list:
            # B105 false positive: RFC6901 nonexistent array marker, no credential.
            if token == "-":  # nosec B105
                return None, "array-end-marker", index
            if re.fullmatch(r"0|[1-9][0-9]*", token, flags=re.ASCII) is None:
                return None, "invalid-array-index", index
            maximum = str(len(current) - 1)
            if not current or len(token) > len(maximum) or (len(token) == len(maximum) and token > maximum):
                return None, "array-index-out-of-range", index
            current = current[int(token)]
        else:
            return None, "cannot-traverse-scalar", index
    return _snapshot(current), None, None


def analyze(envelope):
    """Return a detached report and exit status; invalid/unsupported inputs raise."""
    refs = validate(envelope)
    if envelope["schema"] != SCHEMA:
        raise Unsupported("unsupported schema")
    rows = []
    kinds = {dict: "object", list: "array", str: "string", int: "integer",
             bool: "boolean", type(None): "null"}
    for label, pointer, raw, decoded in refs:
        value, reason, index = _select(envelope["document"], decoded)
        row = {"label": label, "pointer": pointer, "raw_tokens": raw,
               "decoded_tokens": decoded,
               "token_codepoints": [[f"U+{ord(c):04X}" for c in t] for t in decoded],
               "resolved": reason is None}
        if reason is None:
            row.update(value_type=kinds[type(value)], value=value)
        else:
            row.update(reason=reason, failing_token_index=index)
        rows.append(row)
    report = {"profile": SCHEMA, "representation": "plain-pointer",
              "assumption": "synthetic local values; no authorization or identity-safety verdict",
              "limits": dict(LIMITS), "rows": rows}
    return report, 1 if any(not row["resolved"] for row in rows) else 0


def render(report):
    """Serialize validated reports before delivery; include newline in the cap."""
    text = json.dumps(report, ensure_ascii=True, allow_nan=False, separators=(",", ":")) + "\n"
    if len(text.encode("ascii")) > LIMITS["output_bytes"]:
        raise LabError("resource limit")
    return text
