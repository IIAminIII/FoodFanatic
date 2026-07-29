from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import UserForm
from .models import AccountModel


class AccountSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "customer",
            email="customer@example.com",
            password="test-password",
        )
        self.account = AccountModel.objects.create(
            user=self.user,
            is_activated=True,
        )
        self.other_user = User.objects.create_user(
            "other",
            email="other@example.com",
            password="test-password",
        )

    def test_registration_email_is_unique_case_insensitively(self):
        form = UserForm(
            data={
                "username": "new-user",
                "first_name": "New",
                "last_name": "User",
                "email": "CUSTOMER@example.com",
                "password1": "a-complex-test-password-123",
                "password2": "a-complex-test-password-123",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_profile_update_always_targets_logged_in_user(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("update"),
            {
                "username": "customer-updated",
                "first_name": "Updated",
                "last_name": "Customer",
                "email": "customer@example.com",
            },
        )

        self.assertRedirects(response, reverse("profile"))
        self.user.refresh_from_db()
        self.other_user.refresh_from_db()
        self.assertEqual(self.user.username, "customer-updated")
        self.assertEqual(self.other_user.username, "other")

    def test_logout_requires_post(self):
        self.client.force_login(self.user)

        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unverified_user_cannot_log_in(self):
        self.account.is_activated = False
        self.account.save(update_fields=("is_activated",))

        response = self.client.post(
            reverse("login"),
            {"username": "customer", "password": "test-password"},
        )

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_verification_token_is_one_time_use(self):
        self.account.is_activated = False
        self.account.save(update_fields=("is_activated",))
        token = self.account.email_token

        response = self.client.get(reverse("verify", args=(token,)))

        self.assertRedirects(response, reverse("login"))
        self.account.refresh_from_db()
        self.assertTrue(self.account.is_activated)
        self.assertIsNone(self.account.email_token)
