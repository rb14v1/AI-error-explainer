"""
Confidence Scorer

Calculates evidence-based confidence scores.
Confidence reflects how well we understand the error based on available evidence.
"""

from typing import NamedTuple
from .error_parser import ParsedError
from .evidence_builder import EvidenceReport
from .stack_trace_parser import ParsedStackTrace
from .code_analyzer import CodeAnalysis


class ConfidenceBreakdown(NamedTuple):
    """Confidence calculation breakdown."""
    overall: float  # 0.0-1.0
    pattern_match: float  # How well error matches known patterns
    evidence_richness: float  # How much evidence we have
    correlation_strength: float  # How well error+stack+code correlate
    justification: str


def score_confidence(
    parsed_error: ParsedError,
    evidence_report: EvidenceReport,
    parsed_stack: ParsedStackTrace,
    code_analysis: CodeAnalysis
) -> ConfidenceBreakdown:
    """
    Score confidence based on evidence quality and richness.

    Args:
        parsed_error: Parsed error components
        evidence_report: Evidence analysis
        parsed_stack: Parsed stack trace
        code_analysis: Code analysis

    Returns:
        ConfidenceBreakdown with overall score and justification
    """
    # Component scores (0.0-1.0)
    pattern_score = _score_pattern_match(parsed_error)
    evidence_score = _score_evidence_richness(evidence_report, code_analysis)
    correlation_score = _score_correlation(evidence_report, parsed_stack, code_analysis)

    # For explicit Python exceptions with messages, high pattern score is strong indicator
    # Give pattern matching more weight (50%) when it's a recognized exception
    error_lower = parsed_error.error_type.lower()
    python_exceptions = {'modulenotfound', 'importerror', 'nameerror', 'typeerror', 'attributeerror', 'keyerror', 'indexerror', 'valueerror', 'syntaxerror', 'indentationerror'}

    if any(exc in error_lower for exc in python_exceptions):
        # For recognized Python exceptions, pattern match is the strongest signal
        # Explicit exception + message = high confidence
        if pattern_score >= 0.90:
            # Explicit Python exception with message, trust the pattern match heavily
            overall = min(0.95, pattern_score * 0.88 + max(0, evidence_score - 0.3) * 0.12)
        else:
            # Pattern match, evidence (50%), correlation (20%)
            overall = (pattern_score * 0.5) + (evidence_score * 0.3) + (correlation_score * 0.2)
    else:
        # Weight: pattern (30%), evidence (40%), correlation (30%)
        overall = (pattern_score * 0.3) + (evidence_score * 0.4) + (correlation_score * 0.3)

    # Penalty for conflicts
    if evidence_report.conflicts:
        conflict_penalty = len(evidence_report.conflicts) * 0.05
        overall = max(0.0, overall - conflict_penalty)

    # Penalty for major gaps (but not as severe as before)
    if evidence_report.gaps:
        gap_penalty = len(evidence_report.gaps) * 0.02
        overall = max(0.0, overall - gap_penalty)

    overall = min(1.0, max(0.0, overall))

    # Generate justification
    justification = _generate_justification(
        pattern_score, evidence_score, correlation_score,
        evidence_report, parsed_error
    )

    return ConfidenceBreakdown(
        overall=overall,
        pattern_match=pattern_score,
        evidence_richness=evidence_score,
        correlation_strength=correlation_score,
        justification=justification
    )


def _score_pattern_match(parsed_error: ParsedError) -> float:
    """Score how well error matches known patterns (0.0-1.0)."""
    error_msg = parsed_error.full_message
    error_type = parsed_error.error_type
    error_lower = error_type.lower()

    # Recognized Python exception types (high confidence)
    python_exceptions = {
        'modulenotfound', 'importerror', 'nameerror', 'typeerror',
        'attributeerror', 'keyerror', 'indexerror', 'valueerror',
        'syntaxerror', 'indentationerror', 'zerodeivisionerror',
        'recursionerror', 'filenotfounderror', 'ioerror',
    }

    # Recognized JS exception types (high confidence)
    js_exceptions = {
        'typeerror', 'referenceerror', 'syntaxerror', 'rangeerror',
        'urierror', 'eval error',
    }

    # Known full patterns
    known_patterns = [
        "TypeError: Undefined Property Access",
        "TypeError: Cannot Call Non-Function",
        "SyntaxError: Invalid Syntax",
        "ReferenceError: Undefined Variable",
        "AttributeError: Missing Attribute",
        "KeyError: Missing Dictionary Key",
        "IndexError: Array Out of Bounds",
    ]

    if error_type in known_patterns:
        return 0.95

    # Check for recognized exception types (strong indicators)
    if any(exc in error_lower for exc in python_exceptions):
        # Further boost if it's a very specific error
        if ':' in error_msg:
            return 0.95  # Explicit Python exception with message
        return 0.90  # Recognized Python exception

    if any(exc in error_lower for exc in js_exceptions):
        if ':' in error_msg:
            return 0.93
        return 0.88  # Recognized JS exception

    # Partial match: error type extracted with colon separator
    if ":" in error_msg.split('\n')[0]:
        return 0.80  # Increased from 0.75

    # Very vague error message
    if len(error_type) < 5 or error_type == "Unknown Error":
        return 0.15  # Lowered from 0.25 - very insufficient

    # Unknown but properly formatted error
    return 0.55  # Increased from 0.50


def _score_evidence_richness(evidence_report: EvidenceReport, code_analysis: CodeAnalysis) -> float:
    """Score based on how much evidence we have (0.0-1.0)."""
    score = 0.0

    # Evidence count (max 0.4)
    if evidence_report.evidence_list:
        score += min(0.4, len(evidence_report.evidence_list) * 0.1)

    # Code analysis depth (max 0.3)
    code_depth = 0
    if code_analysis.variables:
        code_depth += 0.1
    if code_analysis.functions:
        code_depth += 0.1
    if code_analysis.nullish_checks:
        code_depth += 0.1
    score += code_depth

    # Error symbol identified (max 0.2)
    if evidence_report.error_symbol:
        score += 0.2

    # Penalty for gaps (max -0.2)
    if evidence_report.gaps:
        gap_penalty = len(evidence_report.gaps) * 0.05
        score = max(0.0, score - gap_penalty)

    return min(1.0, score)


def _score_correlation(
    evidence_report: EvidenceReport,
    parsed_stack: ParsedStackTrace,
    code_analysis: CodeAnalysis
) -> float:
    """Score how well error, stack, and code correlate (0.0-1.0)."""
    score = 0.0

    # Stack trace available and has user frames
    if parsed_stack.user_frames:
        score += 0.4
        # Stack frames match code functions
        for frame in parsed_stack.user_frames:
            if frame.function_name in code_analysis.functions:
                score += 0.2
                break
    else:
        score -= 0.2

    # Error symbol found in code
    if evidence_report.error_symbol and evidence_report.error_symbol in code_analysis.variables:
        score += 0.3

    # No conflicts
    if not evidence_report.conflicts:
        score += 0.1

    # Relevant variables/functions identified
    if evidence_report.relevant_variables or evidence_report.relevant_functions:
        score += 0.2

    return min(1.0, max(0.0, score))


def _generate_justification(
    pattern_score: float,
    evidence_score: float,
    correlation_score: float,
    evidence_report: EvidenceReport,
    parsed_error: ParsedError
) -> str:
    """Generate human-readable confidence justification."""
    parts = []

    # Pattern match
    if pattern_score > 0.9:
        parts.append("error matches known pattern")
    elif pattern_score > 0.7:
        parts.append("error type recognized")
    else:
        parts.append("error type uncertain")

    # Evidence
    if evidence_score > 0.8:
        parts.append(f"{len(evidence_report.evidence_list)} evidence items found")
    elif evidence_score > 0.5:
        parts.append("some evidence available")
    else:
        parts.append("limited evidence")

    # Correlation
    if correlation_score > 0.8:
        parts.append("error/stack/code correlate well")
    elif correlation_score > 0.5:
        parts.append("partial error/code correlation")
    else:
        parts.append("weak error/code correlation")

    # Conflicts/gaps
    if evidence_report.conflicts:
        parts.append(f"{len(evidence_report.conflicts)} conflict(s)")
    if evidence_report.gaps:
        parts.append(f"{len(evidence_report.gaps)} gap(s)")

    return "; ".join(parts)
