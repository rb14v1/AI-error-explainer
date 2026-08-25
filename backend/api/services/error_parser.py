"""
Error Message Parser

Extracts structured components from raw error messages:
- error_type/category
- error_symbol (variable/function/module name)
- error_code (if present)
- language_hint (JS/Python/etc inferred from format)
- actual_error_line (final exception line, especially for tracebacks)
"""

import re
from typing import NamedTuple, Optional


class ParsedError(NamedTuple):
    """Structured error components."""
    error_type: str
    error_symbol: Optional[str]
    error_code: Optional[str]
    language_hint: Optional[str]
    first_line: str
    full_message: str
    actual_error_line: str  # Final exception line for tracebacks


def parse_error(error_message: str) -> ParsedError:
    """
    Parse error message into components.

    Handles Python tracebacks specially: extracts the final exception line
    rather than "Traceback (most recent call last):".

    Args:
        error_message: Raw error message string

    Returns:
        ParsedError with structured components
    """
    if not error_message:
        return ParsedError(
            error_type="Unknown Error",
            error_symbol=None,
            error_code=None,
            language_hint=None,
            first_line="",
            full_message="",
            actual_error_line=""
        )

    error_message = error_message.strip()
    lines = error_message.split('\n')

    # Detect if this is a Python traceback
    is_python_traceback = any('Traceback' in line for line in lines[:3])

    if is_python_traceback:
        # Find the actual exception line (last non-empty line)
        actual_error_line = _extract_final_exception_line(lines)
        first_line = lines[0] if lines else ""
    else:
        actual_error_line = lines[-1] if lines else ""
        first_line = lines[0] if lines else ""

    # Extract error type from actual exception line
    error_type = _extract_error_type(actual_error_line)

    # Extract error symbol (variable/function/module name)
    error_symbol = _extract_error_symbol(error_message)

    # Extract error code if present (e.g., E0001)
    error_code = _extract_error_code(error_message)

    # Hint language from error format
    language_hint = _hint_language(error_message)

    return ParsedError(
        error_type=error_type,
        error_symbol=error_symbol,
        error_code=error_code,
        language_hint=language_hint,
        first_line=first_line,
        full_message=error_message,
        actual_error_line=actual_error_line
    )


def _extract_error_type(first_line: str) -> str:
    """Extract error type/category from first line."""
    if not first_line:
        return "Unknown Error"

    # Match "ErrorType: Message" pattern
    if ':' in first_line:
        error_type = first_line.split(':')[0].strip()
        if error_type and len(error_type) < 100:
            return error_type

    # Fallback to first line
    return first_line[:80] if len(first_line) > 80 else first_line


def _extract_error_symbol(error_message: str) -> Optional[str]:
    """
    Extract the symbol (variable/function/module) involved in error.

    Examples:
    - 'Cannot read property "map" of undefined' → "map"
    - 'myVar is not defined' → "myVar"
    - 'No module named 'psycopg2'' → "psycopg2"
    - 'AttributeError: 'str' object has no attribute 'foo'' → "foo"
    - "name 'users' is not defined" → "users"
    """
    patterns = [
        # Module names: "No module named 'psycopg2'" or similar
        r'No module named [\'"]([^\'"]+)[\'"]',  # No module named 'psycopg2'
        # NameError: name 'X' is not defined
        r"name\s+'([^']+)'\s+is not defined",    # name 'users' is not defined
        # Attribute/property patterns - IMPORTANT: get attribute AFTER "has no attribute"
        r"has no attribute\s+'([^']+)'",         # has no attribute 'foo'
        r'has no attribute\s+["\']?(\w+)["\']?', # has no attribute foo
        r"object has no attribute\s+'([^']+)'",  # object has no attribute 'X'
        r'property\s+["\'](\w+)["\']',           # property "name"
        # Variable patterns
        r'([\w.]+)\s+is not defined',            # varName is not defined
        r'([\w.]+)\s+is not a function',         # funcName is not a function
        r'module\s+["\'](\w+)["\']',             # module "name"
    ]

    for pattern in patterns:
        match = re.search(pattern, error_message, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def _extract_error_code(error_message: str) -> Optional[str]:
    """Extract error code if present (e.g., E0001, [Errno 2])."""
    patterns = [
        r'\[Errno\s+(\d+)\]',  # [Errno 2]
        r'\(([A-Z]\d+)\)',      # (E0001)
        r'code:\s*([A-Z]\d+)',  # code: E0001
    ]

    for pattern in patterns:
        match = re.search(pattern, error_message)
        if match:
            return match.group(1)

    return None


def _hint_language(error_message: str) -> Optional[str]:
    """Infer language from error message format."""
    msg_lower = error_message.lower()

    # Python markers (check first - strongest indicators)
    if any(x in msg_lower for x in ['traceback', 'file "', 'module named', 'indentationerror']):
        return "python"

    # Python exceptions are strong indicators
    python_exceptions = ['attributeerror', 'keyerror', 'indexerror', 'valueerror', 'nameerror']
    if any(x in msg_lower for x in python_exceptions):
        return "python"

    # These could be Python or JavaScript, need more context
    if any(x in msg_lower for x in ['typeerror:', 'syntaxerror:']):
        if '.py:' in msg_lower or 'File "' in error_message:
            return "python"
        if any(x in msg_lower for x in ['cannot read', 'is not a function', 'at ']):
            return "javascript"

    # JavaScript/TypeScript markers
    if any(x in msg_lower for x in ['referenceerror:', 'cannot read', '.js:', '.jsx:', '.ts:', '.tsx:']):
        return "javascript"

    # Java markers
    if 'at ' in msg_lower and ('.java:' in msg_lower or 'exception' in msg_lower):
        return "java"

    return None


def _extract_final_exception_line(lines: list) -> str:
    """
    Extract the final exception line from a Python traceback.

    In a Python traceback, the actual error is the last meaningful line.

    Args:
        lines: All lines from the traceback

    Returns:
        The final exception line (e.g., "ModuleNotFoundError: No module named 'psycopg2'")
    """
    # Find and return the last non-empty line that looks like an exception
    for line in reversed(lines):
        line = line.strip()
        if line and not line.startswith('File ') and not line.startswith('Traceback'):
            # This is likely the exception line
            return line

    # Fallback: return the last non-empty line
    for line in reversed(lines):
        if line.strip():
            return line.strip()

    return ""
