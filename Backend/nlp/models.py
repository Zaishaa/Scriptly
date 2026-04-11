from django.db import models
from journal.models import JournalEntry


class EmotionAnalysis(models.Model):
    EMOTION_CHOICES = [
        ('joy', 'Joy'),
        ('sadness', 'Sadness'),
        ('anger', 'Anger'),
        ('fear', 'Fear'),
        ('love', 'Love'),
        ('surprise', 'Surprise'),
    ]

    journal_entry = models.OneToOneField(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='emotion_analysis'
    )
    dominant_emotion = models.CharField(
        max_length=20,
        choices=EMOTION_CHOICES
    )
    joy_score = models.FloatField(default=0.0)
    sadness_score = models.FloatField(default=0.0)
    anger_score = models.FloatField(default=0.0)
    fear_score = models.FloatField(default=0.0)
    love_score = models.FloatField(default=0.0)
    surprise_score = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    is_crisis = models.BooleanField(default=False)
    raw_text = models.TextField()
    processed_text = models.TextField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.journal_entry.user.username} - {self.dominant_emotion} ({self.confidence_score:.2f})"

    class Meta:
        db_table = 'emotion_analysis'