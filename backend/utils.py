"""
ASTraCore++ — preprocessing and token normalization utilities.

Strips C/C++-style comments, normalizes whitespace, and maps identifiers
and numeric literals to abstract placeholders for similarity comparison.
"""

import re
from typing import List, Tuple

# Token tuples from the lexer: (type, value)
Token = Tuple[str, str]


def remove_comments(source: str) -> str:
    """
    Remove // single-line and /* */ multi-line comments.
    Preserves string literals roughly by not stripping // inside strings
    (simplified: we process char-by-char with a small state machine).
    """
    result: List[str] = []
    i = 0
    n = len(source)
    in_string = False
    string_char = ""

    while i < n:
        ch = source[i]

        if not in_string:
            # Start of string
            if ch in ('"', "'"):
                in_string = True
                string_char = ch
                result.append(ch)
                i += 1
                continue
            # Multi-line comment
            if ch == "/" and i + 1 < n and source[i + 1] == "*":
                i += 2
                while i < n:
                    if source[i] == "*" and i + 1 < n and source[i + 1] == "/":
                        i += 2
                        break
                    i += 1
                result.append(" ")
                continue
            # Single-line comment
            if ch == "/" and i + 1 < n and source[i + 1] == "/":
                i += 2
                while i < n and source[i] not in "\r\n":
                    i += 1
                result.append(" ")
                continue
            result.append(ch)
            i += 1
        else:
            result.append(ch)
            if ch == "\\" and i + 1 < n:
                result.append(source[i + 1])
                i += 2
                continue
            if ch == string_char:
                in_string = False
            i += 1

    return "".join(result)


def normalize_whitespace(source: str) -> str:
    """Collapse runs of whitespace to a single space and strip ends."""
    source = re.sub(r"[ \t\r\n]+", " ", source)
    return source.strip()


def preprocess(code: str) -> str:
    """
    Full preprocessing pipeline: strip comments, normalize spacing.
    Returns cleaned source suitable for lexing.
    """
    cleaned = remove_comments(code)
    return normalize_whitespace(cleaned)


def normalize_tokens(tokens: List[Token]) -> List[Token]:
    """
    Normalize token stream for plagiarism-resistant comparison:
    - identifiers → ("IDENTIFIER", "ID")
    - numbers → ("NUMBER", "NUM")
    Keywords, operators, and symbols keep their concrete values.
    """
    out: List[Token] = []
    for t, v in tokens:
        if t == "IDENTIFIER":
            out.append(("IDENTIFIER", "ID"))
        elif t == "NUMBER":
            out.append(("NUMBER", "NUM"))
        else:
            out.append((t, v))
    return out
