from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'severity', 'status',
        'contact_notified', 'triggered_at'
    )
    list_filter = ('severity', 'status')
    search_fields = ('user__email',)