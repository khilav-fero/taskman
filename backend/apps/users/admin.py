from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile 


#th e verbose name has been set as user profile for a reason, in this case each user has only one profile so well, user profile is technically the right term to use
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
        #in case profile somehow doesn't exist
        return getattr(getattr(instance, 'profile', None), 'get_role_display', lambda: None)()


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)