from rest_framework.serializers import ModelSerializer, EmailField, CharField, ValidationError
from django.contrib.auth.models import User
from .models import Task



class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'user', 'title', 'description', 'completed', 'created_at']


class ForgotPasswordSerializer(ModelSerializer):
    email = EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']

class ChangePasswordSerializer(ModelSerializer):
    old_password = CharField(required=True, write_only=True)
    new_password = CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password']

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Old password is incorrect.")
        return value
    
    def update(self, instance, validated_data):
        new_password = validated_data['new_password']
        instance.set_password(new_password)
        instance.save()
        return instance