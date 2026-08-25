"""
Error Explainer Agent Service

The Error Explainer Agent is the core analysis engine for the AI Error Explainer application.

Agent Responsibilities:
1. Error Parsing — Extract error components
2. Stack Trace Parsing — Parse frames and identify user code
3. Code Analysis — Extract code structure
4. Evidence Building — Correlate error, stack, and code
5. Diagnosis Generation — Create contextual explanations and fixes
6. Confidence Scoring — Evidence-based confidence calculation
7. Prevention Tips — Formulate actionable prevention strategies

This is a LOCAL DETERMINISTIC agent with no external API dependencies.
"""

from typing import Optional
from .error_parser import parse_error
from .stack_trace_parser import parse_stack_trace
from .code_analyzer import analyze_code
from .evidence_builder import build_evidence
from .diagnostic_engine import generate_diagnosis
from .confidence_scorer import score_confidence
from .error_patterns import classify_error
from .error_fixes import get_fixes


class ErrorExplainerAgent:
    """
    Single Error Explainer Agent orchestrating an evidence-based analysis pipeline.

    Pipeline stages:
    1. Error Parser → extract error components
    2. Stack Trace Parser → identify frames and user code
    3. Code Analyzer → extract code structure (Python AST, JS structural)
    4. Evidence Builder → correlate all three data sources
    5. Diagnostic Engine → generate contextual diagnosis
    6. Confidence Scorer → evidence-based confidence calculation
    7. Prevention Tips Generator → actionable prevention strategies

    This is a LOCAL DETERMINISTIC implementation with NO external API calls.
    """

    def analyze(
        self,
        error_message: str,
        stack_trace: Optional[str] = None,
        code_snippet: Optional[str] = None,
        language: Optional[str] = None
    ) -> dict:
        """
        Analyze an error through evidence-based pipeline.

        Args:
            error_message: The exact error message or exception string
            stack_trace: Optional stack trace information
            code_snippet: Optional surrounding code snippet
            language: Optional programming language identifier

        Returns:
            dict: Structured response matching api_schema.json
        """
        # Pipeline Stage 1: Error Parser
        parsed_error = parse_error(error_message)

        # Pipeline Stage 2: Stack Trace Parser
        language_hint = language or parsed_error.language_hint
        parsed_stack = parse_stack_trace(stack_trace, language_hint)

        # Pipeline Stage 3: Code Analyzer
        code_analysis = analyze_code(code_snippet, language_hint)

        # Pipeline Stage 4: Evidence Builder
        evidence_report = build_evidence(parsed_error, parsed_stack, code_analysis)

        # Get fallback fixes for diagnosis engine
        error_type, _ = classify_error(error_message)
        fallback_fixes = get_fixes(error_type, language)

        # Check if error information is insufficient
        if not self._is_sufficient_error_info(parsed_error, error_message):
            return {
                "status": "success",
                "error_type": "Insufficient Error Information",
                "what_happened": "The provided error message is too vague to analyze.",
                "why_it_happened": "Error messages like 'Something went wrong' don't contain enough information for diagnosis.",
                "how_to_fix_it": [
                    "Provide the actual error message from your console or logs",
                    "Include the full stack trace if available",
                    "Include any relevant code snippet",
                    "Include your programming language"
                ],
                "corrected_code": "# Include actual error output, e.g.:\n# ModuleNotFoundError: No module named 'psycopg2'\n# or\n# TypeError: Cannot read property 'name' of undefined",
                "prevention_tips": [
                    "Copy the full error message, not just a summary",
                    "Include the complete stack trace",
                    "Test error analysis with specific, real errors"
                ],
                "severity": "Low",
                "confidence": 0.0,
                "failure_location": None
            }

        # Pipeline Stage 5: Diagnostic Engine
        diagnosis = generate_diagnosis(parsed_error, evidence_report, code_snippet, fallback_fixes)

        # Pipeline Stage 6: Confidence Scorer
        confidence_breakdown = score_confidence(
            parsed_error, evidence_report, parsed_stack, code_analysis
        )

        # Pipeline Stage 7: Prevention Tips
        prevention_tips = self._generate_prevention_tips(
            parsed_error, code_analysis, fallback_fixes
        )

        # Determine severity
        severity = self._determine_severity(parsed_error, confidence_breakdown)

        return {
            "status": "success",
            "error_type": parsed_error.error_type,
            "what_happened": diagnosis.what_happened,
            "why_it_happened": diagnosis.why_it_happened,
            "how_to_fix_it": diagnosis.how_to_fix_it,
            "corrected_code": diagnosis.corrected_code,
            "prevention_tips": prevention_tips,
            "severity": severity,
            "confidence": round(confidence_breakdown.overall, 2),
            "failure_location": diagnosis.failure_location
        }

    def _is_sufficient_error_info(self, parsed_error, original_error: str) -> bool:
        """Check if error information is sufficient for analysis."""
        error_type = parsed_error.error_type
        error_lower = error_type.lower()

        # Vague error types that are too generic
        vague_errors = {
            "unknown error", "error", "something went wrong",
            "failed", "problem", "issue", "oops", "sorry",
        }

        if error_type in vague_errors or error_lower in vague_errors:
            return False

        # Check if it's too short and generic
        if len(error_type) < 3:
            return False

        # Check for actual error structure (TypeErroror: message, ModuleNotFoundError, etc)
        if ":" not in original_error and not any(x in error_lower for x in [
            "error", "exception", "fault", "failed", "traceback"
        ]):
            return False

        return True

    def _determine_severity(self, parsed_error, confidence_breakdown) -> str:
        """Determine error severity level."""
        error_type_lower = parsed_error.error_type.lower()
        msg_lower = parsed_error.full_message.lower()

        if "critical" in error_type_lower or "syntaxerror" in error_type_lower:
            return "Critical"

        if "undefined" in error_type_lower or "null" in error_type_lower:
            return "High"

        if any(x in error_type_lower for x in ["error", "exception", "failure"]):
            return "High" if confidence_breakdown.overall > 0.7 else "Medium"

        if confidence_breakdown.overall < 0.4:
            return "Low"

        return "Medium"

    def _generate_prevention_tips(self, parsed_error, code_analysis, fallback_fixes) -> list:
        """Generate prevention tips based on error type, language, and cause."""
        # Use fallback tips if available, but supplement with language-specific advice
        base_tips = []
        if fallback_fixes and 'prevention_tips' in fallback_fixes:
            base_tips = fallback_fixes['prevention_tips']

        tips = []
        error_msg_lower = parsed_error.full_message.lower()
        error_type_lower = parsed_error.error_type.lower()
        language = code_analysis.language or parsed_error.language_hint or "unknown"

        # ModuleNotFoundError / ImportError - Python specific
        if "modulenotfound" in error_type_lower or "importerror" in error_type_lower:
            if language == 'python' or 'python' in error_msg_lower:
                tips.append("Install the required package using pip: pip install <package_name>")
                tips.append("Use a requirements.txt file to manage dependencies")
                tips.append("Ensure your virtual environment is activated")
                tips.append("Check that package names are spelled correctly (case-sensitive)")
            return tips

        # NameError - Python specific
        if "nameerror" in error_type_lower:
            if language == 'python' or 'python' in error_msg_lower:
                tips.append("Declare variables before using them")
                tips.append("Use consistent variable names (Python is case-sensitive)")
                tips.append("Check for typos in variable names")
                tips.append("Use a linter like pylint or flake8 to catch undefined names early")
            return tips

        # AttributeError - Python specific
        if "attributeerror" in error_type_lower:
            if language == 'python' or 'python' in error_msg_lower:
                tips.append("Check the object type and available attributes")
                tips.append("Use hasattr() or getattr() with defaults")
                tips.append("Add type hints to make expected types explicit")
                tips.append("Use __init__ to initialize all attributes")
            return tips

        # KeyError - Python specific
        if "keyerror" in error_type_lower:
            if language == 'python' or 'python' in error_msg_lower:
                tips.append("Use dict.get() with a default value instead of direct access")
                tips.append("Check if keys exist before accessing: if key in dict")
                tips.append("Use defaultdict from collections for automatic defaults")
                tips.append("Validate and document required dictionary keys")
            return tips

        # IndexError - Python specific
        if "indexerror" in error_type_lower:
            if language == 'python' or 'python' in error_msg_lower:
                tips.append("Check list length before accessing: if len(list) > index")
                tips.append("Use enumerate() for safe iteration")
                tips.append("Add bounds checking or use try-except")
                tips.append("Initialize lists with expected values, not empty")
            return tips

        # SyntaxError / IndentationError - Python specific
        if "syntax" in error_type_lower or "indentation" in error_type_lower:
            if language == 'python' or 'python' in error_msg_lower:
                tips.append("Use consistent indentation (4 spaces per level)")
                tips.append("Check for matching parentheses, brackets, and braces")
                tips.append("Use an IDE with Python syntax checking")
                tips.append("Enable linters like pylint or flake8")
            return tips

        # TypeError - undefined/null
        if "undefined" in error_msg_lower or "null" in error_msg_lower:
            if language == 'javascript':
                tips.append("Enable strictNullChecks in tsconfig.json (TypeScript)")
                tips.append("Use optional chaining (?.) for safe property access")
                tips.append("Use nullish coalescing (??) for default values")
                tips.append("Add null/undefined checks before accessing properties")
            elif language == 'python':
                tips.append("Check for None before using objects: if obj is not None")
                tips.append("Use Optional[] type hints for nullable values")
                tips.append("Use getattr() with defaults for optional attributes")
                tips.append("Initialize variables with appropriate defaults")
            return tips

        # ReferenceError - JavaScript specific (not Python)
        if "referenceerror" in error_type_lower:
            if language == 'javascript':
                tips.append("Declare variables with const, let, or var before using")
                tips.append("Use 'use strict' mode to catch undeclared variables")
                tips.append("Check variable scope and hoisting behavior")
                tips.append("Use ESLint to catch undefined variable errors")
            return tips

        # Use base tips if no specific pattern matched
        if base_tips:
            return base_tips

        # Generic language-specific prevention
        if language == 'python':
            return [
                "Use type hints for better error detection",
                "Use a linter like pylint or flake8",
                "Write unit tests to catch errors early",
                "Add docstrings to document expected types and behavior"
            ]
        elif language == 'javascript':
            return [
                "Use TypeScript for compile-time type checking",
                "Use ESLint to catch errors before runtime",
                "Enable strict null checking",
                "Write unit tests with Jest or Mocha"
            ]
        else:
            return [
                "Add defensive checks for all inputs",
                "Use type checking/linting tools available in your language",
                "Write comprehensive tests",
                "Review error handling patterns in your framework"
            ]
