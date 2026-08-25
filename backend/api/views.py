from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import ExplainErrorSerializer
from .services.error_explainer_agent import ErrorExplainerAgent


@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'ok',
        'service': 'AI Error Explainer API'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def explain_error(request):
    serializer = ExplainErrorSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'error_message field is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    validated_data = serializer.validated_data

    # Use the Error Explainer Agent to analyze the error
    agent = ErrorExplainerAgent()
    response = agent.analyze(
        error_message=validated_data.get('error_message'),
        stack_trace=validated_data.get('stack_trace'),
        code_snippet=validated_data.get('code_snippet'),
        language=validated_data.get('language')
    )

    return Response(response, status=status.HTTP_200_OK)
