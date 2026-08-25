"""
Stack Trace Parser

Parses stack traces to extract frames, identify user code vs library frames,
and build call sequence with context.
"""

import re
from typing import NamedTuple, Optional, List


class StackFrame(NamedTuple):
    """A single stack frame."""
    file_path: str
    function_name: str
    line_number: int
    column_number: Optional[int]
    code_line: Optional[str]
    is_library: bool  # True if framework/node_modules/standard library


class ParsedStackTrace(NamedTuple):
    """Parsed stack trace result."""
    frames: List[StackFrame]
    user_frames: List[StackFrame]  # Non-library frames
    language: str  # 'python', 'javascript', 'java', 'unknown'


def parse_stack_trace(stack_trace: Optional[str], language_hint: Optional[str] = None) -> ParsedStackTrace:
    """
    Parse a stack trace into frames.

    Args:
        stack_trace: Raw stack trace string
        language_hint: Hint language ('python', 'javascript', etc)

    Returns:
        ParsedStackTrace with all frames and user-code frames
    """
    if not stack_trace:
        return ParsedStackTrace(frames=[], user_frames=[], language='unknown')

    # Detect language from trace format
    detected_language = language_hint or _detect_language(stack_trace)

    # Parse frames based on language
    if detected_language == 'python':
        frames = _parse_python_traceback(stack_trace)
    elif detected_language == 'javascript':
        frames = _parse_javascript_trace(stack_trace)
    elif detected_language == 'java':
        frames = _parse_java_trace(stack_trace)
    else:
        frames = _parse_generic_trace(stack_trace)

    # Filter library frames
    user_frames = [f for f in frames if not f.is_library]

    return ParsedStackTrace(frames=frames, user_frames=user_frames, language=detected_language)


def _detect_language(stack_trace: str) -> str:
    """Detect stack trace language from format."""
    trace_lower = stack_trace.lower()

    if 'file "' in trace_lower or 'traceback' in trace_lower:
        return 'python'

    if 'at ' in trace_lower and any(x in trace_lower for x in ['.js:', '.ts:', '.tsx:', '.jsx:']):
        return 'javascript'

    if 'at ' in trace_lower and '.java:' in trace_lower:
        return 'java'

    # Check for 'at ' without file extension (generic JS)
    if 'at ' in trace_lower and '(' in trace_lower and ':' in trace_lower:
        return 'javascript'

    return 'unknown'


def _parse_python_traceback(trace: str) -> List[StackFrame]:
    """Parse Python traceback format."""
    frames = []
    lines = trace.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Match: File "path/to/file.py", line 42, in function_name
        match = re.search(r'File\s+"([^"]+)",\s+line\s+(\d+)(?:,\s+in\s+(.+))?', line)
        if match:
            file_path = match.group(1)
            line_number = int(match.group(2))
            function_name = match.group(3) or '<module>'

            # Next line may contain the code (but not if it's another File statement)
            code_line = None
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # Only treat as code if it's NOT another File statement
                if not next_line.startswith('File '):
                    code_line = next_line
                    i += 1

            is_library = _is_library_frame(file_path)
            frames.append(StackFrame(
                file_path=file_path,
                function_name=function_name,
                line_number=line_number,
                column_number=None,
                code_line=code_line,
                is_library=is_library
            ))

        i += 1

    return frames


def _parse_javascript_trace(trace: str) -> List[StackFrame]:
    """Parse JavaScript/Node.js stack trace format."""
    frames = []

    # Match: at functionName (file:line:col)
    pattern = r'at\s+(.+?)\s+\((.+?):(\d+):(\d+)\)'
    matches = re.findall(pattern, trace)

    for func_name, file_path, line_num, col_num in matches:
        is_library = _is_library_frame(file_path)
        frames.append(StackFrame(
            file_path=file_path,
            function_name=func_name.strip(),
            line_number=int(line_num),
            column_number=int(col_num),
            code_line=None,
            is_library=is_library
        ))

    # Also match: at file:line:col (without function)
    pattern2 = r'at\s+([^(]+):(\d+):(\d+)'
    for match in re.finditer(pattern2, trace):
        if '(' not in match.group(0):  # Avoid re-matching above
            file_path = match.group(1).strip()
            is_library = _is_library_frame(file_path)
            frames.append(StackFrame(
                file_path=file_path,
                function_name='<anonymous>',
                line_number=int(match.group(2)),
                column_number=int(match.group(3)),
                code_line=None,
                is_library=is_library
            ))

    return frames


def _parse_java_trace(trace: str) -> List[StackFrame]:
    """Parse Java stack trace format."""
    frames = []

    # Match: at package.ClassName.methodName(FileName.java:42)
    pattern = r'at\s+([^(]+)\(([^:]+):(\d+)\)'
    matches = re.findall(pattern, trace)

    for method_name, file_path, line_num in matches:
        is_library = _is_library_frame(file_path)
        frames.append(StackFrame(
            file_path=file_path,
            function_name=method_name.strip(),
            line_number=int(line_num),
            column_number=None,
            code_line=None,
            is_library=is_library
        ))

    return frames


def _parse_generic_trace(trace: str) -> List[StackFrame]:
    """Fallback generic trace parser."""
    frames = []

    # Try to extract any pattern that looks like file:line
    pattern = r'([/\w.-]+\.\w+):(\d+)'
    matches = re.findall(pattern, trace)

    for file_path, line_num in matches:
        is_library = _is_library_frame(file_path)
        frames.append(StackFrame(
            file_path=file_path,
            function_name='<unknown>',
            line_number=int(line_num),
            column_number=None,
            code_line=None,
            is_library=is_library
        ))

    return frames


def _is_library_frame(file_path: str) -> bool:
    """
    Determine if a frame is library/framework code vs user code.

    Library frames: node_modules, venv, site-packages, .../lib/, standard library
    """
    path_lower = file_path.lower()

    library_markers = [
        'node_modules',
        'venv',
        'site-packages',
        '.venv',
        '__pycache__',
        '/lib/',
        '/usr/lib',
        'python',  # stdlib
        'node',    # Node stdlib
        '.next',
        'dist/',
        'build/',
        '.webpack',
        'react',
        'angular',
        'vue',
        'jquery',
        'lodash',
        'moment',
    ]

    return any(marker in path_lower for marker in library_markers)
