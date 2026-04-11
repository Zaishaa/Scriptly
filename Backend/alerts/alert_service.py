import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class AlertService:

    def determine_severity(self, emotion_analysis):
        dominant = emotion_analysis.dominant_emotion
        confidence = emotion_analysis.confidence_score

        if emotion_analysis.is_crisis:
            return 'critical'
        elif dominant in ['sadness', 'fear', 'anger'] and confidence > 0.75:
            return 'high'
        elif dominant in ['sadness', 'fear', 'anger'] and confidence > 0.50:
            return 'medium'
        else:
            return 'low'

    def build_message(self, user, emotion_analysis, severity):
        emotion = emotion_analysis.dominant_emotion
        confidence = round(emotion_analysis.confidence_score * 100, 1)
        entry_title = emotion_analysis.journal_entry.title
        timestamp = emotion_analysis.analyzed_at.strftime('%Y-%m-%d %H:%M')

        message = f"""
SCRIPTLY MENTAL HEALTH ALERT
{'='*40}
Severity: {severity.upper()}
User: {user.email} (@{user.username})
Time: {timestamp}

Journal Entry: "{entry_title}"
Detected Emotion: {emotion.upper()}
Confidence: {confidence}%

{'⚠️ CRISIS INDICATORS DETECTED ⚠️' if emotion_analysis.is_crisis else ''}

Emotion Breakdown:
- Joy:      {round(emotion_analysis.joy_score * 100, 1)}%
- Sadness:  {round(emotion_analysis.sadness_score * 100, 1)}%
- Anger:    {round(emotion_analysis.anger_score * 100, 1)}%
- Fear:     {round(emotion_analysis.fear_score * 100, 1)}%
- Love:     {round(emotion_analysis.love_score * 100, 1)}%
- Surprise: {round(emotion_analysis.surprise_score * 100, 1)}%

{'='*40}
This is an automated alert from Scriptly.
Please check on this user as soon as possible.
        """.strip()

        return message

    def send_alert(self, user, emotion_analysis):
        from .models import Alert

        severity = self.determine_severity(emotion_analysis)

        # Only send alerts for medium and above
        if severity == 'low':
            return None

        message = self.build_message(user, emotion_analysis, severity)

        # Get emergency contact email
        contact_email = None
        try:
            contact_email = user.emergency_contact.contact_email
        except Exception:
            contact_email = None

        # Log the alert
        logger.warning(f"ALERT TRIGGERED: {user.email} | {severity} | {emotion_analysis.dominant_emotion}")
        logger.warning(message)

        # Create alert record
        alert = Alert.objects.create(
            user=user,
            emotion_analysis=emotion_analysis,
            severity=severity,
            message=message,
            contact_notified=contact_email,
            status='triggered'
        )

        # Try to send email
        if contact_email:
            try:
                send_mail(
                    subject=f'[SCRIPTLY ALERT - {severity.upper()}] Mental Health Check Required',
                    message=message,
                    from_email=settings.EMAIL_HOST_USER or 'alerts@scriptly.com',
                    recipient_list=[contact_email],
                    fail_silently=True
                )
                alert.status = 'sent'
                alert.save()
                logger.info(f"Alert email sent to {contact_email}")
            except Exception as e:
                alert.status = 'failed'
                alert.save()
                logger.error(f"Failed to send alert email: {e}")
        else:
            # No contact — log only
            alert.status = 'sent'
            alert.save()
            logger.info("No emergency contact — alert logged only")

        return alert

    def resolve_alert(self, alert_id):
        from .models import Alert
        try:
            alert = Alert.objects.get(id=alert_id)
            alert.status = 'resolved'
            alert.resolved_at = timezone.now()
            alert.save()
            return alert
        except Alert.DoesNotExist:
            return None