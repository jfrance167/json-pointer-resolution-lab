import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from pointer_lab.contract import LabError, Unsupported, parse, validate
from pointer_lab.model import analyze, render

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/oracles.json"
ORACLES = json.loads(FIXTURE.read_text(encoding="ascii"))


def envelope(document=None, pointers=("",), schema="pointer-lab/1"):
    return {"schema": schema, "document": document,
            "pointers": [{"label": f"case-{i}", "pointer": p} for i, p in enumerate(pointers)]}


def wire(value):
    return json.dumps(value, ensure_ascii=False).encode("utf-8")


class ModelTests(unittest.TestCase):
    def test_freeze_identity(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
                         "08259975a8b68378a4a397251db85769830a2873b2ccbe5297422b7e59cc0117")

    def test_full_original_reports(self):
        for case in ORACLES["cases"]:
            with self.subTest(case=case["name"]):
                original = copy.deepcopy(case["input"])
                actual, code = analyze(parse(wire(original)))
                self.assertEqual(actual, case["expected"])
                self.assertEqual(code, case["exit"])
                self.assertEqual(original, case["input"])
                self.assertEqual(json.loads(render(actual)), actual)

    def test_escape_order(self):
        report, code = analyze(envelope({"~1": 0, "/": 1}, ("/~01",)))
        self.assertEqual(report["rows"][0]["value"], 0)
        self.assertEqual(report["rows"][0]["decoded_tokens"], ["~1"])
        self.assertEqual(code, 0)

    def test_strict_index(self):
        report, code = analyze(envelope([0, 1], ("/01",)))
        self.assertEqual(code, 1)
        self.assertEqual(report["rows"][0]["reason"], "invalid-array-index")
        self.assertNotIn("value", report["rows"][0])

    def test_present_false_values(self):
        report, code = analyze(envelope({"n": None, "f": False, "z": 0, "s": "", "a": [], "o": {}},
                                        ("/n", "/f", "/z", "/s", "/a", "/o")))
        self.assertEqual(code, 0)
        self.assertEqual([r["value_type"] for r in report["rows"]],
                         ["null", "boolean", "integer", "string", "array", "object"])

    def test_exact_unicode(self):
        report, code = analyze(envelope({"\u00e9": 1, "e\u0301": 2}, ("/\u00e9", "/e\u0301")))
        self.assertEqual([r["value"] for r in report["rows"]], [1, 2])
        self.assertEqual(code, 0)

    def test_detached_snapshots_and_aliases(self):
        shared = {"a": []}
        source = envelope([shared, shared], ("", "/0", "/1"))
        report, _ = analyze(source)
        report["rows"][0]["value"][0]["a"].append(1)
        report["rows"][1]["value"]["a"].append(2)
        self.assertEqual(source["document"], [{"a": []}, {"a": []}])
        self.assertEqual(report["rows"][2]["value"], {"a": []})
        self.assertEqual(report["rows"][0]["value"][1], {"a": []})

    def test_cycles_and_hooks(self):
        cycle = []
        cycle.append(cycle)
        self.assertRaises(LabError, analyze, envelope(cycle))
        calls = []

        class Evil(dict):
            def items(self):
                calls.append("items")
                raise RuntimeError("hook")

        class EvilString(str):
            def __hash__(self):
                calls.append("hash")
                return 0

        self.assertRaises(LabError, analyze, Evil(envelope()))
        self.assertRaises(LabError, analyze, envelope(Evil()))
        source = envelope()
        source["schema"] = EvilString("pointer-lab/1")
        self.assertRaises(LabError, analyze, source)
        self.assertEqual(calls, [])

    def test_whole_input_precedence(self):
        for case in ORACLES["errors"]:
            with self.subTest(case=case["name"]):
                with self.assertRaises(LabError) as caught:
                    analyze(parse(case["raw"].encode("ascii")))
                self.assertEqual(str(caught.exception), case["diagnostic"]["reason"])
                self.assertEqual(isinstance(caught.exception, Unsupported), case["exit"] == 3)
        bad = envelope({"bad": float("nan")}, ("/missing",), "unknown/1")
        with patch("pointer_lab.model._select") as lookup:
            self.assertRaises(LabError, analyze, bad)
            lookup.assert_not_called()
        self.assertRaises(LabError, analyze, envelope(None, ("", "/~2")))

    def test_metaclass_equality_never_called(self):
        calls = []

        class HookMeta(type):
            def __eq__(self, other):
                calls.append(other)
                return False

        class Hooked(metaclass=HookMeta):
            pass

        self.assertRaises(LabError, analyze, envelope(Hooked()))
        self.assertEqual(calls, [])

    def test_lexical_gates_before_decoder(self):
        for raw in (b"[" * 9 + b"0" + b"]" * 9, b"9" * 33, b"1e2", b"-0", b"9007199254740992"):
            with self.subTest(raw=raw), patch("pointer_lab.contract.json.loads") as decode:
                self.assertRaises(LabError, parse, raw)
                decode.assert_not_called()
        # Brackets and digits in quoted text do not consume lexical depth/number work.
        report, _ = analyze(parse(wire(envelope("[" * 64 + "9" * 64))))
        self.assertEqual(len(report["rows"][0]["value"]), 128)

    def test_json_rejections(self):
        raw_cases = [b"\xef\xbb\xbf{}", b"\xff", b"{} {}", b"{", b"NaN", b"Infinity", b"1.0",
                     b"01", b"-01", b"1e+2", b'"\\ud800"', b'{"x":1,"\\u0078":2}']
        for raw in raw_cases:
            with self.subTest(raw=raw):
                self.assertRaises(LabError, parse, raw)
        self.assertRaises(LabError, parse, bytearray(b"{}"))
        self.assertRaises(LabError, parse, b" " * 32769)
        self.assertRaises(LabError, analyze, envelope(9007199254740992))
        self.assertRaises(LabError, analyze, envelope(1.0))
        for n in (-9007199254740991, 9007199254740991):
            self.assertEqual(analyze(parse(wire(envelope(n))))[0]["rows"][0]["value"], n)

    def test_shape_and_pointer_rejections(self):
        for pointer in ("#", "#/a", "a", "/~", "/~2", "/a~9b"):
            self.assertRaises(LabError, analyze, envelope(None, (pointer,)))
        for bad in ([], {}, {**envelope(), "extra": 0}, {**envelope(), "pointers": []},
                    envelope(None, tuple("" for _ in range(17)))):
            self.assertRaises(LabError, analyze, bad)
        duplicate = envelope(None, ("", ""))
        duplicate["pointers"][1]["label"] = "case-0"
        self.assertRaises(LabError, analyze, duplicate)
        for label in ("", "a" * 33, "\u00e9", "bad label"):
            bad = envelope()
            bad["pointers"][0]["label"] = label
            self.assertRaises(LabError, analyze, bad)

    def test_scalar_and_token_boundaries(self):
        self.assertEqual(analyze(envelope("\U0001f600" * 128))[1], 0)
        self.assertRaises(LabError, analyze, envelope("a" * 129))
        for value in ("\ud800", "\ufdd0", "\U0001ffff", "\ufffe"):
            self.assertRaises(LabError, analyze, envelope(value))
        self.assertEqual(analyze(envelope("\u0000\u200b\ue000\u0378"))[1], 0)
        self.assertEqual(analyze(envelope({}, ("/" + "a" * 128,)))[1], 1)
        self.assertRaises(LabError, analyze, envelope({}, ("/" + "a" * 129,)))
        self.assertEqual(analyze(envelope({}, ("/" * 8,)))[1], 1)
        self.assertRaises(LabError, analyze, envelope({}, ("/" * 9,)))
        self.assertEqual(analyze(envelope({}, ("/" + "a" * 127 + "/" + "b" * 127,)))[1], 1)
        self.assertRaises(LabError, analyze, envelope({}, ("/" + "a" * 128 + "/" + "b" * 127,)))

    def test_document_nodes_alias_counts_and_depth(self):
        validate(envelope([0] * 511))
        self.assertRaises(LabError, validate, envelope([0] * 512))
        validate(envelope([[] for _ in range(63)]))
        self.assertRaises(LabError, validate, envelope([[] for _ in range(64)]))
        shared = [0] * 255
        self.assertRaises(LabError, validate, envelope([shared, shared]))
        nested = 0
        for _ in range(7):
            nested = [nested]
        validate(envelope(nested))
        self.assertRaises(LabError, validate, envelope([nested]))
        huge_unknown = envelope(None, schema="unknown/1")
        huge_unknown["extra"] = [0] * 564
        with self.assertRaises(LabError) as caught:
            analyze(huge_unknown)
        self.assertNotIsInstance(caught.exception, Unsupported)

    def test_document_aggregate_and_global_bounds(self):
        validate(envelope(["a" * 128] * 16))
        self.assertRaises(LabError, validate, envelope(["a" * 128] * 16 + ["a"]))
        self.assertRaises(LabError, validate, envelope({"a" * 128: "b" * 128 for _ in range(1)} | {"x": "y" * 129}))
        from pointer_lab.contract import _walk
        _walk([0] * 562, "global")
        self.assertRaises(LabError, _walk, [0] * 563, "global")
        _walk([[] for _ in range(81)], "global")
        self.assertRaises(LabError, _walk, [[] for _ in range(82)], "global")
        _walk(["a" * 1024] * 8, "global")
        self.assertRaises(LabError, _walk, ["a" * 1024] * 8 + ["a"], "global")
        self.assertRaises(LabError, _walk, "a" * 1025, "global")

    def test_output_overflow(self):
        source = envelope(["\U0001f600" * 64] * 32, tuple("" for _ in range(16)))
        self.assertLess(len(wire(source)), 32768)
        report, code = analyze(parse(wire(source)))
        self.assertEqual(code, 0)
        actual_bytes = len((json.dumps(report, ensure_ascii=True, separators=(",", ":")) + "\n").encode("ascii"))
        self.assertGreater(actual_bytes, 262144)
        self.assertLess(actual_bytes, 524288)
        with self.assertRaises(LabError) as caught:
            render(report)
        self.assertEqual(str(caught.exception), "resource limit")

    def test_exact_output_cap(self):
        # Exact serializer boundary independent of the resolver.
        self.assertEqual(len(render("a" * 262141).encode("ascii")), 262144)
        self.assertRaises(LabError, render, "a" * 262142)


if __name__ == "__main__":
    unittest.main()
