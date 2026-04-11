from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category',
        'is_crisis_recommendation', 'created_at'
    )
    list_filter = ('category', 'is_crisis_recommendation')