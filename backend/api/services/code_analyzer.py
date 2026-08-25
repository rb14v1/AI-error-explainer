"""
Code Analyzer

Extracts structure from code snippets:
- Python: Uses ast module to parse variables, functions, scope
- JavaScript/TypeScript: Regex-based structural analysis
"""

import ast
import re
from typing import NamedTuple, Optional, Dict, List, Set


class CodeAnalysis(NamedTuple):
    """Analyzed code structure."""
    language: str
    variables: Set[str]  # All variable names declared
    functions: Set[str]  # All function names
    nullish_checks: List[str]  # Lines with null/undefined checks
    array_methods: Set[str]  # Array methods used (.map, .filter, etc)
    property_accesses: List[str]  # obj.prop patterns found
    has_type_hints: bool
    async_patterns: List[str]  # async/await or Promise patterns


def analyze_code(code_snippet: Optional[str], language_hint: Optional[str] = None) -> CodeAnalysis:
    """
    Analyze code snippet for structure.

    Args:
        code_snippet: Code string to analyze
        language_hint: Hint about language ('python', 'javascript', etc)

    Returns:
        CodeAnalysis with extracted structure
    """
    if not code_snippet:
        return CodeAnalysis(
            language='unknown',
            variables=set(),
            functions=set(),
            nullish_checks=[],
            array_methods=set(),
            property_accesses=[],
            has_type_hints=False,
            async_patterns=[]
        )

    # Detect language
    language = language_hint or _detect_language(code_snippet)

    # Analyze based on language
    if language == 'python':
        return _analyze_python(code_snippet)
    else:  # javascript, typescript, unknown -> use structural analysis
        return _analyze_javascript(code_snippet)


def _detect_language(code: str) -> str:
    """Detect language from code patterns."""
    code_lower = code.lower()

    if 'def ' in code or 'import ' in code or 'class ' in code or code.startswith('#'):
        return 'python'

    if any(x in code for x in ['const ', 'let ', 'var ', 'function ', '=>', 'async ', 'await']):
        return 'javascript'

    return 'unknown'


def _analyze_python(code: str) -> CodeAnalysis:
    """Analyze Python code using ast module."""
    variables = set()
    functions = set()
    nullish_checks = []
    array_methods = set()
    property_accesses = []
    has_type_hints = False
    async_patterns = []

    try:
        tree = ast.parse(code)

        class Visitor(ast.NodeVisitor):
            def visit_Name(self, node):
                # Extract variable names
                if isinstance(node.ctx, (ast.Store, ast.Load)):
                    variables.add(node.id)

            def visit_FunctionDef(self, node):
                functions.add(node.name)
                # Check for type hints
                nonlocal has_type_hints
                if node.returns or node.args.args:
                    if any(arg.annotation for arg in node.args.args):
                        has_type_hints = True
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                functions.add(node.name)
                async_patterns.append(f'async def {node.name}')
                self.generic_visit(node)

            def visit_If(self, node):
                # Check for None/null checks
                source = ast.get_source_segment(code, node)
                if source and any(x in source for x in ['is None', 'is not None', 'if not', '!=']):
                    nullish_checks.append(source[:80])
                self.generic_visit(node)

            def visit_Attribute(self, node):
                # Extract property accesses
                source = ast.get_source_segment(code, node)
                if source:
                    property_accesses.append(source)
                self.generic_visit(node)

        Visitor().visit(tree)

    except SyntaxError:
        # If AST parsing fails, fall back to regex analysis
        return _analyze_javascript(code)

    return CodeAnalysis(
        language='python',
        variables=variables,
        functions=functions,
        nullish_checks=nullish_checks,
        array_methods=set(),
        property_accesses=property_accesses,
        has_type_hints=has_type_hints,
        async_patterns=async_patterns
    )


def _analyze_javascript(code: str) -> CodeAnalysis:
    """Analyze JavaScript/TypeScript code using regex patterns."""
    variables = set()
    functions = set()
    nullish_checks = []
    array_methods = set()
    property_accesses = []
    has_type_hints = False
    async_patterns = []

    if not code:
        return CodeAnalysis(
            language='javascript',
            variables=variables,
            functions=functions,
            nullish_checks=nullish_checks,
            array_methods=array_methods,
            property_accesses=property_accesses,
            has_type_hints=has_type_hints,
            async_patterns=async_patterns
        )

    # Variable declarations (const, let, var)
    for match in re.finditer(r'(?:const|let|var)\s+(\w+)', code):
        variables.add(match.group(1))

    # Function parameters (function params and arrow function params)
    for match in re.finditer(r'\{\s*([^}]+)\s*\}|\(\s*([^)]+)\s*\)\s*=>', code):
        params_str = match.group(1) or match.group(2)
        if params_str:
            # Split by comma and extract parameter names
            for param in params_str.split(','):
                param = param.strip()
                # Handle destructuring { name } and type hints : Type
                param_name = re.match(r'(\w+)', param)
                if param_name:
                    variables.add(param_name.group(1))

    # Function declarations
    for match in re.finditer(r'(?:function\s+(\w+)|(\w+)\s*=\s*(?:async\s*)?\()', code):
        name = match.group(1) or match.group(2)
        if name:
            functions.add(name)

    # Function definitions
    for match in re.finditer(r'(?:async\s+)?function\s+(\w+)', code):
        functions.add(match.group(1))

    # Arrow functions
    for match in re.finditer(r'(\w+)\s*=\s*(?:async\s*)?\(', code):
        functions.add(match.group(1))

    # Nullish checks (?.  ||  ?? if not if null checks)
    nullish_patterns = [
        r'[?.][\w]+',  # optional chaining ?.
        r'\|\|',       # ||
        r'\?\?',       # ??
        r'if\s*\(\s*\w+\s*\)',  # if (var)
        r'if\s*\(\s*!\w+\s*\)',  # if (!var)
    ]
    for pattern in nullish_patterns:
        for match in re.finditer(pattern, code):
            nullish_checks.append(match.group(0))

    # Array methods
    for method in ['map', 'filter', 'reduce', 'forEach', 'find', 'some', 'every']:
        if f'.{method}(' in code:
            array_methods.add(method)

    # Property accesses
    for match in re.finditer(r'(\w+)\.(\w+)', code):
        property_accesses.append(f"{match.group(1)}.{match.group(2)}")

    # Type hints (TypeScript)
    if any(x in code for x in [': ', '? ', '<', '>']):
        has_type_hints = True

    # Async patterns
    if 'async' in code:
        async_patterns.append('async/await used')
    if 'Promise' in code or '.then(' in code:
        async_patterns.append('Promise used')

    return CodeAnalysis(
        language='javascript',
        variables=variables,
        functions=functions,
        nullish_checks=list(set(nullish_checks)),
        array_methods=array_methods,
        property_accesses=list(set(property_accesses)),
        has_type_hints=has_type_hints,
        async_patterns=async_patterns
    )
