from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Alert
from .alert_service import AlertService
from nlp.models import EmotionAnalysis


class TriggerAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, analysis_id):
        try:
            analysis = EmotionAnalysis.objects.get(
                id=analysis_id,
                journal_entry__user=request.user
            )
        except EmotionAnalysis.DoesNotExist:
            return Response(
                {'error': 'Analysis not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        service = AlertService()
        alert = service.send_alert(request.user, analysis)

        if alert is None:
            return Response({
                'message': 'No alert needed — emotion levels are normal.',
                'severity': 'low'
            }, status=status.HTTP_200_OK)

        return Response({
            'message': f'Alert triggered successfully!',
            'alert': {
                'id': alert.id,
                'severity': alert.severity,
                'status': alert.status,
                'contact_notified': alert.contact_notified,
                'triggered_at': alert.triggered_at,
                'message': alert.message
            }
        }, status=status.HTTP_201_CREATED)


class AlertListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alerts = Alert.objects.filter(user=request.user)
        data = [{
            'id': a.id,
            'severity': a.severity,
            'status': a.status,
            'dominant_emotion': a.emotion_analysis.dominant_emotion,
            'contact_notified': a.contact_notified,
            'triggered_at': a.triggered_at,
        } for a in alerts]

        return Response({
            'count': alerts.count(),
            'alerts': data
        }, status=status.HTTP_200_OK)


class ResolveAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, alert_id):
        service = AlertService()
        alert = service.resolve_alert(alert_id)

        if not alert:
            return Response(
                {'error': 'Alert not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'message': 'Alert resolved successfully!',
            'alert_id': alert.id,
            'status': alert.status,
            'resolved_at': alert.resolved_at
        }, status=status.HTTP_200_OK)