from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from journal.models import JournalEntry
from .models import EmotionAnalysis
from .serializers import EmotionAnalysisSerializer
from .emotion_detector import EmotionDetector
from .preprocessor import TextPreprocessor
from alerts.alert_service import AlertService

class AnalyzeEmotionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, entry_id):
        # Get the journal entry
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

        # Preprocess text
        preprocessor = TextPreprocessor()
        processed_text = preprocessor.preprocess_for_model(entry.content)

        # Detect emotions
        detector = EmotionDetector()
        result = detector.detect_emotions(processed_text)

        # Save or update emotion analysis
        emotion_scores = result['emotion_scores']

        analysis, created = EmotionAnalysis.objects.update_or_create(
            journal_entry=entry,
            defaults={
                'dominant_emotion': result['dominant_emotion'],
                'confidence_score': result['confidence_score'],
                'joy_score': emotion_scores.get('joy', 0.0),
                'sadness_score': emotion_scores.get('sadness', 0.0),
                'anger_score': emotion_scores.get('anger', 0.0),
                'fear_score': emotion_scores.get('fear', 0.0),
                'love_score': emotion_scores.get('love', 0.0),
                'surprise_score': emotion_scores.get('surprise', 0.0),
                'is_crisis': result['is_crisis'],
                'raw_text': entry.content,
                'processed_text': processed_text,
            }
        )

        # Mark entry as analyzed
        entry.is_analyzed = True
        entry.save()
        
        if result['is_crisis'] or result['dominant_emotion'] in ['sadness', 'fear', 'anger']:
            alert_service = AlertService()
            alert_service.send_alert(request.user, analysis)

        return Response({
            'message': 'Emotion analysis complete!',
            'analysis': EmotionAnalysisSerializer(analysis).data
        }, status=status.HTTP_200_OK)
    


class GetEmotionAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entry_id):
        try:
            entry = JournalEntry.objects.get(
                id=entry_id,
                user=request.user
            )
            analysis = entry.emotion_analysis
            serializer = EmotionAnalysisSerializer(analysis)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JournalEntry.DoesNotExist:
            return Response(
                {'error': 'Journal entry not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except EmotionAnalysis.DoesNotExist:
            return Response(
                {'error': 'This entry has not been analyzed yet.'},
                status=status.HTTP_404_NOT_FOUND
            )


class EmotionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        analyses = EmotionAnalysis.objects.filter(
            journal_entry__user=request.user
        ).order_by('-analyzed_at')

        serializer = EmotionAnalysisSerializer(analyses, many=True)
        return Response({
            'count': analyses.count(),
            'history': serializer.data
        }, status=status.HTTP_200_OK)