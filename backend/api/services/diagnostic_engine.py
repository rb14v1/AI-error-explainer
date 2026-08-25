"""
Diagnostic Engine

Generates contextual diagnosis from error, stack trace, code, and evidence.
"""

from typing import Optional, List, NamedTuple
from .error_parser import ParsedError
from .evidence_builder import EvidenceReport


class Diagnosis(NamedTuple):
    """Generated diagnosis."""
    what_happened: str
    why_it_happened: str
    how_to_fix_it: List[str]
    corrected_code: str
    failure_location: Optional[str] = None  # file:line from stack trace


def generate_diagnosis(
    parsed_error: ParsedError,
    evidence_report: EvidenceReport,
    code_snippet: Optional[str] = None,
    fallback_fixes: Optional[dict] = None
) -> Diagnosis:
    """
    Generate contextual diagnosis from evidence.

    Args:
        parsed_error: Parsed error components
        evidence_report: Evidence correlation results
        code_snippet: Original code snippet
        fallback_fixes: Fallback template fixes if dynamic generation insufficient

    Returns:
        Diagnosis with what, why, how, and corrected code
    """
    # Generate what_happened
    what_happened = _generate_what_happened(parsed_error, evidence_report)

    # Generate why_it_happened
    why_it_happened = _generate_why_it_happened(parsed_error, evidence_report)

    # Generate how_to_fix_it
    how_to_fix_it = _generate_how_to_fix_it(parsed_error, evidence_report, fallback_fixes)

    # Generate corrected_code
    corrected_code = _generate_corrected_code(
        parsed_error, evidence_report, code_snippet, fallback_fixes
    )

    # Extract failure location from stack trace if available
    # Use the DEEPEST (last) user frame as it's closest to the actual error
    failure_location = None
    if evidence_report.user_code_frames:
        frame = evidence_report.user_code_frames[-1]  # Last/deepest frame
        if frame.line_number:
            failure_location = f"{frame.file_path}:{frame.line_number}"

    return Diagnosis(
        what_happened=what_happened,
        why_it_happened=why_it_happened,
        how_to_fix_it=how_to_fix_it,
        corrected_code=corrected_code,
        failure_location=failure_location
    )


def _generate_what_happened(parsed_error: ParsedError, evidence_report: EvidenceReport) -> str:
    """Generate simple explanation of what happened using actual error message."""
    error_type = parsed_error.error_type
    symbol = evidence_report.error_symbol
    error_msg = parsed_error.actual_error_line or parsed_error.full_message

    # Use actual error message for more specific explanations
    error_lower = error_msg.lower()

    # ModuleNotFoundError - extract module name from error message
    if "modulenotfound" in error_type.lower() or "no module named" in error_lower:
        if symbol:
            return f"The Python module '{symbol}' is not available in the active environment."
        return "A required Python module is not installed or available."

    # ImportError
    if "importerror" in error_type.lower():
        if symbol:
            return f"Cannot import '{symbol}' - the module, class, or function is not available."
        return "An import failed - a required module or object cannot be found."

    # NameError
    if "nameerror" in error_type.lower():
        if symbol:
            return f"The name '{symbol}' is not defined in the current scope."
        return "A name was used before being defined or declared."

    # AttributeError with specific object/attribute
    if "attributeerror" in error_type.lower():
        if symbol:
            return f"An object does not have the attribute or method named '{symbol}'."
        return "The code tried to access an attribute that doesn't exist on an object."

    # KeyError
    if "keyerror" in error_type.lower():
        if symbol:
            return f"The dictionary does not contain the key '{symbol}'."
        return "The code tried to access a dictionary key that doesn't exist."

    # IndexError
    if "indexerror" in error_type.lower() or "out of range" in error_lower:
        return "The code tried to access a list or sequence element at an invalid index."

    # SyntaxError
    if "syntaxerror" in error_type.lower() or "syntax" in error_lower:
        if "indentation" in error_lower:
            return "The code has incorrect or inconsistent indentation."
        if "was never closed" in error_lower or "unclosed" in error_lower:
            return "A string, parenthesis, bracket, or brace was not properly closed."
        return "The code contains invalid syntax that cannot be parsed."

    # IndentationError
    if "indentation" in error_type.lower():
        return "The code has incorrect or missing indentation (Python is indentation-sensitive)."

    if "undefined" in error_type.lower() or "undefined" in error_lower:
        if symbol:
            return f"The code tried to access '{symbol}' or a property on it, but '{symbol}' was undefined or null."
        return "The code tried to access a property on a value that was undefined or null."

    if "not a function" in error_type.lower():
        if symbol:
            return f"The code tried to call '{symbol}' as a function, but it is not a function."
        return "The code tried to call something as a function, but it is not a function."

    if "zero" in error_type.lower() and "division" in error_type.lower():
        return "The code attempted to divide by zero."

    # Fallback
    return f"An error of type '{error_type}' occurred." if error_type else "An error occurred."


def _generate_why_it_happened(parsed_error: ParsedError, evidence_report: EvidenceReport) -> str:
    """Generate root cause explanation."""
    reasons = []

    # Use evidence to build why
    for evidence in evidence_report.evidence_list:
        if evidence.type == 'null_undefined_error':
            reasons.append("A variable or property was not initialized before use")
        elif evidence.type == 'symbol_in_code':
            reasons.append(f"'{evidence_report.error_symbol}' is declared but may not be initialized")

    # Check for async issues
    if evidence_report.evidence_list:
        for evidence in evidence_report.evidence_list:
            if 'async' in evidence.value.lower():
                reasons.append("An async operation may not have completed when accessed")

    # Check for missing checks
    if ("undefined" in parsed_error.full_message.lower() or "null" in parsed_error.full_message.lower()):
        if not any('nullish' in e.value.lower() for e in evidence_report.evidence_list):
            reasons.append("No null/undefined checks were present before accessing the value")

    # Stack trace context
    if evidence_report.user_code_frames:
        frame = evidence_report.user_code_frames[0]
        reasons.append(f"The error originated at {frame.file_path}:{frame.line_number} in '{frame.function_name}'")

    # Fallback reason
    if not reasons:
        error_lower = parsed_error.full_message.lower()
        if "undefined" in error_lower or "null" in error_lower:
            reasons.append("A variable was undefined or null when accessed")
        elif "not a function" in error_lower:
            reasons.append("A non-function value was called as a function")
        elif "not defined" in error_lower:
            reasons.append("A variable was used before being declared")
        else:
            reasons.append("The error message provides the reason above")

    return " ".join(reasons)


def _generate_how_to_fix_it(
    parsed_error: ParsedError,
    evidence_report: EvidenceReport,
    fallback_fixes: Optional[dict] = None
) -> List[str]:
    """Generate contextual fix steps - language and error specific."""
    fixes: List[str] = []

    error_type = parsed_error.error_type
    error_msg = parsed_error.actual_error_line or parsed_error.full_message
    error_msg_lower = error_msg.lower()
    symbol = evidence_report.error_symbol

    # ModuleNotFoundError / ImportError - extract module name
    if "modulenotfound" in error_type.lower() or "no module named" in error_msg_lower:
        if symbol:
            fixes = [
                f"Install the missing module: pip install {symbol}",
                f"Check if {symbol} is correctly spelled (case-sensitive)",
                "Ensure your virtual environment is activated",
                f"Update requirements.txt if using: pip install --upgrade {symbol}",
            ]
        else:
            fixes = [
                "Install the missing Python module using pip",
                "Check the module name is spelled correctly",
                "Ensure your virtual environment is activated",
                "Verify the module is available for your Python version"
            ]
        return fixes

    # ImportError
    if "importerror" in error_type.lower():
        if symbol:
            fixes = [
                f"Check if {symbol} is available in the module",
                f"Verify the import statement: from module import {symbol}",
                f"Install the package containing {symbol}",
                "Check for circular imports"
            ]
        return fixes

    # NameError - variable not defined
    if "nameerror" in error_type.lower():
        if symbol:
            fixes = [
                f"Declare the variable before use: {symbol} = ...",
                f"Check spelling of '{symbol}' (Python is case-sensitive)",
                f"Ensure '{symbol}' is in the correct scope",
                f"Check for typos in the variable name"
            ]
        return fixes

    # AttributeError
    if "attributeerror" in error_type.lower():
        if symbol:
            fixes = [
                f"Verify the object has attribute '{symbol}'",
                f"Use hasattr() to check: if hasattr(obj, '{symbol}')",
                f"Use getattr() with a default: getattr(obj, '{symbol}', default)",
                "Check the object type and available methods"
            ]
        else:
            fixes = [
                "Verify the object has the requested attribute",
                "Check the object type and available methods",
                "Use getattr() with a default value"
            ]
        return fixes

    # KeyError - dictionary key missing
    if "keyerror" in error_type.lower():
        if symbol:
            fixes = [
                f"Use dict.get('{symbol}', default) instead of dict['{symbol}']",
                f"Check if '{symbol}' exists: if '{symbol}' in dict",
                f"Initialize dictionary with key '{symbol}'",
                "Validate dictionary structure before access"
            ]
        else:
            fixes = [
                "Use dict.get(key, default) instead of dict[key]",
                "Check if the key exists before accessing",
                "Initialize all required dictionary keys"
            ]
        return fixes

    # IndexError - list index out of bounds
    if "indexerror" in error_type.lower() or "out of range" in error_msg_lower:
        fixes = [
            "Check list length: if len(list) > index",
            "Add bounds checking before access",
            "Use try-except to handle IndexError gracefully",
            "Ensure list is populated with expected values"
        ]
        return fixes

    # SyntaxError / IndentationError
    if "syntaxerror" in error_type.lower() or "indentation" in error_type.lower():
        if "was never closed" in error_msg_lower or "unclosed" in error_msg_lower:
            fixes = [
                "Check for matching parentheses, brackets, and braces",
                "Ensure all strings are properly quoted",
                "Look for unclosed strings or expressions"
            ]
        elif "indentation" in error_msg_lower:
            fixes = [
                "Use consistent indentation (4 spaces per level)",
                "Check indentation after colons (:)",
                "Avoid mixing tabs and spaces"
            ]
        else:
            fixes = [
                "Check for typos in keywords",
                "Verify all strings are quoted correctly",
                "Check for missing colons after statements"
            ]
        return fixes

    # Use fallback fixes if available
    if fallback_fixes and 'how_to_fix_it' in fallback_fixes:
        return fallback_fixes['how_to_fix_it']

    # Generate contextual fixes for remaining cases
    if "undefined" in error_msg_lower or "null" in error_msg_lower:
        fixes = [
            f"Add a null/undefined check before accessing {symbol or 'the variable'}",
            f"Use optional chaining (?.{symbol or 'property'}) if supported",
            f"Provide a default value using nullish coalescing (??)",
            "Ensure the variable is initialized before use",
            "Check parent component/function is providing the value correctly"
        ]

    elif "not a function" in error_msg_lower:
        fixes = [
            f"Verify that {symbol or 'the variable'} is actually a function",
            f"Check for typos in the function name '{symbol or 'name'}'",
            f"Use typeof to check: if (typeof {symbol or 'func'} === 'function')",
            "Ensure the function/method hasn't been reassigned to another value"
        ]

    elif "not defined" in error_msg_lower:
        fixes = [
            f"Declare '{symbol or 'the variable'}' with let, const, or var",
            f"Check the spelling and case of '{symbol or 'the variable'}'",
            "Move the declaration to the correct scope",
            "Use 'use strict' to catch undeclared variables"
        ]

    elif "syntax" in error_msg_lower:
        fixes = [
            "Check for matching parentheses, brackets, and braces",
            "Verify all strings are properly quoted",
            "Look for typos in keywords (function, if, for, etc.)",
            "Use an IDE with syntax highlighting or a linter"
        ]

    elif "attribute" in error_msg_lower:
        fixes = [
            f"Check if the object has attribute '{symbol}'",
            f"Use getattr(obj, '{symbol}', default_value) to provide a default",
            "Verify the object type is what you expect",
            "Check the spelling of the attribute name"
        ]

    elif "key" in error_msg_lower:
        fixes = [
            f"Use dict.get('{symbol}', default) instead of dict['{symbol}']",
            f"Check if '{symbol}' exists before accessing: if '{symbol}' in dict",
            "Initialize the dictionary with all expected keys",
            "Use defaultdict to handle missing keys automatically"
        ]

    elif "index" in error_msg_lower:
        fixes = [
            "Check the length of the list before accessing elements",
            "Verify the index is within bounds (0 <= index < len(list))",
            "Use try-except to handle IndexError gracefully",
            "Use list comprehension with conditional to filter safely"
        ]

    # Add evidence-informed fixes
    if evidence_report.user_code_frames:
        frame = evidence_report.user_code_frames[0]
        fixes.insert(0, f"Review the code at {frame.file_path}:{frame.line_number}")

    # Fallback
    if not fixes:
        fixes = [
            "Read the error message carefully",
            "Check the stack trace for the error location",
            "Review the code at that location",
            "Search documentation for this error type",
            "Add defensive checks to prevent this error"
        ]

    return fixes


def _generate_corrected_code(
    parsed_error: ParsedError,
    evidence_report: EvidenceReport,
    code_snippet: Optional[str] = None,
    fallback_fixes: Optional[dict] = None
) -> str:
    """Generate corrected code example - use provided code when possible."""
    symbol = evidence_report.error_symbol
    error_msg = parsed_error.actual_error_line or parsed_error.full_message
    error_msg_lower = error_msg.lower()

    # For ModuleNotFoundError, show import fix
    if "modulenotfound" in parsed_error.error_type.lower() or "no module named" in error_msg_lower:
        if symbol:
            return f"# Install the module:\n# pip install {symbol}\n\n# Then use it:\nimport {symbol}"
        return "# pip install <module_name>\n# Then: import <module_name>"

    # For NameError, suggest declaration
    if "nameerror" in parsed_error.error_type.lower():
        if symbol:
            return f"# Declare before use:\n{symbol} = None  # or assign a value\n# Then use it:\nprint({symbol})"
        return "# Declare variable before use:\nvariable_name = 'value'\nprint(variable_name)"

    # For AttributeError, suggest getattr
    if "attributeerror" in parsed_error.error_type.lower():
        if symbol:
            return f"# Option 1 - Check with hasattr:\nif hasattr(obj, '{symbol}'):\n    value = obj.{symbol}\n\n# Option 2 - Use getattr with default:\nvalue = getattr(obj, '{symbol}', None)"
        return "# Use getattr with a default:\nvalue = getattr(obj, 'attribute_name', default_value)"

    # For KeyError, suggest dict.get()
    if "keyerror" in parsed_error.error_type.lower():
        if symbol:
            return f"# Use dict.get() with default:\nvalue = my_dict.get('{symbol}', default_value)\n\n# Or check first:\nif '{symbol}' in my_dict:\n    value = my_dict['{symbol}']"
        return "# Use dict.get() with default:\nvalue = my_dict.get('key', default_value)"

    # For IndexError
    if "indexerror" in parsed_error.error_type.lower():
        return "# Check length before accessing:\nif len(my_list) > index:\n    value = my_list[index]\nelse:\n    value = None"

    # For SyntaxError/IndentationError with code snippet
    if code_snippet and ("syntax" in error_msg_lower or "indentation" in error_msg_lower):
        return f"# Your code (with proper indentation/syntax):\n{code_snippet}"

    # Use fallback if available
    if fallback_fixes and 'corrected_code' in fallback_fixes:
        return fallback_fixes['corrected_code']

    # If we have code snippet but no specific error match, offer it back
    if code_snippet and len(code_snippet) < 500:
        return f"# Corrected code:\n{code_snippet}"

    # Generic examples
    if "undefined" in error_msg_lower or "null" in error_msg_lower:
        return "// Check for null/undefined:\nif (value !== null && value !== undefined) {\n  // Use value safely\n}\n\n// Or use optional chaining:\nconst result = obj?.property?.method();"

    if "not a function" in error_msg_lower:
        return "// Check type before calling:\nif (typeof myVar === 'function') {\n  myVar();\n}"

    if "not defined" in error_msg_lower:
        return "// Declare before use:\nconst myVar = 'value';\nconsole.log(myVar);"

    return "# Review the error location in your code and apply the fix suggestions above"
