# apps/users/filters.py
import django_filters
from django.contrib.auth.models import User
from lib.choices import Role

class UserFilter(django_filters.FilterSet):
    profile__role = django_filters.MultipleChoiceFilter(
        field_name='profile__role',
        choices=Role.choices,
        label='Filter by Role (Select Multiple)'
    )

    class Meta:
        model = User
        fields = ['profile__role', 'is_active']