# Serializers.py is used to convert complex data types, such as querysets and model instances, to native Python data types that can then be easily rendered into JSON, XML or other content types.
from django.contrib.auth.models import User
import faker
from .models import UserProfile
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    # Allow the input of username when creating the user profile
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = UserProfile        
        fields = ['user', 'username', 'password', 'email', 'phone_number', 'carrier', 'monthly_payment']
        extra_kwargs = {
            'user': {'read_only': True},  # user field is read-only in response
            'phone_number': {'required': False},
            'carrier': {'required': False},
            'monthly_payment': {'required': False}
        }

    def create(self, validated_data):
        # Extract user-related fields from the validated data
        username = validated_data.pop('username')  # Username is now writable, so we extract it
        password = validated_data.pop('password')
        email = validated_data.pop('email', None)  # Provide a default None if email is not present

        # Create a new User instance, handle the case where email is optional
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # Now create the UserProfile and assign the created User to it
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        user_profile.save()
        return user_profile
    
    def to_representation(self, instance):
        """Customize the representation to include the username in the response."""
        representation = super().to_representation(instance)
        representation['username'] = instance.user.username  # Display the username in the output
        return representation