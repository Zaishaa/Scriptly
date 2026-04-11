from django.db import models
from nlp.models import EmotionAnalysis


class Recommendation(models.Model):
    CATEGORY_CHOICES = [
        ('breathing', 'Breathing Exercise'),
        ('motivation', 'Motivational Message'),
        ('calming', 'Calming Technique'),
        ('gratitude', 'Gratitude Exercise'),
        ('physical', 'Physical Activity'),
        ('social', 'Social Connection'),
        ('professional', 'Professional Help'),
    ]

    emotion_analysis = models.ForeignKey(
        EmotionAnalysis,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    action_steps = models.TextField()
    is_crisis_recommendation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.title}"

    class Meta:
        db_table = 'recommendations'