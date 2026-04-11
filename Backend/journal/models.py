from django.db import models
from accounts.models import User


class JournalEntry(models.Model):
    MOOD_CHOICES = [
        ('great', 'Great'),
        ('good', 'Good'),
        ('okay', 'Okay'),
        ('bad', 'Bad'),
        ('terrible', 'Terrible'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='journal_entries'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    mood = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES,
        blank=True,
        null=True
    )
    is_analyzed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} - {self.created_at.date()}"

    class Meta:
        db_table = 'journal_entries'
        ordering = ['-created_at']