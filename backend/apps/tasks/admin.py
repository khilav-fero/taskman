from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Task, TaskHistory

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'assignee', 'creator', 'created_at', 'deadline')
    list_filter = ('status', 'priority', 'assignee', 'creator')
    search_fields = ('title', 'description')
    filter_horizontal = ('collaborators',)

@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ('task_link', 'user', 'timestamp', 'change_description')
    list_filter = ('user', 'task__title', 'timestamp')
    search_fields = ('change_description', 'user__username', 'task__title')
    readonly_fields = ('task', 'user', 'timestamp', 'change_description')
    ordering = ('-timestamp',)

    @admin.display(description='Task')
    def task_link(self, obj):
        if obj.task:
            link = reverse("admin:tasks_task_change", args=[obj.task.id])
            return format_html('<a href="{}">{}</a>', link, obj.task.title)
        return "Task Deleted"