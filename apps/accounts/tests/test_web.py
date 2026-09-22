from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.countries.models import Country, CountryCurrency, Currency
from apps.travel.models import FavouritePair

User = get_user_model()
PASSWORD = "StrongPass-482!"


@override_settings(VITE_DEV_SERVER_ENABLED=True)
class AccountWebTests(TestCase):
    def test_signup_authenticates_and_redirects_to_saved_state(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "new-user",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )

        self.assertRedirects(response, reverse("saved_state"))
        self.assertTrue(User.objects.filter(username="new-user").exists())
        profile = self.client.get(reverse("profile"))
        self.assertEqual(profile.status_code, 200)

    def test_signup_preserves_safe_same_host_next(self):
        next_url = "/?load=1&source_currency=EUR&destination_currency=JPY"

        response = self.client.post(
            reverse("signup"),
            {
                "username": "returning",
                "password1": PASSWORD,
                "password2": PASSWORD,
                "next": next_url,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], next_url)

    def test_signup_rejects_external_next(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "safe-user",
                "password1": PASSWORD,
                "password2": PASSWORD,
                "next": "https://attacker.example/phish",
            },
        )

        self.assertRedirects(response, reverse("saved_state"))

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_logout_is_post_only(self):
        user = User.objects.create_user(username="member", password=PASSWORD)
        self.client.force_login(user)

        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 405)

    def test_account_deletion_requires_current_password(self):
        user = User.objects.create_user(username="member", password=PASSWORD)
        self.client.force_login(user)

        response = self.client.post(reverse("delete_account"), {"password": "wrong-password"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(pk=user.pk).exists())
        self.assertContains(response, "The password is incorrect.")

    def test_account_deletion_cascades_account_owned_favourites(self):
        user = User.objects.create_user(username="member", password=PASSWORD)
        eur = Currency.objects.create(code="EUR", name="Euro")
        jpy = Currency.objects.create(code="JPY", name="Japanese yen")
        fi = Country.objects.create(iso2="FI", iso3="FIN", name="Finland")
        jp = Country.objects.create(iso2="JP", iso3="JPN", name="Japan")
        CountryCurrency.objects.create(
            country=fi,
            currency=eur,
            is_primary=True,
            source="https://example.test/fi-eur",
        )
        CountryCurrency.objects.create(
            country=jp,
            currency=jpy,
            is_primary=True,
            source="https://example.test/jp-jpy",
        )
        FavouritePair.objects.create(
            user=user,
            source_currency=eur,
            destination_currency=jpy,
            source_country=fi,
            destination_country=jp,
        )
        self.client.force_login(user)

        response = self.client.post(reverse("delete_account"), {"password": PASSWORD})

        self.assertRedirects(response, reverse("converter"))
        self.assertFalse(User.objects.filter(pk=user.pk).exists())
        self.assertEqual(FavouritePair.objects.count(), 0)
        self.assertNotIn("_auth_user_id", self.client.session)
