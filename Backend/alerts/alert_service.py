import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class AlertService:

    def determine_severity(self, emotion_analysis):
        sadness = emotion_analysis.sadness_score
        fear = emotion_analysis.fear_score
        anger = emotion_analysis.anger_score
        negative_score = (sadness + fear + anger) * 100

        if emotion_analysis.is_crisis:
            return 'critical'
        elif negative_score >= 85:
            return 'high'
        elif negative_score >= 60:
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
        from django.core.mail import EmailMultiAlternatives

        severity = self.determine_severity(emotion_analysis)

        if severity == 'low':
            return None

        message = self.build_message(user, emotion_analysis, severity)

        contact_email = None
        try:
            contact_email = user.emergency_contact.contact_email
        except Exception:
            contact_email = None

        logger.warning(f"ALERT TRIGGERED: {user.email} | {severity} | {emotion_analysis.dominant_emotion}")
        logger.warning(message)

        alert = Alert.objects.create(
            user=user,
            emotion_analysis=emotion_analysis,
            severity=severity,
            message=message,
            contact_notified=contact_email,
            status='triggered'
        )

        if contact_email:
            try:
                emotion = emotion_analysis.dominant_emotion
                confidence = round(emotion_analysis.confidence_score * 100, 1)
                entry_title = emotion_analysis.journal_entry.title
                timestamp = emotion_analysis.analyzed_at.strftime('%Y-%m-%d %H:%M')

                severity_color = {
                    'critical': '#dc2626',
                    'high': '#ea580c',
                    'medium': '#d97706',
                    'low': '#16a34a'
                }.get(severity, '#6b7280')

                def bar(score):
                    return f"{round(score * 100)}%"

                html_message = f"""
<html>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:Arial,sans-serif;">
  <div style="max-width:580px;margin:30px auto;background:white;
              border-radius:16px;overflow:hidden;
              box-shadow:0 4px 20px rgba(0,0,0,0.1);">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1e293b,#334155);
                padding:30px;text-align:center;">
      <h1 style="color:white;margin:0;font-size:24px;letter-spacing:1px;">
        🧠 Scriptly
      </h1>
      <p style="color:#94a3b8;margin:6px 0 0;font-size:13px;">
        Mental Health Journal
      </p>
    </div>

    <!-- Alert Badge -->
    <div style="background:{severity_color};padding:16px;text-align:center;">
      <span style="color:white;font-size:18px;font-weight:bold;letter-spacing:1px;">
        ⚠️ {severity.upper()} ALERT
        {'— 🚨 CRISIS DETECTED' if emotion_analysis.is_crisis else ''}
      </span>
    </div>

    <!-- Body -->
    <div style="padding:30px;">
      <p style="color:#374151;font-size:15px;margin-top:0;">Hi there,</p>
      <p style="color:#374151;font-size:15px;">
        This is an automated alert from <strong>Scriptly</strong>.
        Your contact <strong>{user.username}</strong>
        (<a href="mailto:{user.email}" style="color:#4f46e5;">{user.email}</a>)
        has submitted a journal entry that our AI has flagged for emotional distress.
      </p>

      <!-- Info Box -->
      <div style="background:#f8fafc;border:1px solid #e2e8f0;
                  border-radius:10px;padding:20px;margin:20px 0;">
        <table width="100%" cellpadding="6">
          <tr>
            <td style="color:#64748b;font-size:13px;width:140px;">📅 Time</td>
            <td style="color:#1e293b;font-size:13px;font-weight:bold;">{timestamp}</td>
          </tr>
          <tr>
            <td style="color:#64748b;font-size:13px;">📝 Entry</td>
            <td style="color:#1e293b;font-size:13px;font-weight:bold;">"{entry_title}"</td>
          </tr>
          <tr>
            <td style="color:#64748b;font-size:13px;">🎭 Emotion</td>
            <td style="color:{severity_color};font-size:13px;font-weight:bold;">
              {emotion.upper()} ({confidence}%)
            </td>
          </tr>
          <tr>
            <td style="color:#64748b;font-size:13px;">🔴 Severity</td>
            <td style="color:{severity_color};font-size:13px;font-weight:bold;">
              {severity.upper()}
            </td>
          </tr>
        </table>
      </div>

      <!-- Emotion Breakdown -->
      <h3 style="color:#1e293b;font-size:15px;margin-bottom:12px;">
        📊 Emotion Breakdown
      </h3>

      <!-- Joy -->
      <div style="margin-bottom:10px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
          <span style="font-size:13px;color:#374151;">😊 Joy</span>
          <span style="font-size:13px;color:#374151;">{bar(emotion_analysis.joy_score)}</span>
        </div>
        <div style="background:#e5e7eb;border-radius:999px;height:8px;">
          <div style="background:#22c55e;height:8px;border-radius:999px;
                      width:{bar(emotion_analysis.joy_score)};"></div>
        </div>
      </div>

      <!-- Sadness -->
      <div style="margin-bottom:10px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
          <span style="font-size:13px;color:#374151;">😢 Sadness</span>
          <span style="font-size:13px;color:#374151;">{bar(emotion_analysis.sadness_score)}</span>
        </div>
        <div style="background:#e5e7eb;border-radius:999px;height:8px;">
          <div style="background:#3b82f6;height:8px;border-radius:999px;
                      width:{bar(emotion_analysis.sadness_score)};"></div>
        </div>
      </div>

      <!-- Anger -->
      <div style="margin-bottom:10px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
          <span style="font-size:13px;color:#374151;">😠 Anger</span>
          <span style="font-size:13px;color:#374151;">{bar(emotion_analysis.anger_score)}</span>
        </div>
        <div style="background:#e5e7eb;border-radius:999px;height:8px;">
          <div style="background:#ef4444;height:8px;border-radius:999px;
                      width:{bar(emotion_analysis.anger_score)};"></div>
        </div>
      </div>

      <!-- Fear -->
      <div style="margin-bottom:10px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
          <span style="font-size:13px;color:#374151;">😨 Fear</span>
          <span style="font-size:13px;color:#374151;">{bar(emotion_analysis.fear_score)}</span>
        </div>
        <div style="background:#e5e7eb;border-radius:999px;height:8px;">
          <div style="background:#f97316;height:8px;border-radius:999px;
                      width:{bar(emotion_analysis.fear_score)};"></div>
        </div>
      </div>

      <!-- Love -->
      <div style="margin-bottom:10px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
          <span style="font-size:13px;color:#374151;">❤️ Love</span>
          <span style="font-size:13px;color:#374151;">{bar(emotion_analysis.love_score)}</span>
        </div>
        <div style="background:#e5e7eb;border-radius:999px;height:8px;">
          <div style="background:#ec4899;height:8px;border-radius:999px;
                      width:{bar(emotion_analysis.love_score)};"></div>
        </div>
      </div>

      <!-- Surprise -->
      <div style="margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
          <span style="font-size:13px;color:#374151;">😲 Surprise</span>
          <span style="font-size:13px;color:#374151;">{bar(emotion_analysis.surprise_score)}</span>
        </div>
        <div style="background:#e5e7eb;border-radius:999px;height:8px;">
          <div style="background:#a855f7;height:8px;border-radius:999px;
                      width:{bar(emotion_analysis.surprise_score)};"></div>
        </div>
      </div>

      <!-- Action Box -->
      <div style="background:#fef3c7;border:1px solid #fcd34d;
                  border-radius:10px;padding:16px;margin-top:10px;">
        <p style="margin:0;color:#92400e;font-size:14px;">
          💛 <strong>Please reach out</strong> to {user.username}
          as soon as possible and check in on how they are feeling.
        </p>
      </div>
    </div>

    <!-- Footer -->
    <div style="background:#f8fafc;padding:20px;text-align:center;
                border-top:1px solid #e2e8f0;">
      <p style="color:#94a3b8;font-size:12px;margin:0;">
        This is an automated message from Scriptly.<br>
        Please do not reply to this email.
      </p>
    </div>

  </div>
</body>
</html>
                """

                email = EmailMultiAlternatives(
                    subject=f'[SCRIPTLY ALERT - {severity.upper()}] '
                            f'Mental Health Check Required for {user.username}',
                    body=message,
                    from_email=f"Scriptly Alerts <{settings.EMAIL_HOST_USER}>",
                    to=[contact_email]
                )
                email.attach_alternative(html_message, "text/html")
                email.send()

                alert.status = 'sent'
                alert.save()
                logger.info(f"Alert email sent to {contact_email}")

            except Exception as e:
                alert.status = 'failed'
                alert.save()
                logger.error(f"Failed to send alert email: {e}")
        else:
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