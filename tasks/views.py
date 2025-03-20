from .models import Task
from .serializers import TaskSerializer, UserSerializer, User, ForgotPasswordSerializer, ChangePasswordSerializer
from .tasks import send_task_notification
from .utils import generate_random_password
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken




class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """ New User Registration """
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                "data": "User created successfully",
                "id": str(user.id),
                "refresh": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "data": "User Registration Failed",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        serializer = UserSerializer(request.data)
        if user:
            #Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ForgotPasswordView(APIView):
    queryset = User.objects.all()
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        users = User.objects.filter(email=email)

        if users.exists():
            user = users.first()
            new_password = generate_random_password()
            try:
                send_mail(
                    'Password Reset for iSans Original',
                    f'Dear {user.first_name},\n\n'  # Personalizing with first name
                    'We have received a request to reset your password for iSans Original.\n\n'
                    f'Your new password is: {new_password}\n\n'
                    'Please use this password to log in to your account. We recommend that you change your password to something more secure as soon as possible.\n\n'
                    'If you have any questions or concerns, please contact us at support@isansoriginal.com.\n\n'
                    'Best regards,\n'
                    'The iSans Original Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )
                user.set_password(new_password)
                user.save()
                return Response({"message": "New password has been sent to your mailbox"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": "Failed to send email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"error": "Email not found"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user 
            serializer.update(user, serializer.validated_data)
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cache_key = f'task_list_user_{request.user.id}'
        cached_tasks = cache.get(cache_key)
        if not cached_tasks:
            tasks = Task.objects.filter(user=request.user)
            serializer = TaskSerializer(tasks, many=True)
            cache.set(cache_key, serializer.data, timeout=60)
            return Response(serializer.data)
        return Response(cached_tasks)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            send_task_notification.delay(serializer.data['title'])
            cache.delete(f'task_list_user_{request.user.id}')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Task.objects.get(pk=pk, user=self.request.user)
        except Task.DoesNotExist:
            return None

    def get(self, request, pk):
        task = self.get_object(pk)
        if task:
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        """
        Update a specific project detail
        """
        task = self.get_object(pk)
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete(f'task_list_user_{request.user.id}')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Delete specific task
        """
        task = self.get_object(pk)
        if not task:
            return Response({'error': 'Task is not found'}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        cache.delete(f'task_list_user_{request.user.id}')
        return Response({'Task has been successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
            