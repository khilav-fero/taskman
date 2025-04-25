# apps/core/models.py
from django.db import models
from django.contrib.auth.models import User
from apps.tasks.models import Task

class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        verbose_name="Recipient",
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField("Message")
    read = models.BooleanField("Read Status", default=False)
    timestamp = models.DateTimeField("Timestamp", auto_now_add=True)
    related_task = models.ForeignKey(
        Task,
        verbose_name="Related Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_notifications'
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        status = "Read" if self.read else "Unread"
        return f"To {self.recipient.username}: {self.message[:60]}... ({status})"