"""Strict whole-input admission before schema decisions or pointer lookup."""
import json
import os
from pathlib import Path
import re
import stat

SCHEMA = "pointer-lab/1"
LIMITS = {"input_bytes": 32768, "depth": 8, "global_nodes": 563,
          "global_containers": 82, "global_scalars": 8192, "global_utf8_bytes": 32768,
          "global_text_scalars": 1024, "global_text_utf8_bytes": 4096,
          "document_nodes": 512, "document_containers": 64,
          "document_text_scalars": 128, "document_text_utf8_bytes": 512,
          "document_scalars": 2048, "document_utf8_bytes": 8192,
          "references": 16, "pointer_scalars": 256, "pointer_utf8_bytes": 1024,
          # B105 false positives: numeric pointer-part caps, no credentials.
          "tokens": 8, "token_scalars": 128, "token_utf8_bytes": 512,  # nosec B105
          "pointer_total_scalars": 4096, "pointer_total_utf8_bytes": 16384,
          "output_bytes": 262144, "integer_abs": 9007199254740991,
          "numeric_lexeme": 32}


class LabError(ValueError):
    """Fixed, bounded diagnostic selected by trusted code."""


class Unsupported(LabError):
    """Common admission succeeded, but schema is unsupported."""


def invalid():
    raise LabError("invalid input")


def bound(value, maximum):
    if value > maximum:
        raise LabError("resource limit")


def text_size(value, scalar_limit, byte_limit):
    if type(value) is not str:
        invalid()
    bound(len(value), scalar_limit)
    for char in value:
        cp = ord(char)
        if 0xD800 <= cp <= 0xDFFF or 0xFDD0 <= cp <= 0xFDEF or cp & 0xFFFF in (0xFFFE, 0xFFFF):
            invalid()
    size = len(value.encode("utf-8"))
    bound(size, byte_limit)
    return len(value), size


def _walk(value, prefix, parent_depth=0, active=None, counts=None):
    # Exact builtins prevent arbitrary iterator/equality/copy hooks. Aliases count
    # per logical occurrence, while active ancestors distinguish actual cycles.
    if active is None:
        active, counts = set(), [0, 0, 0, 0]
    counts[0] += 1
    bound(counts[0], LIMITS[prefix + "_nodes"])
    kind = type(value)
    if not any(kind is allowed for allowed in (dict, list, str, int, bool, type(None))):
        invalid()
    if kind is str:
        size = text_size(value, LIMITS[prefix + "_text_scalars"], LIMITS[prefix + "_text_utf8_bytes"])
        counts[2] += size[0]
        counts[3] += size[1]
    elif kind is int:
        if value > LIMITS["integer_abs"] or value < -LIMITS["integer_abs"]:
            invalid()
    elif kind is dict or kind is list:
        depth = parent_depth + 1
        bound(depth, LIMITS["depth"])
        counts[1] += 1
        bound(counts[1], LIMITS[prefix + "_containers"])
        ident = id(value)
        if ident in active:
            invalid()
        active.add(ident)
        if kind is dict:
            for key, child in value.items():
                size = text_size(key, LIMITS[prefix + "_text_scalars"], LIMITS[prefix + "_text_utf8_bytes"])
                counts[2] += size[0]
                counts[3] += size[1]
                bound(counts[2], LIMITS[prefix + "_scalars"])
                bound(counts[3], LIMITS[prefix + "_utf8_bytes"])
                _walk(child, prefix, depth, active, counts)
        else:
            for child in value:
                _walk(child, prefix, depth, active, counts)
        active.remove(ident)
    bound(counts[2], LIMITS[prefix + "_scalars"])
    bound(counts[3], LIMITS[prefix + "_utf8_bytes"])


def _keys(value, expected):
    if type(value) is not dict or len(value) != len(expected):
        invalid()
    if any(type(key) is not str for key in value) or set(value) != expected:
        invalid()


def _ascii(value, pattern):
    if type(value) is not str or re.fullmatch(pattern, value, flags=re.ASCII) is None:
        invalid()


def tokens(pointer):
    """Validate and retain both raw and once-decoded token provenance."""
    text_size(pointer, LIMITS["pointer_scalars"], LIMITS["pointer_utf8_bytes"])
    if pointer == "":
        return [], []
    if not pointer.startswith("/"):
        invalid()
    raw = pointer.split("/")[1:]
    bound(len(raw), LIMITS["tokens"])
    decoded = []
    for token in raw:
        text_size(token, LIMITS["token_scalars"], LIMITS["token_utf8_bytes"])
        if re.search(r"~(?:[^01]|$)", token):
            invalid()
        result = token.replace("~1", "/").replace("~0", "~")
        text_size(result, LIMITS["token_scalars"], LIMITS["token_utf8_bytes"])
        decoded.append(result)
    return raw, decoded


def validate(envelope):
    """Admit every value/reference before unsupported-schema or lookup decisions."""
    _walk(envelope, "global")
    _keys(envelope, {"schema", "document", "pointers"})
    _ascii(envelope["schema"], r"[A-Za-z0-9/._-]{1,64}")
    _walk(envelope["document"], "document", parent_depth=1)
    refs = envelope["pointers"]
    if type(refs) is not list or not refs:
        invalid()
    bound(len(refs), LIMITS["references"])
    labels, parsed = set(), []
    scalars = size = 0
    for ref in refs:
        _keys(ref, {"label", "pointer"})
        _ascii(ref["label"], r"[A-Za-z0-9_-]{1,32}")
        if ref["label"] in labels:
            invalid()
        labels.add(ref["label"])
        raw, decoded = tokens(ref["pointer"])
        parsed.append((ref["label"], ref["pointer"], raw, decoded))
        scalars += len(ref["pointer"])
        size += len(ref["pointer"].encode("utf-8"))
    bound(scalars, LIMITS["pointer_total_scalars"])
    bound(size, LIMITS["pointer_total_utf8_bytes"])
    return parsed


def _preflight(text):
    # A finite lexical gate, not a second JSON parser. Quoted text is skipped;
    # json.loads remains grammar authority after depth/numeric work is bounded.
    depth, quoted, escaped, index = 0, False, False, 0
    while index < len(text):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            bound(depth, LIMITS["depth"])
        elif char in "}]":
            depth -= 1
            if depth < 0:
                invalid()
        elif char in "-0123456789":
            end = index + 1
            while end < len(text) and text[end] in "-+0123456789.eE":
                end += 1
                bound(end - index, LIMITS["numeric_lexeme"])
            _integer(text[index:end])
            index = end - 1
        index += 1


def _integer(token):
    if len(token) > LIMITS["numeric_lexeme"]:
        raise LabError("resource limit")
    # B105 false positive: negative-zero numeric spelling is not a credential.
    if re.fullmatch(r"-?(?:0|[1-9][0-9]*)", token, flags=re.ASCII) is None or token == "-0":  # nosec B105
        invalid()
    value = int(token)
    if abs(value) > LIMITS["integer_abs"]:
        invalid()
    return value


def _reject(_token):
    invalid()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            invalid()
        result[key] = value
    return result


def parse(raw):
    """Decode exact bytes with lexical gates, duplicate rejection and full admission."""
    if type(raw) is not bytes:
        invalid()
    bound(len(raw), LIMITS["input_bytes"])
    try:
        text = raw.decode("utf-8", errors="strict")
        if text.startswith("\ufeff"):
            invalid()
        _preflight(text)
        envelope = json.loads(text, object_pairs_hook=_pairs, parse_int=_integer,
                              parse_float=_reject, parse_constant=_reject)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise LabError("invalid input") from error
    validate(envelope)
    return envelope


def _identity(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def read(path: Path):
    """Bound regular files and observed metadata changes; not hostile-race containment."""
    before = path.stat()
    if not stat.S_ISREG(before.st_mode):
        invalid()
    bound(before.st_size, LIMITS["input_bytes"])
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
    with os.fdopen(os.open(path, flags), "rb") as handle:
        opened = os.fstat(handle.fileno())
        if not stat.S_ISREG(opened.st_mode) or _identity(before) != _identity(opened):
            raise OSError("input changed")
        raw = handle.read(LIMITS["input_bytes"] + 1)
        bound(len(raw), LIMITS["input_bytes"])
        if len(raw) != opened.st_size or _identity(opened) != _identity(os.fstat(handle.fileno())):
            raise OSError("input changed")
        return raw
