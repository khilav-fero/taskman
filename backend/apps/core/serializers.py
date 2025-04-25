# apps/core/serializers.py
from rest_framework import serializers
from .models import Notification
from apps.users.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(read_only=True)
    related_task = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'message',
            'read',
            'timestamp',
            'related_task'
        ]
        read_only_fields = [
            'id', 'recipient', 'message', 'timestamp', 'related_task'
        ]
