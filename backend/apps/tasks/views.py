from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
# get_object_or_404 used for returning a clean http404 instead of the default does not exist 
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied

from .models import Task, TaskHistory
from .serializers import TaskSerializer, TaskHistorySerializer
from apps.users.permissions import (
    IsAdminOrManagerUser,
    IsOwnerOrAdminOrManager
)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().select_related(
        'assignee__profile', 'creator__profile'
    ).prefetch_related(
        'collaborators__profile'
    ).order_by('-priority', '-created_at')
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assignee', 'creator', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = [
        'created_at', 'updated_at', 'deadline', 'priority', 'status', 'title'
    ]

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAdminOrManagerUser]
        elif self.action in [
            'update', 'partial_update', 'destroy',
            'assign', 'manage_collaborators'
        ]:
            permission_classes = [IsOwnerOrAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(
        detail=True, methods=['post'],
        permission_classes=[IsAdminOrManagerUser], url_path='assign'
    )
    def assign(self, request, pk=None):
        task = self.get_object()
        assignee_id = request.data.get('assignee_id')
        if assignee_id is None:
            return Response(
                {'error': 'assignee_id required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            assignee = User.objects.get(pk=assignee_id)
            task.assignee = assignee
            task.save()
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': f'User ID {assignee_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAdminOrManagerUser],
        url_path='collaborators/(?P<user_pk>[^/.]+)'
    )
    def manage_collaborators(self, request, pk=None, user_pk=None):
        task = self.get_object()
        try:
            user_to_manage = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response(
                {'error': f'User ID {user_pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'POST':
            if user_to_manage in task.collaborators.all():
                return Response(
                    {'warning': 'User already collaborator.'},
                    status=status.HTTP_200_OK
                )
            task.collaborators.add(user_to_manage)
            return Response(
                {'status': 'Collaborator added.'},
                status=status.HTTP_200_OK
            )
        elif request.method == 'DELETE':
            if user_to_manage not in task.collaborators.all():
                return Response(
                    {'error': 'User is not collaborator.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            task.collaborators.remove(user_to_manage)
            return Response(status=status.HTTP_204_NO_CONTENT)


class TaskHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_pk = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_pk)
        if not IsOwnerOrAdminOrManager().has_object_permission(self.request, self, task):
            raise PermissionDenied("Cannot view history for this task.")
        return TaskHistory.objects.filter(task=task).select_related(
            'user__profile'
        ).order_by('-timestamp')

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]