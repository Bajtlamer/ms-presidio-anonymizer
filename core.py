"""
core.py  --  Markdown-aware anonymizer for mixed EN/CZ text.
"""

import re
from typing import Optional


PATTERNS: list[tuple[str, str]] = [
    ("IBAN",        r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b'),
    ("CREDIT_CARD", r'\b(?:\d[ -]?){13,16}\b'),
    ("EMAIL",       r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b'),
    ("URL",         r'https?://[^\s\)\]>\"]+'),
    ("IP_ADDRESS",  r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    ("CZ_RC",       r'\b\d{6}/\d{3,4}\b'),
    ("CZ_ICO",      r'\bIČO\s*:?\s*\d{8}\b'),
    ("CZ_DIC",      r'\bDIČ\s*:?\s*CZ\d{8,10}\b'),
    ("PHONE",       r'(?:\+420|\+421|00420|00421)\s?(?:\d[\s]?){9}'),
    ("PHONE",       r'\b\+?\d[\d\s\-().]{7,}\d\b'),
]

_CODE_FENCE  = re.compile(r'(```[\s\S]*?```|~~~[\s\S]*?~~~)', re.MULTILINE)
_FRONTMATTER = re.compile(r'^---\n[\s\S]*?\n---\n', re.MULTILINE)


def _split_protected(text: str) -> list[tuple[str, bool]]:
    ranges: list[tuple[int, int]] = []
    fm = _FRONTMATTER.match(text)
    if fm:
        ranges.append((fm.start(), fm.end()))
    for m in _CODE_FENCE.finditer(text):
        ranges.append((m.start(), m.end()))
    if not ranges:
        return [(text, False)]
    ranges.sort()
    segments: list[tuple[str, bool]] = []
    cursor = 0
    for start, end in ranges:
        if cursor < start:
            segments.append((text[cursor:start], False))
        segments.append((text[start:end], True))
        cursor = end
    if cursor < len(text):
        segments.append((text[cursor:], False))
    return segments


_nlp_models: Optional[list] = None

NER_MAP = {
    "PERSON": "PERSON", "PER": "PERSON", "P": "PERSON",
    "ORG":    "ORG",
    "GPE":    "LOCATION", "LOC": "LOCATION",
}


def _load_models() -> list:
    try:
        import spacy
    except ImportError:
        print("[anonymizer] spaCy not installed. Regex-only mode.")
        return []
    loaded = []
    for name in ("en_core_web_lg", "en_core_web_sm"):
        try:
            loaded.append(spacy.load(name, disable=["parser", "lemmatizer"]))
            print(f"[anonymizer] Loaded: {name}")
            break
        except OSError:
            pass
    for name in ("cs_core_news_lg", "cs_core_news_sm"):
        try:
            loaded.append(spacy.load(name, disable=["parser", "lemmatizer"]))
            print(f"[anonymizer] Loaded: {name}")
            break
        except OSError:
            pass
    return loaded


def _models() -> list:
    global _nlp_models
    if _nlp_models is None:
        _nlp_models = _load_models()
    return _nlp_models


def _ner_spans(text: str) -> list[tuple[int, int, str]]:
    spans = []
    for nlp in _models():
        for ent in nlp(text).ents:
            mapped = NER_MAP.get(ent.label_)
            if mapped:
                spans.append((ent.start_char, ent.end_char, mapped))
    return spans


class ReplacementMap:
    def __init__(self):
        self._fwd: dict[str, str] = {}
        self._rev: dict[str, str] = {}
        self._cnt: dict[str, int] = {}

    def get_or_create(self, etype: str, original: str) -> str:
        key = f"{etype}:{original}"
        if key not in self._fwd:
            self._cnt[etype] = self._cnt.get(etype, 0) + 1
            ph = f"[{etype}_{self._cnt[etype]}]"
            self._fwd[key] = ph
            self._rev[ph] = original
        return self._fwd[key]

    def restore(self, text: str) -> str:
        for ph, orig in sorted(self._rev.items(), key=lambda x: -len(x[0])):
            text = text.replace(ph, orig)
        return text

    def to_dict(self) -> dict:
        return dict(self._rev)

    @classmethod
    def from_dict(cls, data: dict) -> "ReplacementMap":
        obj = cls()
        for ph, orig in data.items():
            parts = ph.strip("[]").rsplit("_", 1)
            etype = parts[0] if len(parts) == 2 else "UNKNOWN"
            obj._fwd[f"{etype}:{orig}"] = ph
            obj._rev[ph] = orig
            n = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else 0
            obj._cnt[etype] = max(obj._cnt.get(etype, 0), n)
        return obj


def _anonymize_plain(text: str, rmap: ReplacementMap) -> str:
    hits: list[tuple[int, int, str, str]] = []
    for etype, pat in PATTERNS:
        for m in re.finditer(pat, text):
            hits.append((m.start(), m.end(), etype, m.group()))
    for start, end, etype in _ner_spans(text):
        hits.append((start, end, etype, text[start:end]))
    if not hits:
        return text
    hits.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    resolved: list[tuple[int, int, str, str]] = []
    last_end = -1
    for start, end, etype, orig in hits:
        if start >= last_end:
            resolved.append((start, end, etype, orig))
            last_end = end
    for start, end, etype, orig in sorted(resolved, key=lambda x: -x[0]):
        ph = rmap.get_or_create(etype, orig)
        text = text[:start] + ph + text[end:]
    return text


def anonymize_markdown(text: str, rmap=None) -> tuple[str, ReplacementMap]:
    if rmap is None:
        rmap = ReplacementMap()
    parts = []
    for segment, protected in _split_protected(text):
        parts.append(segment if protected else _anonymize_plain(segment, rmap))
    return "".join(parts), rmap


def deanonymize_markdown(text: str, rmap: ReplacementMap) -> str:
    return rmap.restore(text)