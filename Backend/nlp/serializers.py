from rest_framework import serializers
from .models import EmotionAnalysis


class EmotionAnalysisSerializer(serializers.ModelSerializer):
    journal_entry_title = serializers.CharField(
        source='journal_entry.title',
        read_only=True
    )

    class Meta:
        model = EmotionAnalysis
        fields = (
            'id', 'journal_entry', 'journal_entry_title',
            'dominant_emotion', 'confidence_score',
            'joy_score', 'sadness_score', 'anger_score',
            'fear_score', 'love_score', 'surprise_score',
            'is_crisis', 'processed_text', 'analyzed_at'
        )
        read_only_fields = fields