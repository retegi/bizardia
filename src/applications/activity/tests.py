from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .models import Activity, ActivityRegistration, ActivityRegistrationPayment, YesNo
from .services import send_activity_registration_confirmation_email
from .views import get_stripe_checkout_locale


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="Bizardia <no-reply@example.com>",
)
class ActivityRegistrationConfirmationEmailTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="registratzailea",
            email="registratzailea@example.com",
            password="secret",
        )
        self.activity = Activity.objects.create(
            title="Mendi irteera",
            slug="mendi-irteera",
            author="Bizardia",
            status=Activity.Status.PUBLISHED,
            requires_payment=False,
        )

    def registration_payload(self):
        return {
            "name": "Ane",
            "surname": "Etxeberria",
            "locality": "Azkoitia",
            "federation_member": YesNo.YES,
            "anonymous": YesNo.NO,
        }

    def test_free_registration_sends_admin_and_user_confirmation_emails(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("activity_app:activity_register", kwargs={"slug": self.activity.slug}),
            self.registration_payload(),
        )

        self.assertEqual(response.status_code, 302)
        registration = ActivityRegistration.objects.get()
        self.assertEqual(registration.user, self.user)
        self.assertIsNotNone(registration.confirmation_email_sent_at)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["bizardia@gmail.com"])
        self.assertEqual(mail.outbox[1].to, [self.user.email])
        self.assertIn("Jarduera: Mendi irteera", mail.outbox[1].body)
        self.assertIn("Izena: Ane Etxeberria", mail.outbox[1].body)
        self.assertIn("Herria: Azkoitia", mail.outbox[1].body)
        self.assertIn("Mendi federazioko kidea: Bai", mail.outbox[1].body)
        self.assertIn("Izen-emate data eta ordua:", mail.outbox[1].body)
        self.assertIn("Ordainketa egoera: ez dagokio", mail.outbox[1].body)

    def test_confirmation_email_is_not_duplicated_for_same_registration(self):
        registration = ActivityRegistration.objects.create(
            activity=self.activity,
            user=self.user,
            **self.registration_payload(),
        )

        self.assertTrue(send_activity_registration_confirmation_email(registration))
        self.assertFalse(send_activity_registration_confirmation_email(registration))

        self.assertEqual(len(mail.outbox), 2)

    def test_missing_user_email_does_not_break_flow_or_send_user_email(self):
        self.user.email = ""
        self.user.save(update_fields=["email"])
        registration = ActivityRegistration.objects.create(
            activity=self.activity,
            user=self.user,
            **self.registration_payload(),
        )

        self.assertFalse(send_activity_registration_confirmation_email(registration))

        registration.refresh_from_db()
        self.assertIsNotNone(registration.confirmation_email_sent_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["bizardia@gmail.com"])

    @patch("applications.activity.views.stripe.checkout.Session.retrieve")
    def test_paid_registration_sends_email_only_after_confirmed_payment(self, retrieve_mock):
        paid_activity = Activity.objects.create(
            title="Ikastaroa",
            slug="ikastaroa",
            author="Bizardia",
            status=Activity.Status.PUBLISHED,
            requires_payment=True,
            price=Decimal("12.50"),
            currency="eur",
        )
        payment = ActivityRegistrationPayment.objects.create(
            activity=paid_activity,
            user=self.user,
            registration_data=self.registration_payload(),
            amount=paid_activity.price,
            currency=paid_activity.currency,
            stripe_checkout_session_id="cs_test_confirmed",
        )
        retrieve_mock.return_value = Mock(payment_status="paid")
        self.client.force_login(self.user)

        self.assertEqual(ActivityRegistration.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.get(
            reverse(
                "activity_app:activity_checkout_success",
                kwargs={"slug": paid_activity.slug},
            ),
            {"session_id": payment.stripe_checkout_session_id},
        )

        self.assertEqual(response.status_code, 302)
        registration = ActivityRegistration.objects.get(activity=paid_activity)
        payment.refresh_from_db()
        self.assertEqual(payment.status, ActivityRegistrationPayment.Status.COMPLETED)
        self.assertEqual(payment.registration, registration)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["bizardia@gmail.com"])
        self.assertEqual(mail.outbox[1].to, [self.user.email])
        self.assertIn("Ordainketa egoera: ordainduta", mail.outbox[1].body)
        self.assertIn("Ordaindutako zenbatekoa: 12,50 EUR", mail.outbox[1].body)


@override_settings(STRIPE_SECRET_KEY="sk_test_fake")
class ActivityStripeCheckoutLocaleTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="ordaintzailea",
            email="ordaintzailea@example.com",
            password="secret",
        )
        self.activity = Activity.objects.create(
            title="Ordainpeko jarduera",
            slug="ordainpeko-jarduera",
            author="Bizardia",
            status=Activity.Status.PUBLISHED,
            requires_payment=True,
            price=Decimal("8.00"),
            currency="eur",
        )

    def registration_payload(self):
        return {
            "name": "Jon",
            "surname": "Agirre",
            "locality": "Azpeitia",
            "federation_member": YesNo.NO,
            "anonymous": YesNo.NO,
        }

    def test_stripe_checkout_locale_mapping(self):
        cases = (
            ("es", "es"),
            ("es-es", "es"),
            ("en", "en"),
            ("en-us", "en"),
            ("eu", "es"),
            ("fr", "es"),
        )

        for language, expected_locale in cases:
            with self.subTest(language=language), translation.override(language):
                self.assertEqual(get_stripe_checkout_locale(), expected_locale)

    @patch("applications.activity.views.stripe.checkout.Session.create")
    def test_activity_checkout_passes_resolved_locale_to_stripe(self, create_mock):
        create_mock.return_value = Mock(id="cs_test_locale", url="https://checkout.stripe.test")
        self.client.force_login(self.user)

        with translation.override("eu"):
            response = self.client.post(
                reverse("activity_app:activity_checkout", kwargs={"slug": self.activity.slug}),
                self.registration_payload(),
            )

        self.assertEqual(response.status_code, 302)
        create_mock.assert_called_once()
        self.assertEqual(create_mock.call_args.kwargs["locale"], "es")
