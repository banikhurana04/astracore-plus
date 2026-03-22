"""
ASTraCore++ — lexer for a small C/C++-like subset.

Produces a flat list of (type, value) tokens for downstream analysis.
"""

from typing import List, Tuple

Token = Tuple[str, str]

KEYWORDS = frozenset(
    {"int", "if", "else", "for", "while", "return"}
)

# Longer operators first for greedy matching
OPERATORS_MULTI = ["==", "<=", ">="]
OPERATORS_SINGLE = set("+-*/=<>")

SYMBOLS = set(";,{}()")


def tokenize(source: str) -> List[Token]:
    """
    Tokenize preprocessed source (single-line, normalized spaces).
    Returns list of (type, value) tuples.
    """
    tokens: List[Token] = []
    i = 0
    n = len(source)

    while i < n:
        c = source[i]

        if c.isspace():
            i += 1
            continue

        # String literal (pass through as one token for fidelity)
        if c == '"':
            j = i + 1
            while j < n:
                if source[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                if source[j] == '"':
                    j += 1
                    break
                j += 1
            tokens.append(("STRING", source[i:j]))
            i = j
            continue

        # Char literal (simplified)
        if c == "'":
            j = i + 1
            if j < n and source[j] == "\\" and j + 2 < n:
                j += 3
            elif j < n:
                j += 1
            if j < n and source[j] == "'":
                j += 1
            tokens.append(("CHAR", source[i:j]))
            i = j
            continue

        # Number
        if c.isdigit():
            j = i
            while j < n and (source[j].isdigit() or source[j] == "."):
                j += 1
            tokens.append(("NUMBER", source[i:j]))
            i = j
            continue

        # Identifier or keyword
        if c.isalpha() or c == "_":
            j = i
            while j < n and (source[j].isalnum() or source[j] == "_"):
                j += 1
            word = source[i:j]
            if word in KEYWORDS:
                tokens.append(("KEYWORD", word))
            else:
                tokens.append(("IDENTIFIER", word))
            i = j
            continue

        # Multi-char operators
        two = source[i : i + 2]
        if len(two) == 2 and two in OPERATORS_MULTI:
            tokens.append(("OPERATOR", two))
            i += 2
            continue

        if c in OPERATORS_SINGLE:
            tokens.append(("OPERATOR", c))
            i += 1
            continue

        if c in SYMBOLS:
            tokens.append(("SYMBOL", c))
            i += 1
            continue

        # Unknown single character (keep for robustness)
        tokens.append(("UNKNOWN", c))
        i += 1

    return tokens
