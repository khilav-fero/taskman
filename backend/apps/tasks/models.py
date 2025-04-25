from django.db import models
from django.contrib.auth.models import User
from lib.choices import TaskLifecycleStage, TaskPriority

class Task(models.Model):
    title = models.CharField("Title", max_length=200)
    description = models.TextField("Description", blank=True, null=True)
    status = models.CharField(
        "Status",
        max_length=10,
        choices=TaskLifecycleStage.choices,
        default=TaskLifecycleStage.TO_DO
    )
    priority = models.IntegerField(
        "Priority",
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM
    )
    assignee = models.ForeignKey(
        User,
        verbose_name="Assignee",
        on_delete=models.SET_NULL,
        related_name='assigned_tasks',
        blank=True,
        null=True
    )
    collaborators = models.ManyToManyField(
        User,
        verbose_name="Collaborators",
        related_name='collaborating_tasks',
        blank=True
    )
    creator = models.ForeignKey(
        User,
        verbose_name="Creator",
        on_delete=models.SET_NULL,
        related_name='created_tasks',
        null=True
    )
    deadline = models.DateField("Deadline", blank=True, null=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    updated_at = models.DateTimeField("Updated At", auto_now=True)

    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"'{self.title}' ({self.get_status_display()})"


class TaskHistory(models.Model):
    task = models.ForeignKey(
        Task,
        verbose_name="Task",
        on_delete=models.CASCADE,
        related_name='history'
    )
    user = models.ForeignKey(
        User,
        verbose_name="User Performing Change",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField("Timestamp", auto_now_add=True)
    change_description = models.CharField("Change Description", max_length=255)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Task History Entry"
        verbose_name_plural = "Task History Entries"

    def __str__(self):
        user_display = self.user.username if self.user else "System/Unknown"
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')}: {self.change_description} (by {user_display}) on Task {self.task_id}"