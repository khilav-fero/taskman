# users/views.py
from django.contrib.auth.models import User
from rest_framework import generics, viewsets, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer
from .permissions import IsAdminUser, IsAdminOrManagerUser
from .models import Profile, Role

class RegisterView(generics.CreateAPIView):
    """ Handles user registration. """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class CustomAuthToken(ObtainAuthToken):
    """ Handles user login and returns token + basic user info. """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={'request': request})
        return Response({'token': token.key, 'user': user_serializer.data})

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint for viewing Users. """
    queryset = User.objects.all().select_related('profile').order_by('-date_joined')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAdminOrManagerUser]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update_role']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser], url_path='update-role')
    def update_role(self, request, pk=None):
        """ Allows Admin to update a user's role. """
        user = self.get_object()
        new_role = request.data.get('role')
        if not new_role or new_role not in Role.values:
            return Response({'error': 'Valid role is required (ADMIN, MANAGER, TEAM_MEMBER).'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            profile = user.profile
            profile.role = new_role
            profile.save()
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
             return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)