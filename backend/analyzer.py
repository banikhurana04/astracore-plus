"""
ASTraCore++ — lightweight static analysis on token streams.

Heuristics (no full AST): tracks `int <name>` declarations and counts
identifier occurrences to flag unused or barely-used variables.
"""

from typing import List, Tuple

Token = Tuple[str, str]


def analyze(tokens: List[Token]) -> List[str]:
    """
    Return human-readable warnings:
    - Unused variable: declared with `int` but identifier appears only once.
    - Used only once: declared and referenced exactly once elsewhere (2 total).
    """
    warnings: List[str] = []

    # Count all identifier occurrences by name
    counts: dict = {}
    for t, v in tokens:
        if t == "IDENTIFIER":
            counts[v] = counts.get(v, 0) + 1

    # Find declarations: KEYWORD int followed by IDENTIFIER
    declared: List[str] = []
    i = 0
    while i < len(tokens) - 1:
        t0, v0 = tokens[i]
        t1, v1 = tokens[i + 1]
        if t0 == "KEYWORD" and v0 == "int" and t1 == "IDENTIFIER":
            # Skip function declarations: int name (
            if i + 2 < len(tokens) and tokens[i + 2][1] == "(":
                i += 1
                continue
            declared.append(v1)
        i += 1

    seen = set()
    for name in declared:
        if name in seen:
            continue
        seen.add(name)
        c = counts.get(name, 0)
        if c == 1:
            warnings.append(f'Unused variable: "{name}" (declared but never used).')
        elif c == 2:
            warnings.append(
                f'Variable "{name}" is only used once (besides declaration); '
                "consider removing or using meaningfully."
            )

    return warnings
