import logging
import uuid

from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView

from .forms import ChangeData, UserForm
from .models import AccountModel

logger = logging.getLogger(__name__)


def send_verification_email(request, user, token):
    verification_url = request.build_absolute_uri(
        reverse("verify", kwargs={"token": token})
    )
    message = render_to_string(
        "registercnfrm.html",
        {"user": user, "verification_url": verification_url},
    )
    email = EmailMultiAlternatives(
        "Confirm your FoodFanatic email",
        f"Confirm your email: {verification_url}",
        to=[user.email],
    )
    email.attach_alternative(message, "text/html")
    email.send()


class SignupUserView(CreateView):
    template_name = "register.html"
    form_class = UserForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        account, _ = AccountModel.objects.get_or_create(user=self.object)
        try:
            send_verification_email(
                self.request,
                self.object,
                account.email_token,
            )
        except Exception:
            logger.exception("Could not send verification email for user %s", self.object.pk)
            messages.warning(
                self.request,
                "Your account was created, but the verification email could not be sent. "
                "Please contact support.",
            )
        else:
            messages.success(
                self.request,
                "Please check your email to verify your account.",
            )
        return response


def verify(request, token):
    try:
        account = AccountModel.objects.get(email_token=token)
    except (AccountModel.DoesNotExist, ValueError):
        messages.error(request, "This verification link is invalid or has expired.")
        return redirect("login")

    account.is_activated = True
    account.email_token = None
    account.save(update_fields=("is_activated", "email_token"))
    messages.success(request, "Email verification was successful. You can now log in.")
    return redirect("login")


class LoginUserView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        account = AccountModel.objects.filter(user=user).first()
        if user.is_staff or (account and account.is_activated):
            messages.success(self.request, "Logged in successfully.")
            return super().form_valid(form)

        messages.error(self.request, "Please verify your email before logging in.")
        return redirect("login")

    def form_invalid(self, form):
        messages.error(self.request, "The username or password is incorrect.")
        return super().form_invalid(form)


@login_required(login_url="login")
@require_POST
def userlogout(request):
    logout(request)
    messages.warning(request, "Logged out successfully.")
    return redirect("home")


@login_required(login_url="login")
def Profile(request):
    return render(request, "profile.html")


@method_decorator(login_required(login_url="login"), name="dispatch")
class UpdateProfileView(UpdateView):
    form_class = ChangeData
    template_name = "chngedata.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        old_email = self.request.user.email
        response = super().form_valid(form)
        if old_email.lower() != self.object.email.lower():
            account, _ = AccountModel.objects.get_or_create(user=self.object)
            account.is_activated = False
            account.email_token = uuid.uuid4()
            account.save(update_fields=("is_activated", "email_token"))
            try:
                send_verification_email(
                    self.request,
                    self.object,
                    account.email_token,
                )
            except Exception:
                logger.exception(
                    "Could not send changed-email verification for user %s",
                    self.object.pk,
                )
                messages.warning(
                    self.request,
                    "Profile updated, but the verification email could not be sent.",
                )
            else:
                messages.info(
                    self.request,
                    "Profile updated. Verify your new email before your next login.",
                )
        else:
            messages.success(self.request, "Profile updated.")
        return response


@login_required(login_url="login")
def passchnge(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)
        messages.success(request, "Your password was changed.")
        return redirect("profile")
    return render(request, "chngepass.html", {"form": form})
