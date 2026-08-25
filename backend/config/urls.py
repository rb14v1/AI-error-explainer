from django.urls import path, include

urlpatterns = [
    path('api/', include('api.urls')),
    # OIDC authentication endpoints: /oidc/authenticate/, /oidc/callback/, /oidc/logout/
    path('oidc/', include('mozilla_django_oidc.urls')),
]
