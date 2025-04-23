from rest_framework import serializers
from .models import Task, Comment
from lib.choices import TaskLifecycleStage, TaskPriority
from apps.users.serializers import UserSerializer
from django.contrib.auth.models import User

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    task = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'text', 'created_at']
        read_only_fields = ['task', 'author', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True, required=False)
    collaborators = UserSerializer(many=True, read_only=True, required=False)
    creator = UserSerializer(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', write_only=True, required=False, allow_null=True
    )
    collaborator_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='collaborators', write_only=True, many=True, required=False
    )

    status = serializers.ChoiceField(choices=TaskLifecycleStage.choices)
    priority = serializers.ChoiceField(choices=TaskPriority.choices)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee',             
            'assignee_id',          
            'collaborators',        
            'collaborator_ids',     
            'creator',              
            'deadline', 'created_at', 'updated_at'
        ]
        read_only_fields = ['creator', 'created_at', 'updated_at']

    def create(self, validated_data):
        
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['creator'] = request.user
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)