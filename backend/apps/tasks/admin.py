from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Task, Comment

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'assignee', 'creator', 'created_at', 'deadline')
    list_filter = ('status', 'priority', 'assignee', 'creator')
    search_fields = ('title', 'description')
    filter_horizontal = ('collaborators',) # Better UI for M2M

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task_link', 'author', 'text_snippet', 'created_at')
    list_filter = ('author', 'task__title')
    search_fields = ('text', 'author__username', 'task__title')
    readonly_fields = ('created_at',) # Usually don't edit timestamp

    @admin.display(description='Comment Snippet')
    def text_snippet(self, obj):
        return (obj.text[:50] + '...') if len(obj.text) > 50 else obj.text

    @admin.display(description='Task')
    def task_link(self, obj):
        # Link to parent task in admin
        link = reverse("admin:tasks_task_change", args=[obj.task.id]) # Use app_label:model_name_change
        return format_html('<a href="{}">{}</a>', link, obj.task.title)