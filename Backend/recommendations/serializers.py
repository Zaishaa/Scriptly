from rest_framework import serializers
from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = (
            'id', 'category', 'title',
            'description', 'action_steps',
            'is_crisis_recommendation', 'created_at'
        )
        read_only_fields = fields