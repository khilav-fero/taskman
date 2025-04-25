# apps/core/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message_snippet', 'read', 'timestamp', 'task_link')
    list_filter = ('read', 'recipient', 'timestamp')
    search_fields = ('message', 'recipient__username', 'related_task__title')
    list_editable = ('read',)
    readonly_fields = ('timestamp', 'recipient', 'message', 'related_task')
    ordering = ('-timestamp',)

    @admin.display(description='Message Snippet')
    def message_snippet(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message

    @admin.display(description='Related Task')
    def task_link(self, obj):
        if obj.related_task:
            link = reverse("admin:tasks_task_change", args=[obj.related_task.id])
            return format_html('<a href="{}">{}</a>', link, obj.related_task.title)
        return "-"