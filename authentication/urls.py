from django.urls import path
from authentication.views import (RegisterView, LoginView, ForgotPasswordView, PasswordResetConfirmView,
                                  PasswordChangeView, LogoutAPIView, ProfileUpdateView)

urlpatterns = [
    path('v1/user/register',RegisterView.as_view(),name='register'),
    path('v1/user/login',LoginView.as_view(),name='login'),
    path('v1/user/forgot-password',ForgotPasswordView.as_view(),name='forgot-password'),
    path('v1/user/reset-password/',PasswordResetConfirmView.as_view(),name='reset-password'),
    path('v1/user/change-password/',PasswordChangeView.as_view(),name='change-password'),
    path('v1/user/logout',LogoutAPIView.as_view(),name='logout'),
    path('v1/user/profile',ProfileUpdateView.as_view(),name='update'),
]