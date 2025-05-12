# apps/tasks/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from lib.choices import Role

from .models import Task, TaskHistory
from .serializers import TaskSerializer, TaskHistorySerializer
from apps.users.permissions import (
    IsAdminOrManagerUser,
    IsOwnerOrAdminOrManager
)
from .filters import TaskFilter # Import the new filter class

class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().select_related(
        'assignee__profile', 'creator__profile'
    ).prefetch_related(
        'collaborators__profile'
    )
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter # Use the filterset_class instead of filterset_fields
    search_fields = ['title', 'description']
    ordering_fields = [
        'created_at', 'updated_at', 'deadline', 'priority', 'status', 'title'
    ]
    ordering = ['-priority', '-created_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()

        base_queryset = super().get_queryset()

        if hasattr(user, 'profile') and user.profile.role in [Role.ADMIN, Role.MANAGER]:
            return base_queryset
        else:
            return base_queryset.filter(
                Q(assignee=user) | Q(creator=user) | Q(collaborators=user)
            ).distinct()

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAdminOrManagerUser]
        elif self.action in ['update', 'partial_update', 'destroy', 'assign', 'manage_collaborators']:
            permission_classes = [IsOwnerOrAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrManagerUser], url_path='assign')
    def assign(self, request, pk=None):
        task = self.get_object(); assignee_id = request.data.get('assignee_id')
        if assignee_id is None: return Response({'error': 'assignee_id required.'}, status=status.HTTP_400_BAD_REQUEST)
        try: assignee = User.objects.get(pk=assignee_id); task.assignee = assignee; task.save(); return Response(self.get_serializer(task).data)
        except User.DoesNotExist: return Response({'error': f'User ID {assignee_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAdminOrManagerUser], url_path='collaborators/(?P<user_pk>[^/.]+)')
    def manage_collaborators(self, request, pk=None, user_pk=None):
        task = self.get_object();
        try: user_to_manage = User.objects.get(pk=user_pk)
        except User.DoesNotExist: return Response({'error': f'User ID {user_pk} not found.'}, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
            if user_to_manage in task.collaborators.all(): return Response({'warning': 'User already collaborator.'}, status=status.HTTP_200_OK)
            task.collaborators.add(user_to_manage); return Response({'status': 'Collaborator added.'}, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            if user_to_manage not in task.collaborators.all(): return Response({'error': 'User is not collaborator.'}, status=status.HTTP_400_BAD_REQUEST)
            task.collaborators.remove(user_to_manage); return Response(status=status.HTTP_204_NO_CONTENT)


class TaskHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TaskPagination

    def get_queryset(self):
        task_pk = self.kwargs.get('task_pk'); task = get_object_or_404(Task, pk=task_pk)
        if not IsOwnerOrAdminOrManager().has_object_permission(self.request, self, task):
             raise PermissionDenied("Cannot view history for this task.")
        return TaskHistory.objects.filter(task=task).select_related('user__profile').order_by('-timestamp')

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]