from django.urls import path
from .views import GetRecommendationsView, RecommendationHistoryView

urlpatterns = [
    path(
        'entries/<int:entry_id>/',
        GetRecommendationsView.as_view(),
        name='get-recommendations'
    ),
    path(
        'history/',
        RecommendationHistoryView.as_view(),
        name='recommendation-history'
    ),
]