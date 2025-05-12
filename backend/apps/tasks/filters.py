import django_filters
from .models import Task, User

class TaskFilter(django_filters.FilterSet):
    deadline__gte = django_filters.DateFilter(field_name='deadline', lookup_expr='gte')
    deadline__lte = django_filters.DateFilter(field_name='deadline', lookup_expr='lte')
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    updated_at__gte = django_filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_at__lte = django_filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    
    collaborators = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        field_name='collaborators',
        to_field_name='id',
        conjoined=False
    )

    class Meta:
        model = Task
        fields = {
            'status': ['exact', 'in'],
            'priority': ['exact', 'gte', 'lte', 'in'],
            'assignee': ['exact', 'in'],
            'creator': ['exact', 'in'],
            'deadline': ['exact'],
            'created_at': ['exact'],
            'updated_at': ['exact'],
        }