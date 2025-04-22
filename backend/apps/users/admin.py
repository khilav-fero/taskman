from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Role

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'
    fields = ('role',)

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_select_related = ('profile',)

    @admin.display(description='Role')
    def get_role(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.get_role_display()
        return None

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)