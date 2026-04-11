from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from journal.models import JournalEntry
from nlp.models import EmotionAnalysis
from .models import Recommendation
from .serializers import RecommendationSerializer
from .engine import RecommendationEngine


class GetRecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entry_id):
        # Get journal entry
        try:
            entry = JournalEntry.objects.get(
                id=entry_id,
                user=request.user
            )
        except JournalEntry.DoesNotExist:
            return Response(
                {'error': 'Journal entry not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if analyzed
        try:
            analysis = entry.emotion_analysis
        except EmotionAnalysis.DoesNotExist:
            return Response(
                {'error': 'Please analyze this entry first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate fresh recommendations
        engine = RecommendationEngine()
        raw_recommendations = engine.generate(analysis)

        # Save to database
        Recommendation.objects.filter(
            emotion_analysis=analysis
        ).delete()

        saved_recs = []
        for rec_data in raw_recommendations:
            rec = Recommendation.objects.create(
                emotion_analysis=analysis,
                category=rec_data['category'],
                title=rec_data['title'],
                description=rec_data['description'],
                action_steps=rec_data['action_steps'],
                is_crisis_recommendation=rec_data.get(
                    'is_crisis_recommendation', False
                )
            )
            saved_recs.append(rec)

        serializer = RecommendationSerializer(saved_recs, many=True)

        return Response({
            'emotion': analysis.dominant_emotion,
            'confidence': analysis.confidence_score,
            'is_crisis': analysis.is_crisis,
            'recommendations': serializer.data
        }, status=status.HTTP_200_OK)


class RecommendationHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recommendations = Recommendation.objects.filter(
            emotion_analysis__journal_entry__user=request.user
        ).order_by('-created_at')

        serializer = RecommendationSerializer(
            recommendations, many=True
        )
        return Response({
            'count': recommendations.count(),
            'recommendations': serializer.data
        }, status=status.HTTP_200_OK)