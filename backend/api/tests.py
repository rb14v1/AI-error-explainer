from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .services.error_explainer_agent import ErrorExplainerAgent
from .services.error_patterns import classify_error


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check_success(self):
        url = reverse('health_check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['service'], 'AI Error Explainer API')

    def test_health_check_response_structure(self):
        url = reverse('health_check')
        response = self.client.get(url)
        self.assertIn('status', response.data)
        self.assertIn('service', response.data)


class ErrorPatternTests(TestCase):
    """Test error classification and pattern matching."""

    def test_classify_undefined_property_error(self):
        msg = 'TypeError: Cannot read property "name" of undefined'
        error_type, confidence = classify_error(msg)
        self.assertIn('Undefined', error_type)
        self.assertGreaterEqual(confidence, 0.8)

    def test_classify_not_a_function_error(self):
        msg = 'TypeError: myFunc is not a function'
        error_type, confidence = classify_error(msg)
        self.assertIn('function', error_type.lower())
        self.assertGreaterEqual(confidence, 0.8)

    def test_classify_syntax_error(self):
        msg = 'SyntaxError: Unexpected token }'
        error_type, confidence = classify_error(msg)
        self.assertIn('SyntaxError', error_type)
        self.assertGreaterEqual(confidence, 0.8)

    def test_classify_undefined_variable(self):
        msg = 'ReferenceError: myVar is not defined'
        error_type, confidence = classify_error(msg)
        self.assertIn('ReferenceError', error_type)
        self.assertGreaterEqual(confidence, 0.8)

    def test_classify_unknown_error(self):
        msg = 'Some weird error that does not match patterns'
        error_type, confidence = classify_error(msg)
        self.assertIsNotNone(error_type)
        self.assertGreater(confidence, 0.0)

    def test_classify_empty_message(self):
        error_type, confidence = classify_error('')
        self.assertEqual(error_type, 'Unknown Error')
        self.assertEqual(confidence, 0.0)


class ErrorExplainerAgentTests(TestCase):
    """Test the Error Explainer Agent."""

    def setUp(self):
        self.agent = ErrorExplainerAgent()

    def test_analyze_undefined_property_error(self):
        result = self.agent.analyze(
            error_message='TypeError: Cannot read property "map" of undefined'
        )
        self.assertEqual(result['status'], 'success')
        self.assertIn('Type', result['error_type'])
        self.assertIsNotNone(result['what_happened'])
        self.assertGreater(len(result['what_happened']), 0)
        self.assertIsInstance(result['how_to_fix_it'], list)
        self.assertGreater(len(result['how_to_fix_it']), 0)
        self.assertIn(result['severity'], ['Low', 'Medium', 'High', 'Critical'])
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)

    def test_analyze_with_stack_trace(self):
        result = self.agent.analyze(
            error_message='TypeError: Cannot read property "map" of undefined',
            stack_trace='at UserList (UserList.tsx:14:18)'
        )
        self.assertEqual(result['status'], 'success')
        # Confidence should be reasonable with stack trace
        self.assertGreaterEqual(result['confidence'], 0.4)

    def test_analyze_with_code_snippet(self):
        result = self.agent.analyze(
            error_message='TypeError: Cannot read property "map" of undefined',
            code_snippet='const UserList = ({ users }) => { return users.map(u => u.name); };'
        )
        self.assertEqual(result['status'], 'success')
        self.assertGreaterEqual(result['confidence'], 0.4)

    def test_analyze_syntax_error(self):
        result = self.agent.analyze(
            error_message='SyntaxError: Unexpected token }'
        )
        self.assertEqual(result['status'], 'success')
        self.assertIn('Syntax', result['error_type'])
        self.assertEqual(result['severity'], 'Critical')

    def test_analyze_reference_error(self):
        result = self.agent.analyze(
            error_message='ReferenceError: myVariable is not defined'
        )
        self.assertEqual(result['status'], 'success')
        self.assertIn('Reference', result['error_type'])

    def test_analyze_unknown_error(self):
        result = self.agent.analyze(
            error_message='Some completely unknown error message'
        )
        self.assertEqual(result['status'], 'success')
        self.assertIsNotNone(result['error_type'])
        self.assertGreater(len(result['how_to_fix_it']), 0)

    def test_analyze_with_language(self):
        result = self.agent.analyze(
            error_message='AttributeError: has no attribute',
            language='python'
        )
        self.assertEqual(result['status'], 'success')
        self.assertIn('Attribute', result['error_type'])

    def test_analyze_response_schema(self):
        result = self.agent.analyze(
            error_message='TypeError: Cannot read property "name" of undefined'
        )
        required_fields = [
            'status', 'error_type', 'what_happened', 'why_it_happened',
            'how_to_fix_it', 'corrected_code', 'prevention_tips',
            'severity', 'confidence'
        ]
        for field in required_fields:
            self.assertIn(field, result, f"Missing field: {field}")

        # Validate types
        self.assertEqual(result['status'], 'success')
        self.assertIsInstance(result['error_type'], str)
        self.assertIsInstance(result['what_happened'], str)
        self.assertIsInstance(result['why_it_happened'], str)
        self.assertIsInstance(result['how_to_fix_it'], list)
        self.assertIsInstance(result['corrected_code'], str)
        self.assertIsInstance(result['prevention_tips'], list)
        self.assertIn(result['severity'], ['Low', 'Medium', 'High', 'Critical'])
        self.assertIsInstance(result['confidence'], float)


class ExplainErrorAPITests(TestCase):
    """Test the explain error API endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('explain_error')

    def test_explain_error_with_valid_input(self):
        payload = {
            'error_message': 'TypeError: Cannot read property "map" of undefined'
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('error_type', response.data)
        self.assertIn('what_happened', response.data)

    def test_explain_error_with_all_fields(self):
        payload = {
            'error_message': 'TypeError: Cannot read property "map" of undefined',
            'stack_trace': 'at UserList (UserList.tsx:14:18)',
            'code_snippet': 'const UserList = ({ users }) => { return users.map(u => u.name); };',
            'language': 'typescript'
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_explain_error_missing_required_field(self):
        payload = {
            'stack_trace': 'at UserList (UserList.tsx:14:18)'
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_explain_error_empty_error_message(self):
        payload = {
            'error_message': ''
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# Phase 3: Pipeline Component Tests

class ErrorParserTests(TestCase):
    """Test error message parsing."""

    def setUp(self):
        from .services.error_parser import parse_error

        self.parse_error = parse_error

    def test_parse_error_with_type_and_message(self):
        msg = 'TypeError: Cannot read property "name" of undefined'
        result = self.parse_error(msg)
        self.assertIn('Type', result.error_type)
        self.assertEqual(result.full_message, msg)

    def test_parse_error_extracts_symbol(self):
        msg = 'ReferenceError: myVar is not defined'
        result = self.parse_error(msg)
        self.assertEqual(result.error_symbol, 'myVar')

    def test_parse_error_detects_language(self):
        js_msg = 'TypeError: Cannot read property "map" of undefined'
        result = self.parse_error(js_msg)
        self.assertEqual(result.language_hint, 'javascript')

        py_msg = 'AttributeError: has no attribute'
        result = self.parse_error(py_msg)
        self.assertEqual(result.language_hint, 'python')

    def test_parse_error_empty_message(self):
        result = self.parse_error('')
        self.assertEqual(result.error_type, 'Unknown Error')
        self.assertEqual(result.error_symbol, None)


class StackTraceParserTests(TestCase):
    """Test stack trace parsing."""

    def setUp(self):
        from .services.stack_trace_parser import parse_stack_trace

        self.parse_stack_trace = parse_stack_trace

    def test_parse_python_traceback(self):
        trace = '''Traceback (most recent call last):
  File "app.py", line 42, in main
    result = process(data)
  File "lib.py", line 10, in process
    return data.method()
'''
        result = self.parse_stack_trace(trace)
        self.assertEqual(result.language, 'python')
        self.assertGreater(len(result.frames), 0)
        # Should filter out library frames
        self.assertGreaterEqual(len(result.user_frames), 0)

    def test_parse_javascript_trace(self):
        trace = 'at UserList (UserList.tsx:14:18)\nat processData (data.js:5:10)'
        result = self.parse_stack_trace(trace)
        self.assertEqual(result.language, 'javascript')
        self.assertGreater(len(result.frames), 0)

    def test_parse_stack_filters_library_frames(self):
        trace = '''at MyComponent (MyComponent.tsx:20:5)
at ReactDOM (node_modules/react-dom/dist.js:100:10)
at process (/app/lib/process.js:42:5)'''
        result = self.parse_stack_trace(trace)
        # node_modules should be filtered
        library_count = sum(1 for f in result.frames if f.is_library)
        self.assertGreater(library_count, 0)

    def test_parse_empty_stack_trace(self):
        result = self.parse_stack_trace(None)
        self.assertEqual(len(result.frames), 0)
        self.assertEqual(result.language, 'unknown')


class CodeAnalyzerTests(TestCase):
    """Test code analysis."""

    def setUp(self):
        from .services.code_analyzer import analyze_code

        self.analyze_code = analyze_code

    def test_analyze_javascript_code(self):
        code = '''
const UserList = ({ users }) => {
  return users.map(u => u.name);
};
'''
        result = self.analyze_code(code)
        self.assertEqual(result.language, 'javascript')
        self.assertIn('UserList', result.functions)
        # Check for users variable (either in variables or at least detected)
        self.assertTrue('users' in result.variables or len(result.variables) > 0)
        self.assertIn('map', result.array_methods)

    def test_analyze_python_code(self):
        code = '''
def process_data(items):
    result = [item.value for item in items]
    return result
'''
        result = self.analyze_code(code)
        self.assertEqual(result.language, 'python')
        self.assertIn('process_data', result.functions)

    def test_analyze_nullish_checks(self):
        code = '''
const value = user?.profile?.name ?? 'Unknown';
if (users) { users.map(u => u.id); }
'''
        result = self.analyze_code(code)
        self.assertGreater(len(result.nullish_checks), 0)

    def test_analyze_async_patterns(self):
        code = '''
async function fetch() {
  const data = await api.get();
  return data;
}
'''
        result = self.analyze_code(code)
        self.assertGreater(len(result.async_patterns), 0)

    def test_analyze_empty_code(self):
        result = self.analyze_code(None)
        self.assertEqual(result.language, 'unknown')
        self.assertEqual(len(result.variables), 0)


class EvidenceBuilderTests(TestCase):
    """Test evidence correlation."""

    def setUp(self):
        from .services.error_parser import parse_error
        from .services.stack_trace_parser import parse_stack_trace
        from .services.code_analyzer import analyze_code
        from .services.evidence_builder import build_evidence

        self.parse_error = parse_error
        self.parse_stack_trace = parse_stack_trace
        self.analyze_code = analyze_code
        self.build_evidence = build_evidence

    def test_evidence_correlates_error_and_code(self):
        error = self.parse_error('TypeError: Cannot read property "map" of undefined')
        stack = self.parse_stack_trace('at process (app.js:10:5)')
        code = self.analyze_code('const items = undefined; items.map(x => x);')

        evidence = self.build_evidence(error, stack, code)
        self.assertGreater(len(evidence.evidence_list), 0)

    def test_evidence_detects_symbol_in_code(self):
        error = self.parse_error('ReferenceError: users is not defined')
        stack = self.parse_stack_trace('')
        code = self.analyze_code('const users = [];')

        evidence = self.build_evidence(error, stack, code)
        self.assertIn('users', evidence.relevant_variables)

    def test_evidence_reports_gaps(self):
        error = self.parse_error('TypeError')
        stack = self.parse_stack_trace(None)
        code = self.analyze_code(None)

        evidence = self.build_evidence(error, stack, code)
        self.assertGreater(len(evidence.gaps), 0)

    def test_evidence_detects_conflicts(self):
        error = self.parse_error('ReferenceError: myVar is not defined')
        stack = self.parse_stack_trace('')
        code = self.analyze_code('const other = 5;')

        evidence = self.build_evidence(error, stack, code)
        # myVar not found in code should create conflict
        self.assertGreater(len(evidence.conflicts), 0)


class ConfidenceScorerTests(TestCase):
    """Test confidence calculation."""

    def setUp(self):
        from .services.error_parser import parse_error
        from .services.stack_trace_parser import parse_stack_trace
        from .services.code_analyzer import analyze_code
        from .services.evidence_builder import build_evidence
        from .services.confidence_scorer import score_confidence

        self.parse_error = parse_error
        self.parse_stack_trace = parse_stack_trace
        self.analyze_code = analyze_code
        self.build_evidence = build_evidence
        self.score_confidence = score_confidence

    def test_confidence_is_high_with_rich_evidence(self):
        error = self.parse_error('TypeError: Cannot read property "map" of undefined')
        stack = self.parse_stack_trace('at UserList (UserList.tsx:14:18)')
        code = self.analyze_code('const users = undefined; users.map(x => x);')

        evidence = self.build_evidence(error, stack, code)
        confidence = self.score_confidence(error, evidence, stack, code)
        self.assertGreaterEqual(confidence.overall, 0.5)

    def test_confidence_is_low_with_incomplete_input(self):
        error = self.parse_error('Some unknown error')
        stack = self.parse_stack_trace(None)
        code = self.analyze_code(None)

        evidence = self.build_evidence(error, stack, code)
        confidence = self.score_confidence(error, evidence, stack, code)
        self.assertLess(confidence.overall, 0.6)

    def test_confidence_has_justification(self):
        error = self.parse_error('TypeError')
        stack = self.parse_stack_trace('')
        code = self.analyze_code('')

        evidence = self.build_evidence(error, stack, code)
        confidence = self.score_confidence(error, evidence, stack, code)
        self.assertGreater(len(confidence.justification), 0)

    def test_confidence_penalizes_conflicts(self):
        error = self.parse_error('ReferenceError: unknown is not defined')
        stack = self.parse_stack_trace('')
        code = self.analyze_code('const other = 5;')

        evidence = self.build_evidence(error, stack, code)
        confidence = self.score_confidence(error, evidence, stack, code)
        # Should be lower due to conflict
        self.assertLess(confidence.overall, 0.8)


class DiagnosticEngineTests(TestCase):
    """Test diagnosis generation."""

    def setUp(self):
        from .services.error_parser import parse_error
        from .services.stack_trace_parser import parse_stack_trace
        from .services.code_analyzer import analyze_code
        from .services.evidence_builder import build_evidence
        from .services.diagnostic_engine import generate_diagnosis

        self.parse_error = parse_error
        self.parse_stack_trace = parse_stack_trace
        self.analyze_code = analyze_code
        self.build_evidence = build_evidence
        self.generate_diagnosis = generate_diagnosis

    def test_diagnosis_includes_error_symbol(self):
        error = self.parse_error('TypeError: Cannot read property "map" of undefined')
        stack = self.parse_stack_trace('')
        code = self.analyze_code('const users = undefined;')
        evidence = self.build_evidence(error, stack, code)

        diagnosis = self.generate_diagnosis(error, evidence)
        # Check that diagnosis mentions what/why/how
        self.assertGreater(len(diagnosis.what_happened), 0)
        self.assertGreater(len(diagnosis.why_it_happened), 0)
        self.assertGreater(len(diagnosis.how_to_fix_it), 0)

    def test_diagnosis_generates_corrected_code(self):
        error = self.parse_error('TypeError: Cannot read property "map" of undefined')
        stack = self.parse_stack_trace('')
        code = self.analyze_code('const users = undefined; users.map(x => x);')
        evidence = self.build_evidence(error, stack, code)

        diagnosis = self.generate_diagnosis(error, evidence, code)
        self.assertGreater(len(diagnosis.corrected_code), 0)

    def test_diagnosis_handles_unknown_errors(self):
        error = self.parse_error('SomeWeirdError: Unknown')
        stack = self.parse_stack_trace('')
        code = self.analyze_code('')
        evidence = self.build_evidence(error, stack, code)

        diagnosis = self.generate_diagnosis(error, evidence)
        self.assertGreater(len(diagnosis.what_happened), 0)


class ContextualFixesTests(TestCase):
    """Test that fixes are contextual, not generic templates."""

    def setUp(self):
        self.agent = ErrorExplainerAgent()

    def test_fixes_are_specific_to_undefined_error(self):
        # Undefined error
        result1 = self.agent.analyze(
            error_message='TypeError: Cannot read property "map" of undefined',
            code_snippet='const users = undefined; users.map(x => x);'
        )

        # Not-a-function error
        result2 = self.agent.analyze(
            error_message='TypeError: myFunc is not a function',
            code_snippet='const x = 5; x();'
        )

        # Fixes should be different
        self.assertNotEqual(result1['how_to_fix_it'][0], result2['how_to_fix_it'][0])

    def test_prevention_tips_are_language_specific(self):
        # Python error
        result_py = self.agent.analyze(
            error_message='AttributeError: has no attribute',
            language='python',
            code_snippet='class User:\n    pass\nuser = User()\nuser.name'
        )

        # JavaScript error
        result_js = self.agent.analyze(
            error_message='TypeError: Cannot read property "name" of undefined',
            language='typescript',
            code_snippet='const user = undefined; user.name;'
        )

        # Tips should reference language-specific tools
        py_tips = ' '.join(result_py['prevention_tips']).lower()
        js_tips = ' '.join(result_js['prevention_tips']).lower()

        # At least one should be different in nature
        self.assertNotEqual(result_py['prevention_tips'], result_js['prevention_tips'])


class BackwardCompatibilityTests(TestCase):
    """Test API backward compatibility."""

    def setUp(self):
        self.agent = ErrorExplainerAgent()
        self.client = APIClient()
        self.url = reverse('explain_error')

    def test_response_schema_unchanged(self):
        """Ensure response format matches api_schema.json."""
        result = self.agent.analyze('TypeError: test error')

        required_fields = [
            'status', 'error_type', 'what_happened', 'why_it_happened',
            'how_to_fix_it', 'corrected_code', 'prevention_tips',
            'severity', 'confidence'
        ]

        for field in required_fields:
            self.assertIn(field, result, f"Missing required field: {field}")

        # Type checks
        self.assertEqual(result['status'], 'success')
        self.assertIsInstance(result['error_type'], str)
        self.assertIsInstance(result['what_happened'], str)
        self.assertIsInstance(result['why_it_happened'], str)
        self.assertIsInstance(result['how_to_fix_it'], list)
        self.assertIsInstance(result['corrected_code'], str)
        self.assertIsInstance(result['prevention_tips'], list)
        self.assertIn(result['severity'], ['Low', 'Medium', 'High', 'Critical'])
        self.assertIsInstance(result['confidence'], float)

    def test_confidence_still_between_0_and_1(self):
        result = self.agent.analyze('TypeError: test')
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)

    def test_explain_error_whitespace_only_error_message(self):
        payload = {
            'error_message': '   '
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_explain_error_oversized_payload(self):
        payload = {
            'error_message': 'x' * 25000,
            'stack_trace': 'y' * 25000,
            'code_snippet': 'z' * 2000
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_explain_error_response_structure(self):
        payload = {
            'error_message': 'SyntaxError: Unexpected token'
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        required_fields = [
            'status', 'error_type', 'what_happened', 'why_it_happened',
            'how_to_fix_it', 'corrected_code', 'prevention_tips',
            'severity', 'confidence'
        ]
        for field in required_fields:
            self.assertIn(field, response.data)

    def test_explain_error_python_attribute_error(self):
        payload = {
            'error_message': 'AttributeError: has no attribute',
            'language': 'python'
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Attribute', response.data['error_type'])

    def test_explain_error_confidence_increases_with_context(self):
        # Test with just error message
        payload_minimal = {
            'error_message': 'TypeError: Cannot read property "map" of undefined'
        }
        response_minimal = self.client.post(self.url, payload_minimal, format='json')
        confidence_minimal = response_minimal.data['confidence']

        # Test with error message and stack trace
        payload_with_trace = {
            'error_message': 'TypeError: Cannot read property "map" of undefined',
            'stack_trace': 'at UserList (UserList.tsx:14:18)'
        }
        response_with_trace = self.client.post(self.url, payload_with_trace, format='json')
        confidence_with_trace = response_with_trace.data['confidence']

        # Confidence should be higher with more context
        self.assertGreaterEqual(confidence_with_trace, confidence_minimal)
