from rest_framework import permissions
from .models import Role, Profile
from tasks.models import Task, Comment

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

class IsOwnerOrAdminOrManager(permissions.BasePermission):
    """
    Check if user is Admin/Manager OR related to the Task object.
    Also used to check if user can comment on a Task.
    """
    message = "You do not have permission to perform this action on this object."
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and hasattr(request.user, 'profile') and \
           request.user.profile.role in [Role.ADMIN, Role.MANAGER]:
            return True

        if isinstance(obj, Task):

            return (obj.assignee == request.user or
                    obj.creator == request.user or
                    request.user in obj.collaborators.all())

        if isinstance(obj, Comment):
             # Check if user is related to the parent task
             parent_task = obj.task
             return (parent_task.assignee == request.user or
                     parent_task.creator == request.user or
                     request.user in parent_task.collaborators.all())


        return False # Deny for other object types or unrelated users

class IsCommentAuthorOrAdminOrManager(permissions.BasePermission):
    """ Check if user is Admin/Manager OR the author of the comment for update/delete. """
    message = "You can only modify or delete your own comments."
    def has_object_permission(self, request, view, obj):
        # Ensure obj is a Comment instance
        if not isinstance(obj, Comment):
            return False # Should not happen if applied correctly

        if request.user.is_authenticated and hasattr(request.user, 'profile') and \
           request.user.profile.role in [Role.ADMIN, Role.MANAGER]:
            return True

        return obj.author == request.user