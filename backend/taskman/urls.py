# taskman/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

# Import views using the apps prefix
from apps.users import views as user_views
from apps.tasks import views as task_views

# --- Top Level Router ---
router = DefaultRouter()
router.register(r'users', user_views.UserViewSet, basename='user')
router.register(r'tasks', task_views.TaskViewSet, basename='task')

# --- Nested Router for Comments ---
tasks_router = nested_routers.NestedDefaultRouter(router, r'tasks', lookup='task')
tasks_router.register(r'comments', task_views.CommentViewSet, basename='task-comments')


urlpatterns = [
    path('admin/', admin.site.urls),

    # --- API URLs ---
    path('api/', include(router.urls)),
    path('api/', include(tasks_router.urls)),

    # Standalone authentication endpoints
    path('api/register/', user_views.RegisterView.as_view(), name='register'),
    path('api/login/', user_views.CustomAuthToken.as_view(), name='login'),

    # Browsable API login/logout (uses Session Auth)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]