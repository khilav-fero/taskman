from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Role

class ProfileSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Role.choices)
    class Meta:
        model = Profile
        fields = ['role']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'is_staff', 'date_joined']
        read_only_fields = ['is_staff', 'date_joined', 'profile']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, min_length=8)
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
    def create(self, validated_data):
        user = User.objects.create_user( 
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user