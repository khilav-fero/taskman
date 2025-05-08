# apps/users/views.py
from django.contrib.auth.models import User
from rest_framework import generics, viewsets, permissions, status, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from .models import Profile
from .serializers import (
    UserSerializer, RegisterSerializer, ProfileSerializer, UserCreateUpdateSerializer
)
from .permissions import IsAdminUser, IsAdminOrManagerUser
from lib.choices import Role
from .filters import UserFilter # Import the custom FilterSet

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={'request': request})
        return Response({'token': token.key, 'user': user_serializer.data})

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('profile').order_by('username')
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter # Use the custom FilterSet class
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'first_name', 'last_name', 'date_joined', 'profile__role']


    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'list': permission_classes = [IsAdminOrManagerUser]
        elif self.action == 'retrieve' or self.action == 'get_current_user': permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'update_role']: permission_classes = [IsAdminUser]
        else: permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def perform_destroy(self, instance):
        if instance == self.request.user: raise PermissionDenied("Administrators cannot delete their own account via the API.")
        instance.delete()

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        if not request.user.is_authenticated: return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(request.user); return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser], url_path='update-role')
    def update_role(self, request, pk=None):
        user = self.get_object(); new_role = request.data.get('role')
        if not new_role or new_role not in Role.values: return Response({'error': f'Valid role required: {Role.values}'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            profile, created = Profile.objects.get_or_create(user=user); profile.role = new_role; profile.save()
            serializer = ProfileSerializer(profile); return Response(serializer.data)
        except Exception as e: return Response({'error': 'An unexpected error occurred updating role.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)