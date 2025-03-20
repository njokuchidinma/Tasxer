from django.urls import path
from .views import RegisterView, LoginView, ForgotPasswordView, ChangePasswordView, TaskView, TaskDetailView




urlpatterns = [
    path('register/', RegisterView.as_view(), name='register-user'),
    path('login/', LoginView.as_view(), name='login-user'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('tasks/', TaskView.as_view(), name='tasks'),
    path('task-detail/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
]