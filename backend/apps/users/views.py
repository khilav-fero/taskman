# from django.contrib.auth.models import User
# from rest_framework import generics, viewsets, permissions, status
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authtoken.models import Token
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from .models import Profile
# from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer
# from .permissions import IsAdminUser, IsAdminOrManagerUser
# from lib.choices import Role

# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     permission_classes = [permissions.AllowAny] 
#     serializer_class = RegisterSerializer

# class CustomAuthToken(ObtainAuthToken):
#     """ Custom login view to include user data in response """
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         user_serializer = UserSerializer(user, context={'request': request}) 
#         return Response({'token': token.key, 'user': user_serializer.data})

# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """ ViewSet for listing and retrieving users """
#     queryset = User.objects.all().select_related('profile').order_by('-date_joined')
#     serializer_class = UserSerializer

#     def get_permissions(self):
#         """ Dynamic permissions based on action """
#         if self.action == 'list': permission_classes = [IsAdminOrManagerUser]
#         elif self.action == 'retrieve': permission_classes = [permissions.IsAuthenticated]
#         elif self.action in ['update_role']: permission_classes = [IsAdminUser] 
#         else: permission_classes = [permissions.IsAdminUser] 
#         return [permission() for permission in permission_classes]

#     @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser], url_path='update-role')
#     def update_role(self, request, pk=None):
#         """ Custom action for Admins to update user roles """
#         user = self.get_object() 
#         new_role = request.data.get('role')
#         if not new_role or new_role not in Role.values:
#             return Response({'error': f'Valid role required: {Role.values}'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             profile, created = Profile.objects.get_or_create(user=user)
#             profile.role = new_role
#             profile.save()
#             serializer = ProfileSerializer(profile) 
#             return Response(serializer.data)
#         except Exception as e: 
#             return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# apps/users/views.py
from django.contrib.auth.models import User
from rest_framework import generics, viewsets, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action # Make sure this is imported
from .models import Profile
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer
from .permissions import IsAdminUser, IsAdminOrManagerUser
from lib.choices import Role

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

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().select_related('profile').order_by('-date_joined')
    serializer_class = UserSerializer

    def get_permissions(self):
        # Ensure 'get_current_user' action has appropriate permissions
        if self.action == 'list':
            permission_classes = [IsAdminOrManagerUser]
        elif self.action == 'retrieve' or self.action == 'get_current_user': # <<< Add get_current_user here
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'update_role':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAdminUser] # Default restrictive
        return [permission() for permission in permission_classes]

    # --- VERIFY THIS ACTION EXISTS AND IS CORRECT ---
    @action(detail=False, methods=['get'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        """
        Returns details for the currently authenticated user.
        Accessible via /api/users/me/
        """
        # Check if user is authenticated (should be guaranteed by permission_classes, but safe check)
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    # --- END VERIFICATION ---

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser], url_path='update-role')
    def update_role(self, request, pk=None):
        user = self.get_object(); new_role = request.data.get('role')
        if not new_role or new_role not in Role.values: return Response({'error': f'Valid role required: {Role.values}'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            profile, created = Profile.objects.get_or_create(user=user); profile.role = new_role; profile.save()
            serializer = ProfileSerializer(profile); return Response(serializer.data)
        except Exception as e: return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)