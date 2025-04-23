from django.db import models


class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    MANAGER = 'MANAGER', 'Manager'
    TEAM_MEMBER = 'TEAM_MEMBER', 'Team Member'

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