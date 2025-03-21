from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from tasks.models import Task


class TaskViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(user=self.user, title='Test Task', description='Test Description')

    def test_get_task(self):
        url = reverse('tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_task(self):
        url = reverse('tasks')
        data = {'title': 'New Task', 'description': 'New Description', "completed": "False", 'user': self.user.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_update_task(self):
        url = reverse('task-detail', args=[self.task.id])
        data = {'title': 'Updated Task'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')

    def test_delete_task(self):
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Task.objects.count(), 0)


class AuthViewTest(APITestCase):
    def test_register_user(self):
        url = reverse('register-user')
        data = {'username': 'newuser', 'password': 'newpass123', 'email': 'newuser@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_login_user(self):
        User.objects.create_user(username='testuser', password='testpass123')
        url = reverse('login-user')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)