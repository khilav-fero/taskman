# apps/users/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile
from lib.choices import Role

# --- Profile Serializer (For READ) ---
class ProfileSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Role.choices, read_only=True)
    class Meta: model = Profile; fields = ['role']

# --- User Serializer (For READ) ---
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta: model = User; fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'is_staff', 'date_joined']; read_only_fields = ['is_staff', 'date_joined', 'profile']

# --- Register Serializer ---
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, min_length=8)
    class Meta: model = User; fields = ['username', 'password', 'email', 'first_name', 'last_name']
    def create(self, validated_data): user = User.objects.create_user(**validated_data); return user

# --- Profile Serializer (For WRITE) ---
class ProfileWriteSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Role.choices, required=False)
    class Meta: model = Profile; fields = ['role']

# --- User Create/Update Serializer (CORRECTED) ---
class UserCreateUpdateSerializer(serializers.ModelSerializer):
    # --- REMOVED source='profile' ---
    profile = ProfileWriteSerializer(required=False)
    # --- END REMOVAL ---
    password = serializers.CharField(write_only=True, required=False, allow_null=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'profile']
        read_only_fields = ['id']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        if not password: raise serializers.ValidationError({'password': 'Password is required for creating a user.'})
        user = User.objects.create_user(password=password, **validated_data)
        if profile_data and hasattr(user, 'profile'):
            user.profile.role = profile_data.get('role', Role.TEAM_MEMBER)
            user.profile.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('profile', None)
        validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        return instance