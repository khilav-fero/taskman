from django.db.models.signals import post_save, m2m_changed, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Task, TaskHistory, Comment # Added Comment
from apps.core.models import Notification
from lib.choices import TaskLifecycleStage, TaskPriority

_task_previous_values = {}

@receiver(pre_save, sender=Task)
def store_task_previous_values(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Task.objects.get(pk=instance.pk)
            _task_previous_values[instance.pk] = {
                'title': old.title, 'description': old.description, 'status': old.status,
                'priority': old.priority, 'assignee': old.assignee,
                'assignee_username': old.assignee.username if old.assignee else "Unassigned",
                'deadline': old.deadline,
            }
        except Task.DoesNotExist:
            if instance.pk in _task_previous_values: del _task_previous_values[instance.pk]

@receiver(post_save, sender=Task)
def log_task_changes_and_notify(sender, instance, created, **kwargs):
    user_performing_change = None; changes = []; previous = _task_previous_values.get(instance.pk, {})
    if created:
        creator_name = instance.creator.username if instance.creator else "Unknown"
        changes.append(f"Task created by {creator_name}")
        if instance.assignee and instance.assignee != instance.creator:
            Notification.objects.create(recipient=instance.assignee, message=f"You have been assigned a new task: '{instance.title}'", related_task=instance)
    else:
        current_s_d = instance.get_status_display(); prev_s_d = dict(TaskLifecycleStage.choices).get(previous.get('status'), '?')
        current_p_d = instance.get_priority_display(); prev_p_d = dict(TaskPriority.choices).get(previous.get('priority'), '?')
        if instance.title != previous.get('title'): changes.append(f"Title changed to '{instance.title}'")
        if instance.description != previous.get('description'): changes.append("Description updated")
        if instance.status != previous.get('status'): changes.append(f"Status changed from '{prev_s_d}' to '{current_s_d}'")
        if instance.priority != previous.get('priority'): changes.append(f"Priority changed from '{prev_p_d}' to '{current_p_d}'")
        if instance.assignee != previous.get('assignee'):
             assignee_name = instance.assignee.username if instance.assignee else "Unassigned"
             old_assignee_name = previous.get('assignee_username', "Unassigned")
             changes.append(f"Assignee changed from '{old_assignee_name}' to '{assignee_name}'")
             if instance.assignee and instance.assignee != previous.get('assignee') and instance.assignee != instance.creator:
                 Notification.objects.create(recipient=instance.assignee, message=f"You have been assigned task: '{instance.title}'", related_task=instance)
        if instance.deadline != previous.get('deadline'): deadline_str = instance.deadline.strftime('%Y-%m-%d') if instance.deadline else "None"; changes.append(f"Deadline changed to {deadline_str}")
    for change in changes: TaskHistory.objects.create(task=instance, user=user_performing_change, change_description=change)
    if instance.pk in _task_previous_values: del _task_previous_values[instance.pk]

@receiver(m2m_changed, sender=Task.collaborators.through)
def log_collaborator_changes(sender, instance, action, pk_set, **kwargs):
    user_performing_change = None; task = instance
    if action == "post_add":
        users = User.objects.filter(pk__in=pk_set)
        for u in users:
            TaskHistory.objects.create(task=task, user=user_performing_change, change_description=f"Added {u.username} as collaborator")
            if u != task.creator and u != task.assignee: # Avoid double-notifying if already creator/assignee
                Notification.objects.create(recipient=u, message=f"You were added as a collaborator on task: '{task.title}'", related_task=task)
    elif action == "post_remove":
        users = User.objects.filter(pk__in=pk_set)
        for u in users:
             TaskHistory.objects.create(task=task, user=user_performing_change, change_description=f"Removed {u.username} as collaborator")
             Notification.objects.create(recipient=u, message=f"You were removed as a collaborator from task: '{task.title}'", related_task=task)

@receiver(post_save, sender=Comment)
def create_comment_notification_and_history(sender, instance, created, **kwargs):
    user_performing_change = instance.author
    task = instance.task
    if created:
        TaskHistory.objects.create(
            task=task,
            user=user_performing_change,
            change_description=f"Comment added by {user_performing_change.username}: '{instance.text[:50]}...'"
        )
        recipients = set()
        if task.creator and task.creator != user_performing_change: recipients.add(task.creator)
        if task.assignee and task.assignee != user_performing_change: recipients.add(task.assignee)
        for collaborator in task.collaborators.all():
            if collaborator != user_performing_change: recipients.add(collaborator)
        message = f"{user_performing_change.username} commented on task '{task.title}'"
        for user_recipient in recipients:
            Notification.objects.create(recipient=user_recipient, message=message, related_task=task)