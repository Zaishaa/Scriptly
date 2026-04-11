from django.urls import path
from .views import TriggerAlertView, AlertListView, ResolveAlertView

urlpatterns = [
    path(
        'trigger/<int:analysis_id>/',
        TriggerAlertView.as_view(),
        name='trigger-alert'
    ),
    path(
        'list/',
        AlertListView.as_view(),
        name='alert-list'
    ),
    path(
        'resolve/<int:alert_id>/',
        ResolveAlertView.as_view(),
        name='resolve-alert'
    ),
]