from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from tasks.serializers import UserSerializer, TaskSerializer, ChangePasswordSerializer
from tasks.models import Task


class UserSerializerTest(TestCase):
    def test_create_user(self):
        data = {'username': 'testuser', 'password': 'testpass123', 'email': 'test@example.com'}
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')

    def test_invalid_email(self):
        data = {'username': 'testuser', 'password': 'testpass123', 'email': 'invalid-email'}
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

class TaskSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.task_data = {'user': self.user.id, 'title': 'Test Task', 'description': 'Test Description', 'completed': False}

    def test_create_task(self):
        serializer = TaskSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.title, 'Test Task')

class ChangePasswordSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='oldpass')
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.user

    def test_valid_password_change(self):
        data = {'old_password': 'oldpass', 'new_password': 'newpass123'}
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

    def test_invalid_old_password(self):
        data = {'old_password': 'oldpass', 'new_password': 'newpass123'}
        serializer = ChangePasswordSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)

    