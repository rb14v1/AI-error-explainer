from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from mozilla_django_oidc.contrib.drf import OIDCAuthentication
from .serializers import ExplainErrorSerializer
from .services.error_explainer_agent import ErrorExplainerAgent


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def health_check(request):
    """Public health-check endpoint — no authentication required."""
    return Response({
        'status': 'ok',
        'service': 'AI Error Explainer API'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([OIDCAuthentication])
@permission_classes([IsAuthenticated])
def explain_error(request):
    """Protected endpoint — requires a valid OIDC/OAuth2 bearer token.

    Unauthenticated requests receive HTTP 401.
    """
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
