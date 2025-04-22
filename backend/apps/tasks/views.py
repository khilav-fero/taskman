from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied 
from .models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer
from users.permissions import (
    IsAdminOrManagerUser,
    IsOwnerOrAdminOrManager,
    IsCommentAuthorOrAdminOrManager 
)

class TaskViewSet(viewsets.ModelViewSet):
    """ API endpoint for Tasks CRUD operations and custom actions (assign, collaborators). """
    queryset = Task.objects.all().select_related(
        'assignee__profile', 'creator__profile'
    ).prefetch_related(
        'collaborators__profile'
    ).order_by('-priority', '-created_at')
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assignee', 'creator', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'deadline', 'priority', 'status', 'title']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAdminOrManagerUser]
        elif self.action in ['update', 'partial_update', 'destroy', 'assign', 'manage_collaborators']:
            permission_classes = [IsOwnerOrAdminOrManager]
        else: # list, retrieve
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save() # Creator set in serializer context

    def perform_update(self, serializer):
        serializer.save() # Simple update

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrManagerUser], url_path='assign')
    def assign(self, request, pk=None):
        task = self.get_object()
        assignee_id = request.data.get('assignee_id')
        if assignee_id is None: return Response({'error': 'assignee_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try: assignee = User.objects.get(pk=assignee_id)
        except User.DoesNotExist: return Response({'error': f'User with ID {assignee_id} not found.'}, status=status.HTTP_404_NOT_FOUND)
        task.assignee = assignee
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAdminOrManagerUser], url_path='collaborators/(?P<user_pk>[^/.]+)')
    def manage_collaborators(self, request, pk=None, user_pk=None):
        task = self.get_object()
        try: user_to_manage = User.objects.get(pk=user_pk)
        except User.DoesNotExist: return Response({'error': f'User with ID {user_pk} not found.'}, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
            if user_to_manage in task.collaborators.all(): return Response({'warning': f'User {user_to_manage.username} is already a collaborator.'}, status=status.HTTP_200_OK)
            task.collaborators.add(user_to_manage)
            return Response({'status': f'User {user_to_manage.username} added as collaborator.'}, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            if user_to_manage not in task.collaborators.all(): return Response({'error': f'User {user_to_manage.username} is not a collaborator.'}, status=status.HTTP_400_BAD_REQUEST)
            task.collaborators.remove(user_to_manage)
            return Response({'status': f'User {user_to_manage.username} removed as collaborator.'}, status=status.HTTP_204_NO_CONTENT)

class CommentViewSet(viewsets.ModelViewSet):
    """ API endpoint for Comments nested under Tasks. """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ Filter comments based on the task_pk in the URL. """
        task_pk = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_pk)

        return Comment.objects.filter(task=task).select_related('author__profile').order_by('created_at')

    def perform_create(self, serializer):
        """ Set author and task automatically, check permission on parent task. """
        task_pk = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_pk)
        if not IsOwnerOrAdminOrManager().has_object_permission(self.request, self, task):
             raise PermissionDenied("You do not have permission to comment on this task.")
        serializer.save(author=self.request.user, task=task)

    def get_permissions(self):
        """ Set specific permissions for update/destroy actions on comments. """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsCommentAuthorOrAdminOrManager]
        elif self.action == 'create':
             permission_classes = [permissions.IsAuthenticated]
        else: 
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

