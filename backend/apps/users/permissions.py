from rest_framework import permissions
from .models import Profile 
from lib.choices import Role 
# have to use absolute path from apps
from apps.tasks.models import Task, Comment

class IsAdminUser(permissions.BasePermission):
    message = "Access restricted to Admin users."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == Role.ADMIN)

class IsManagerUser(permissions.BasePermission):
    message = "Access restricted to Manager users."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == Role.MANAGER)

class IsAdminOrManagerUser(permissions.BasePermission):
    message = "Access restricted to Admin or Manager users."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'profile') and
                    request.user.profile.role in [Role.ADMIN, Role.MANAGER])

# --- Object-Level Permissions ---
class IsOwnerOrAdminOrManager(permissions.BasePermission):
    message = "You do not have permission to perform this action on this object."
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated: return False 
        if hasattr(request.user, 'profile') and request.user.profile.role in [Role.ADMIN, Role.MANAGER]:
            return True 

        if isinstance(obj, Task):
            return (obj.assignee == request.user or
                    obj.creator == request.user or
                    request.user in obj.collaborators.all())
        if isinstance(obj, Comment):
             parent_task = obj.task
             return (parent_task.assignee == request.user or
                     parent_task.creator == request.user or
                     request.user in parent_task.collaborators.all())
        return False

class IsCommentAuthorOrAdminOrManager(permissions.BasePermission):
    message = "You can only modify or delete your own comments."
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated: return False # Must be logged in
        if not isinstance(obj, Comment): return False

        if hasattr(request.user, 'profile') and request.user.profile.role in [Role.ADMIN, Role.MANAGER]:
            return True 

        return obj.author == request.user 