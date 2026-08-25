from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('explain/', views.explain_error, name='explain_error'),
]
