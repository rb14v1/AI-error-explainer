"""
Error pattern definitions for local deterministic classification.

Defines regex patterns and heuristics for recognizing common programming errors.
"""

import re
from typing import NamedTuple


class ErrorPattern(NamedTuple):
    """Definition of an error pattern."""
    name: str
    patterns: list[str]
    severity_base: str
    description: str


# Common error patterns by language and type
ERROR_PATTERNS = [
    # JavaScript / TypeScript errors
    ErrorPattern(
        name="TypeError: Undefined Property Access",
        patterns=[
            r"Cannot read propert(y|ies) .* of undefined",
            r"Cannot read propert(y|ies) .* of null",
            r"TypeError.*undefined",
        ],
        severity_base="High",
        description="Attempting to access a property on undefined or null value"
    ),
    ErrorPattern(
        name="TypeError: Cannot Call Non-Function",
        patterns=[
            r"is not a function",
            r"TypeError.*not a function",
        ],
        severity_base="High",
        description="Attempting to call something that is not a function"
    ),
    ErrorPattern(
        name="SyntaxError: Invalid Syntax",
        patterns=[
            r"SyntaxError",
            r"Unexpected token",
        ],
        severity_base="Critical",
        description="Code contains invalid syntax"
    ),
    ErrorPattern(
        name="ReferenceError: Undefined Variable",
        patterns=[
            r"is not defined",
            r"ReferenceError",
        ],
        severity_base="High",
        description="Attempting to use a variable that has not been declared"
    ),

    # Python errors
    ErrorPattern(
        name="AttributeError: Missing Attribute",
        patterns=[
            r"AttributeError.*has no attribute",
            r"has no attribute",
        ],
        severity_base="High",
        description="Object does not have the requested attribute"
    ),
    ErrorPattern(
        name="KeyError: Missing Dictionary Key",
        patterns=[
            r"KeyError",
        ],
        severity_base="High",
        description="Attempting to access a dictionary key that does not exist"
    ),
    ErrorPattern(
        name="IndexError: Array Out of Bounds",
        patterns=[
            r"IndexError.*out of range",
            r"list index out of range",
        ],
        severity_base="High",
        description="Attempting to access an array index that does not exist"
    ),
    ErrorPattern(
        name="ValueError: Invalid Value",
        patterns=[
            r"ValueError",
        ],
        severity_base="Medium",
        description="Function received an argument of correct type but inappropriate value"
    ),
    ErrorPattern(
        name="TypeError: Wrong Type",
        patterns=[
            r"TypeError.*expected",
            r"TypeError.*got",
        ],
        severity_base="High",
        description="Operation or function applied to object of inappropriate type"
    ),
    ErrorPattern(
        name="ZeroDivisionError",
        patterns=[
            r"ZeroDivisionError",
            r"division by zero",
        ],
        severity_base="High",
        description="Attempting to divide by zero"
    ),
    ErrorPattern(
        name="ImportError: Module Not Found",
        patterns=[
            r"ImportError",
            r"ModuleNotFoundError",
            r"No module named",
        ],
        severity_base="High",
        description="Attempting to import a module that does not exist"
    ),
    ErrorPattern(
        name="FileNotFoundError",
        patterns=[
            r"FileNotFoundError",
            r"\[Errno 2\].*No such file or directory",
        ],
        severity_base="Medium",
        description="Attempting to access a file that does not exist"
    ),
    ErrorPattern(
        name="NullPointerException / Null Reference",
        patterns=[
            r"NullPointerException",
            r"null reference",
            r"Cannot invoke.*on a null object reference",
        ],
        severity_base="High",
        description="Attempting to use a null/nil reference"
    ),
    ErrorPattern(
        name="RuntimeError",
        patterns=[
            r"RuntimeError",
        ],
        severity_base="High",
        description="Generic runtime error occurred"
    ),
    ErrorPattern(
        name="TypeError: Array Method on Non-Array",
        patterns=[
            r"\.map is not a function",
            r"\.filter is not a function",
            r"\.reduce is not a function",
        ],
        severity_base="High",
        description="Attempting to use array methods on a non-array value"
    ),
]


def classify_error(error_message: str) -> tuple[str, float]:
    """
    Classify an error message and return error type and confidence.

    Args:
        error_message: The error message to classify

    Returns:
        Tuple of (error_type, confidence)
    """
    if not error_message:
        return "Unknown Error", 0.0

    error_msg_lower = error_message.lower()

    # Check each pattern
    for pattern in ERROR_PATTERNS:
        for regex_pattern in pattern.patterns:
            if re.search(regex_pattern, error_message, re.IGNORECASE):
                # Higher confidence if pattern appears early in message
                position = error_message.lower().find(regex_pattern.lower())
                confidence = 0.95 if position < 100 else 0.85
                return pattern.name, confidence

    # Fallback: try to extract first line as error type
    first_line = error_message.split('\n')[0]
    if ':' in first_line:
        error_type = first_line.split(':')[0].strip()
        if error_type and len(error_type) < 100:
            return error_type, 0.6

    return "Unknown Error", 0.3
