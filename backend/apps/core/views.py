from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification
from .serializers import NotificationSerializer
from apps.tasks.views import TaskPagination

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TaskPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['read']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related(
            'recipient__profile', 'related_task'
        ).order_by('-timestamp')

    @action(detail=True, methods=['post'], url_path='mark_as_read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.read:
            notification.read = True
            notification.save(update_fields=['read'])
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='mark_all_as_read')
    def mark_all_as_read(self, request):
        queryset = self.get_queryset()
        updated_count = queryset.filter(read=False).update(read=True)
        return Response({'status': f'{updated_count} notifications marked as read.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='unread_count')
    def unread_count(self, request):
        count = self.get_queryset().filter(read=False).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)