from django.db import models
from accounts.models import User
from nlp.models import EmotionAnalysis


class Alert(models.Model):
    ALERT_STATUS_CHOICES = [
        ('triggered', 'Triggered'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('resolved', 'Resolved'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    emotion_analysis = models.ForeignKey(
        EmotionAnalysis,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=ALERT_STATUS_CHOICES,
        default='triggered'
    )
    message = models.TextField()
    contact_notified = models.EmailField(blank=True, null=True)
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.severity} - {self.status}"

    class Meta:
        db_table = 'alerts'
        ordering = ['-triggered_at']