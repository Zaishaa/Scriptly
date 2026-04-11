from django.contrib import admin
from .models import JournalEntry


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'mood', 'is_analyzed', 'created_at')
    list_filter = ('mood', 'is_analyzed', 'created_at')
    search_fields = ('user__email', 'title', 'content')