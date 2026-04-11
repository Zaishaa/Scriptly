from django.contrib import admin
from .models import EmotionAnalysis


@admin.register(EmotionAnalysis)
class EmotionAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'journal_entry', 'dominant_emotion',
        'confidence_score', 'is_crisis', 'analyzed_at'
    )
    list_filter = ('dominant_emotion', 'is_crisis')
    search_fields = ('journal_entry__user__email',)