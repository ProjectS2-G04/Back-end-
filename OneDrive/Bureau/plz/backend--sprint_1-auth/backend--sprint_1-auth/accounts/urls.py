from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("send-reset-code/", SendResetCodeView.as_view(), name="send-reset-code"),
    path("verify-reset-code/", VerifyResetCodeView.as_view(), name="verify-reset-code"),
    path("password-reset/", ResetPasswordView.as_view(), name="password-reset"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDeleteView.as_view(), name="user-delete"),
    path('user_register/', user_register, name='user_register'),
]
