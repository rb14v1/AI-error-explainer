"""
Evidence Builder

Correlates error message, stack trace, and code analysis to build evidence.
"""

from typing import NamedTuple, List, Dict, Optional
from .error_parser import ParsedError
from .stack_trace_parser import ParsedStackTrace, StackFrame
from .code_analyzer import CodeAnalysis


class Evidence(NamedTuple):
    """A single piece of evidence."""
    type: str  # 'error_symbol', 'stack_correlation', 'code_pattern', 'async_mismatch', etc
    value: str
    strength: float  # 0.0-1.0 confidence
    source: str  # 'error', 'stack', 'code'


class EvidenceReport(NamedTuple):
    """Complete evidence analysis."""
    evidence_list: List[Evidence]
    error_symbol: Optional[str]
    user_code_frames: List[StackFrame]
    relevant_variables: List[str]
    relevant_functions: List[str]
    conflicts: List[str]  # Contradictory evidence
    gaps: List[str]  # Missing information


def build_evidence(
    parsed_error: ParsedError,
    parsed_stack: ParsedStackTrace,
    code_analysis: CodeAnalysis
) -> EvidenceReport:
    """
    Build evidence report by correlating all three data sources.

    Args:
        parsed_error: Parsed error components
        parsed_stack: Parsed stack trace
        code_analysis: Analyzed code structure

    Returns:
        EvidenceReport with correlated findings
    """
    evidence_list: List[Evidence] = []
    conflicts: List[str] = []
    gaps: List[str] = []
    relevant_variables: List[str] = []
    relevant_functions: List[str] = []

    # Step 1: Error symbol evidence
    if parsed_error.error_symbol:
        evidence_list.append(Evidence(
            type='error_symbol',
            value=parsed_error.error_symbol,
            strength=0.9,
            source='error'
        ))
        # Check if symbol is in code
        if parsed_error.error_symbol in code_analysis.variables:
            relevant_variables.append(parsed_error.error_symbol)
            evidence_list.append(Evidence(
                type='symbol_in_code',
                value=f'{parsed_error.error_symbol} declared in code',
                strength=0.85,
                source='code'
            ))
        elif parsed_error.error_symbol in code_analysis.functions:
            relevant_functions.append(parsed_error.error_symbol)

    # Step 2: Stack trace correlation
    if parsed_stack.user_frames:
        evidence_list.append(Evidence(
            type='user_frames_found',
            value=f'{len(parsed_stack.user_frames)} user code frame(s)',
            strength=0.8,
            source='stack'
        ))
        # Check if functions in stack exist in code
        for frame in parsed_stack.user_frames:
            if frame.function_name in code_analysis.functions:
                relevant_functions.append(frame.function_name)
    else:
        gaps.append('No user code frames in stack trace')

    # Step 3: Check for async/await mismatches
    error_msg_lower = parsed_error.full_message.lower()
    has_async_in_error = 'promise' in error_msg_lower or 'async' in error_msg_lower
    has_async_in_code = bool(code_analysis.async_patterns)

    if has_async_in_error and not has_async_in_code:
        conflicts.append('Error mentions async but code has no async patterns')
    elif has_async_in_code and not has_async_in_error:
        # May not be a conflict, async code can fail normally
        pass

    # Step 4: Check for nullish access patterns
    error_msg_lower = parsed_error.full_message.lower()
    has_null_undefined_in_error = any(x in error_msg_lower for x in ['undefined', 'null', 'cannot read'])
    has_nullish_checks_in_code = bool(code_analysis.nullish_checks)

    if has_null_undefined_in_error:
        evidence_list.append(Evidence(
            type='null_undefined_error',
            value='Null/undefined access indicated',
            strength=0.85,
            source='error'
        ))
        if has_nullish_checks_in_code:
            evidence_list.append(Evidence(
                type='nullish_checks_present',
                value='Code has null/undefined checks',
                strength=0.7,
                source='code'
            ))
        else:
            gaps.append('No null/undefined checks found in code')

    # Step 5: Check for array method errors
    error_msg_lower = parsed_error.full_message.lower()
    for method in code_analysis.array_methods:
        if method in error_msg_lower:
            evidence_list.append(Evidence(
                type='method_error_correlation',
                value=f'.{method}() used in code, mentioned in error',
                strength=0.8,
                source='error+code'
            ))

    # Step 6: Check for type hints
    if code_analysis.language == 'javascript' and code_analysis.has_type_hints:
        evidence_list.append(Evidence(
            type='type_hints_present',
            value='TypeScript type hints present',
            strength=0.6,
            source='code'
        ))

    # Step 7: Track evidence gaps
    if not parsed_error.error_symbol:
        gaps.append('No error symbol identified from message')
    if not code_analysis.variables and not code_analysis.functions:
        gaps.append('No structure extracted from code snippet')
    if not parsed_stack.frames:
        gaps.append('No stack trace provided')

    # Step 8: Check for conflicting variable evidence
    if parsed_error.error_symbol and parsed_error.error_symbol not in code_analysis.variables:
        if code_analysis.variables:  # Only if we found other variables
            conflicts.append(f'{parsed_error.error_symbol} not found in code')

    return EvidenceReport(
        evidence_list=evidence_list,
        error_symbol=parsed_error.error_symbol,
        user_code_frames=parsed_stack.user_frames,
        relevant_variables=list(set(relevant_variables)),
        relevant_functions=list(set(relevant_functions)),
        conflicts=conflicts,
        gaps=gaps
    )
