from django.urls import path
from .views import (
    AnalyzeEmotionView,
    GetEmotionAnalysisView,
    EmotionHistoryView
)

urlpatterns = [
    path('analyze/<int:entry_id>/', AnalyzeEmotionView.as_view(), name='analyze-emotion'),
    path('analysis/<int:entry_id>/', GetEmotionAnalysisView.as_view(), name='get-analysis'),
    path('history/', EmotionHistoryView.as_view(), name='emotion-history'),
]