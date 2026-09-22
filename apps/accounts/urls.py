from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from apps.accounts.forms import QuietAuthenticationForm
from apps.accounts.views import delete_account, profile, signup

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=QuietAuthenticationForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", signup, name="signup"),
    path("profile/", profile, name="profile"),
    path("delete/", delete_account, name="delete_account"),
]
