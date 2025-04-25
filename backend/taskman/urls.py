from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from apps.users import views as user_views
from apps.tasks import views as task_views
from apps.core import views as core_views

router = DefaultRouter()
router.register(r'users', user_views.UserViewSet, basename='user')
router.register(r'tasks', task_views.TaskViewSet, basename='task')
router.register(r'notifications', core_views.NotificationViewSet, basename='notification')

tasks_router = nested_routers.NestedDefaultRouter(router, r'tasks', lookup='task')
tasks_router.register(r'history', task_views.TaskHistoryViewSet, basename='task-history')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include(tasks_router.urls)),
    path('api/register/', user_views.RegisterView.as_view(), name='register'),
    path('api/login/', user_views.CustomAuthToken.as_view(), name='login'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

admin.site.site_header = "Taskman Admin"
admin.site.site_title = "Taskman Admin Portal"
admin.site.index_title = "Welcome to the Taskman Administration Portal"

from django.contrib.auth.models import Group

admin.site.unregister(Group)
