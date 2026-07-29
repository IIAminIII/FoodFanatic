from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.SignupUserView.as_view(), name="register"),
    path("login/", views.LoginUserView.as_view(), name="login"),
    path("logout/", views.userlogout, name="logout"),
    path("verify/<str:token>/", views.verify, name="verify"),
    path("profile/", views.Profile, name="profile"),
    path("passwordchng/", views.passchnge, name="passchnge"),
    path("update_profile/", views.UpdateProfileView.as_view(), name="update"),
]
