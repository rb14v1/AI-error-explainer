"""
Error fixes and prevention strategies database.

Maps error types to suggested fixes and prevention tips.
"""

from typing import NamedTuple


class FixStrategy(NamedTuple):
    """Definition of fixes and prevention tips for an error type."""
    error_pattern: str
    language: str
    what_happened: str
    why_it_happened: str
    how_to_fix_it: list[str]
    corrected_code: str
    prevention_tips: list[str]


FIX_STRATEGIES = {
    "TypeError: Undefined Property Access": {
        "javascript": FixStrategy(
            error_pattern="TypeError: Undefined Property Access",
            language="JavaScript",
            what_happened="The code tried to access a property on a value that is undefined or null, which does not have any properties.",
            why_it_happened="A variable was not initialized, a function did not return a value, or an async operation had not completed when the code tried to use it.",
            how_to_fix_it=[
                "Use optional chaining (?.operator) to safely access properties: obj?.property",
                "Add a null/undefined check before accessing properties: if (obj) { obj.property }",
                "Provide a default value using the nullish coalescing operator (??): obj?.property ?? defaultValue",
                "Ensure variables are initialized before use",
                "Verify that async operations have completed before accessing their results"
            ],
            corrected_code="const value = user?.profile?.name ?? 'Unknown';\nconst items = array?.map(item => item.id) ?? [];",
            prevention_tips=[
                "Enable TypeScript strict null checks: 'strictNullChecks: true' in tsconfig.json",
                "Use linters to detect potential null/undefined issues before runtime",
                "Always initialize variables with default values",
                "Use type guards and type narrowing in TypeScript"
            ]
        ),
        "typescript": FixStrategy(
            error_pattern="TypeError: Undefined Property Access",
            language="TypeScript",
            what_happened="The code tried to access a property on a value that is undefined or null.",
            why_it_happened="Type safety was not properly enforced, or async data was accessed before loading completed.",
            how_to_fix_it=[
                "Enable strictNullChecks in tsconfig.json for compile-time error detection",
                "Add type annotations to function parameters and return types",
                "Use optional chaining: obj?.property",
                "Add null checks or use type guards",
                "Use strict type assertions in TypeScript"
            ],
            corrected_code="interface User { profile?: { name: string } }\nconst name: string = user?.profile?.name ?? 'Unknown';",
            prevention_tips=[
                "Always enable 'strictNullChecks' in TypeScript configuration",
                "Use NonNull assertions (!) only when 100% certain a value exists",
                "Define interfaces and types for all data structures",
                "Use strict compiler options to catch errors at compile time"
            ]
        ),
        "python": FixStrategy(
            error_pattern="TypeError: Undefined Property Access",
            language="Python",
            what_happened="The code tried to access an attribute on a None or undefined object.",
            why_it_happened="A function returned None, a variable was not initialized, or an optional dependency was missing.",
            how_to_fix_it=[
                "Check if the object is None before accessing attributes: if obj is not None: obj.property",
                "Use getattr() with a default value: getattr(obj, 'property', default_value)",
                "Use try-except to catch AttributeError exceptions",
                "Initialize objects properly before use",
                "Add type hints to make expected types explicit"
            ],
            corrected_code="user = get_user()\nname = user.name if user is not None else 'Unknown'\nvalue = getattr(obj, 'property', None)",
            prevention_tips=[
                "Use type hints: def func() -> Optional[User]",
                "Return explicit None or use Optional types",
                "Use linters like mypy to catch type errors",
                "Always check for None before using objects"
            ]
        ),
    },
    "TypeError: Cannot Call Non-Function": {
        "javascript": FixStrategy(
            error_pattern="TypeError: Cannot Call Non-Function",
            language="JavaScript",
            what_happened="The code tried to call something as a function, but it is not a function (it might be a value, string, number, etc.).",
            why_it_happened="A variable was reassigned to a non-function value, or a property was accessed incorrectly.",
            how_to_fix_it=[
                "Verify that the variable is actually a function before calling it",
                "Check for typos in the function name",
                "Use typeof to check: if (typeof myFunc === 'function') myFunc()",
                "Ensure the variable has not been reassigned to a different value",
                "Check that the correct method/function is being called"
            ],
            corrected_code="const myFunc = () => console.log('Hello');\nif (typeof myFunc === 'function') { myFunc(); }",
            prevention_tips=[
                "Use TypeScript to enforce function types at compile time",
                "Keep function names consistent and avoid reassignment",
                "Use arrow functions for callbacks to maintain context",
                "Add type annotations for all function parameters"
            ]
        ),
        "typescript": FixStrategy(
            error_pattern="TypeError: Cannot Call Non-Function",
            language="TypeScript",
            what_happened="Attempted to invoke something that is not a function.",
            why_it_happened="Type mismatch or variable reassignment to a non-callable type.",
            how_to_fix_it=[
                "Check the type: verify it has a function signature",
                "Use TypeScript type checking: (x: (...args: any[]) => any)",
                "Ensure you're calling the right property/method",
                "Check for typos in property access"
            ],
            corrected_code="type Callback = (value: string) => void;\nconst doSomething = (cb: Callback) => cb('test');",
            prevention_tips=[
                "Use strict types for callbacks and handlers",
                "Enable 'strict' mode in TypeScript compiler",
                "Define function types explicitly with interface or type alias",
                "Use type guards for optional functions"
            ]
        ),
    },
    "SyntaxError: Invalid Syntax": {
        "javascript": FixStrategy(
            error_pattern="SyntaxError: Invalid Syntax",
            language="JavaScript",
            what_happened="The code contains a syntax error that prevents it from being parsed and executed.",
            why_it_happened="Mismatched parentheses, quotes, braces, or invalid JavaScript syntax.",
            how_to_fix_it=[
                "Check for missing or mismatched parentheses, brackets, or braces",
                "Verify that all strings are properly quoted (use matching quotes)",
                "Check for semicolons at the end of statements (if required by your style)",
                "Look for typos in keywords (function, if, for, etc.)",
                "Use an IDE with syntax highlighting to spot errors"
            ],
            corrected_code="// Wrong: const obj = { key: value }\n// Right: const obj = { key: 'value' };\nconst arr = [1, 2, 3];\nif (true) { console.log('ok'); }",
            prevention_tips=[
                "Use an IDE with built-in syntax checking",
                "Enable a linter like ESLint to catch syntax errors early",
                "Use a formatter like Prettier to auto-format code",
                "Write code carefully and review before running"
            ]
        ),
        "python": FixStrategy(
            error_pattern="SyntaxError: Invalid Syntax",
            language="Python",
            what_happened="The code contains invalid Python syntax.",
            why_it_happened="Incorrect indentation, unclosed strings/parentheses, or invalid Python keywords.",
            how_to_fix_it=[
                "Check indentation (Python is indentation-sensitive)",
                "Verify all parentheses, brackets, and braces are matched",
                "Ensure strings are properly quoted and closed",
                "Check for correct colon usage (after if, for, def, class)",
                "Look for typos in Python keywords"
            ],
            corrected_code="# Wrong: if x = 5\n# Right:\nif x == 5:\n    print('equal')\n\ndef func():\n    return value",
            prevention_tips=[
                "Use consistent indentation (4 spaces per level)",
                "Use an IDE with Python syntax checking",
                "Enable linter tools like pylint or flake8",
                "Test code frequently to catch syntax errors early"
            ]
        ),
    },
    "ReferenceError: Undefined Variable": {
        "javascript": FixStrategy(
            error_pattern="ReferenceError: Undefined Variable",
            language="JavaScript",
            what_happened="The code references a variable that has not been declared or defined.",
            why_it_happened="Variable was not declared with let/const/var, or it was declared in a different scope.",
            how_to_fix_it=[
                "Declare the variable using let, const, or var before using it",
                "Check the spelling of the variable name (case-sensitive)",
                "Verify the variable is defined in the correct scope",
                "Move variable declaration to the correct scope",
                "Use 'use strict' mode to catch undeclared variables"
            ],
            corrected_code="// Wrong: console.log(myVar);\n// Right:\nconst myVar = 'value';\nconsole.log(myVar);\n\nfunction test() {\n  const localVar = 10;\n  return localVar;\n}",
            prevention_tips=[
                "Always declare variables before using them",
                "Use 'const' by default, 'let' when reassignment is needed",
                "Avoid global variables when possible",
                "Use a linter like ESLint to catch undeclared variables"
            ]
        ),
    },
    "AttributeError: Missing Attribute": {
        "python": FixStrategy(
            error_pattern="AttributeError: Missing Attribute",
            language="Python",
            what_happened="The code tried to access an attribute that does not exist on the object.",
            why_it_happened="The object does not have the requested attribute, or the attribute name is misspelled.",
            how_to_fix_it=[
                "Check the spelling of the attribute name (case-sensitive)",
                "Verify the object type has the attribute you're trying to access",
                "Use hasattr() to check if attribute exists: hasattr(obj, 'attr')",
                "Use getattr() with a default value: getattr(obj, 'attr', default)",
                "Check the object's __dict__ or dir(obj) to see available attributes"
            ],
            corrected_code="class User:\n    def __init__(self, name):\n        self.name = name\n\nuser = User('John')\nprint(user.name)  # Correct\nif hasattr(user, 'email'):\n    print(user.email)",
            prevention_tips=[
                "Use __init__ to initialize all attributes",
                "Document all available attributes in docstrings",
                "Use type hints and type checkers like mypy",
                "Use properties and getters for computed attributes"
            ]
        ),
    },
    "KeyError: Missing Dictionary Key": {
        "python": FixStrategy(
            error_pattern="KeyError: Missing Dictionary Key",
            language="Python",
            what_happened="The code tried to access a dictionary key that does not exist.",
            why_it_happened="The key was not added to the dictionary, or the key name is misspelled.",
            how_to_fix_it=[
                "Use dict.get(key) instead of dict[key] to provide a default",
                "Check if key exists first: if key in dict: dict[key]",
                "Use dict.setdefault(key, default) to provide defaults",
                "Verify the key spelling and case",
                "Initialize the dictionary with all expected keys"
            ],
            corrected_code="data = {'name': 'John', 'age': 30}\n# Wrong: print(data['email'])\n# Right:\nprint(data.get('email', 'N/A'))  # Returns 'N/A' if key doesn't exist\nif 'email' in data:\n    print(data['email'])",
            prevention_tips=[
                "Use dict.get() with defaults instead of direct access",
                "Use defaultdict from collections module for missing keys",
                "Document required dictionary keys in function docstrings",
                "Validate input data before accessing dictionary keys"
            ]
        ),
    },
    "IndexError: Array Out of Bounds": {
        "python": FixStrategy(
            error_pattern="IndexError: Array Out of Bounds",
            language="Python",
            what_happened="The code tried to access a list element at an index that does not exist.",
            why_it_happened="Index is negative without proper offset, or the list is shorter than expected.",
            how_to_fix_it=[
                "Check the length of the list: len(mylist)",
                "Verify the index is within bounds: 0 <= index < len(list)",
                "Use try-except to handle IndexError gracefully",
                "Use list[index:index+1] for safe access (returns empty list if out of bounds)",
                "Ensure the list is populated before accessing it"
            ],
            corrected_code="items = [1, 2, 3]\nif len(items) > 0:\n    first = items[0]\n\ntry:\n    value = items[5]\nexcept IndexError:\n    value = None",
            prevention_tips=[
                "Always check list length before accessing elements",
                "Use enumerate() for safe iteration over lists",
                "Use defensive programming with try-except blocks",
                "Initialize lists with expected values, not empty"
            ]
        ),
    },
}


def get_fixes(error_type: str, language: str = None) -> dict:
    """
    Get fix strategy for an error type and language.

    Args:
        error_type: The classified error type
        language: Optional programming language

    Returns:
        Dictionary with fixes, or empty dict if not found
    """
    strategies = FIX_STRATEGIES.get(error_type, {})

    if language and language.lower() in strategies:
        strategy = strategies[language.lower()]
        return {
            "what_happened": strategy.what_happened,
            "why_it_happened": strategy.why_it_happened,
            "how_to_fix_it": strategy.how_to_fix_it,
            "corrected_code": strategy.corrected_code,
            "prevention_tips": strategy.prevention_tips,
        }

    # Try first available language if specific one not found
    for lang_strategies in strategies.values():
        return {
            "what_happened": lang_strategies.what_happened,
            "why_it_happened": lang_strategies.why_it_happened,
            "how_to_fix_it": lang_strategies.how_to_fix_it,
            "corrected_code": lang_strategies.corrected_code,
            "prevention_tips": lang_strategies.prevention_tips,
        }

    return {}
