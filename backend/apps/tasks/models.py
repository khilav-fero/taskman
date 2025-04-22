from django.db import models
from django.contrib.auth.models import User

class TaskLifecycleStage(models.TextChoices):
    TO_DO = 'TODO', 'To-Do'
    IN_PROGRESS = 'INPROGRESS', 'In-Progress'
    CODE_REVIEW = 'REVIEW', 'Code Review'
    DONE = 'DONE', 'Done'

class TaskPriority(models.IntegerChoices):
    LOW = 1, 'Low'
    MEDIUM = 2, 'Medium'
    HIGH = 3, 'High'
    URGENT = 4, 'Urgent'

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=TaskLifecycleStage.choices, default=TaskLifecycleStage.TO_DO)
    priority = models.IntegerField(choices=TaskPriority.choices, default=TaskPriority.MEDIUM)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_tasks', blank=True, null=True)
    collaborators = models.ManyToManyField(User, related_name='collaborating_tasks', blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    deadline = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"'{self.title}' ({self.get_status_display()})"
    class Meta: ordering = ['-priority', '-created_at']

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        short_text = (self.text[:75] + '...') if len(self.text) > 75 else self.text
        return f"Comment by {self.author.username} on '{self.task.title}': {short_text}"

    class Meta:
        ordering = ['created_at'] # Showing oldest comments first

