from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase, override_settings
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
        self.assertIsNone(registration.confirmation_email_sent_at)
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
        response_messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertIn(
            "Ordainketa behar bezala egin da eta izen-ematea baieztatu da.",
            response_messages,
        )
        registration = ActivityRegistration.objects.get(activity=paid_activity)
        payment.refresh_from_db()
        self.assertEqual(payment.status, ActivityRegistrationPayment.Status.COMPLETED)
        self.assertEqual(payment.registration, registration)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["bizardia@gmail.com"])
        self.assertEqual(mail.outbox[1].to, [self.user.email])
        self.assertIn("Ordainketa egoera: online ordainduta", mail.outbox[1].body)
        self.assertIn("Ordaindutako zenbatekoa: 12,50 EUR", mail.outbox[1].body)

    @patch("applications.activity.views.stripe.checkout.Session.create")
    def test_paid_registration_can_be_confirmed_with_payment_on_event(self, create_mock):
        paid_activity = Activity.objects.create(
            title="Ikastaroa bertan",
            slug="ikastaroa-bertan",
            author="Bizardia",
            status=Activity.Status.PUBLISHED,
            requires_payment=True,
            price=Decimal("12.50"),
            currency="eur",
        )
        payload = self.registration_payload()
        payload["pay_on_event"] = "on"
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("activity_app:activity_checkout", kwargs={"slug": paid_activity.slug}),
            payload,
        )

        self.assertEqual(response.status_code, 302)
        create_mock.assert_not_called()
        registration = ActivityRegistration.objects.get(activity=paid_activity)
        payment = registration.payment
        self.assertEqual(payment.status, ActivityRegistrationPayment.Status.PENDING)
        self.assertEqual(payment.payment_method, ActivityRegistrationPayment.Method.ON_EVENT)
        self.assertEqual(payment.amount, Decimal("12.50"))
        self.assertIsNone(registration.completed_payment)
        self.assertEqual(registration.pending_on_event_payment, payment)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(
            "ordainketa ekitaldiaren egunerako zain geratu da",
            mail.outbox[1].body,
        )

    @patch("applications.activity.views.stripe.checkout.Session.retrieve")
    def test_paid_registration_success_message_is_not_duplicated_for_completed_payment(
        self,
        retrieve_mock,
    ):
        paid_activity = Activity.objects.create(
            title="Ikastaroa osatuta",
            slug="ikastaroa-osatuta",
            author="Bizardia",
            status=Activity.Status.PUBLISHED,
            requires_payment=True,
            price=Decimal("12.50"),
            currency="eur",
        )
        registration = ActivityRegistration.objects.create(
            activity=paid_activity,
            user=self.user,
            **self.registration_payload(),
        )
        payment = ActivityRegistrationPayment.objects.create(
            activity=paid_activity,
            user=self.user,
            registration=registration,
            registration_data=self.registration_payload(),
            amount=paid_activity.price,
            currency=paid_activity.currency,
            stripe_checkout_session_id="cs_test_completed",
            status=ActivityRegistrationPayment.Status.COMPLETED,
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "activity_app:activity_checkout_success",
                kwargs={"slug": paid_activity.slug},
            ),
            {"session_id": payment.stripe_checkout_session_id},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(retrieve_mock.called)
        response_messages = [str(message) for message in response.context["messages"]]
        self.assertIn(
            "Ordainketa behar bezala egin da eta izen-ematea baieztatu da.",
            response_messages,
        )

        second_response = self.client.get(
            reverse(
                "activity_app:activity_checkout_success",
                kwargs={"slug": paid_activity.slug},
            ),
            {"session_id": payment.stripe_checkout_session_id},
            follow=True,
        )

        self.assertEqual(second_response.status_code, 200)
        second_response_messages = [
            str(message) for message in second_response.context["messages"]
        ]
        self.assertNotIn(
            "Ordainketa behar bezala egin da eta izen-ematea baieztatu da.",
            second_response_messages,
        )

    @patch(
        "applications.activity.services.EmailMultiAlternatives.send",
        side_effect=TimeoutError("SMTP timeout"),
    )
    @patch("applications.activity.views.stripe.checkout.Session.retrieve")
    def test_paid_registration_success_survives_confirmation_email_timeout(
        self,
        retrieve_mock,
        send_mock,
    ):
        paid_activity = Activity.objects.create(
            title="Ikastaroa timeout",
            slug="ikastaroa-timeout",
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
            stripe_checkout_session_id="cs_test_timeout",
        )
        retrieve_mock.return_value = Mock(payment_status="paid")
        self.client.force_login(self.user)

        with self.assertLogs("applications.activity.services", level="ERROR") as logs:
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
        self.assertIsNone(registration.confirmation_email_sent_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["bizardia@gmail.com"])
        self.assertTrue(send_mock.called)
        self.assertIn(
            "Activity registration confirmation email could not be sent.",
            "\n".join(logs.output),
        )

    def test_registration_list_shows_payment_on_event_and_excludes_it_from_collected_total(self):
        paid_activity = Activity.objects.create(
            title="Ikastaroa zerrenda",
            slug="ikastaroa-zerrenda",
            author="Bizardia",
            status=Activity.Status.PUBLISHED,
            requires_payment=True,
            price=Decimal("12.50"),
            currency="eur",
        )
        paid_registration = ActivityRegistration.objects.create(
            activity=paid_activity,
            user=self.user,
            **self.registration_payload(),
        )
        ActivityRegistrationPayment.objects.create(
            activity=paid_activity,
            user=self.user,
            registration=paid_registration,
            registration_data=self.registration_payload(),
            amount=Decimal("12.50"),
            currency="eur",
            status=ActivityRegistrationPayment.Status.COMPLETED,
            payment_method=ActivityRegistrationPayment.Method.STRIPE,
        )
        pending_payload = self.registration_payload()
        pending_payload["name"] = "Mikel"
        pending_registration = ActivityRegistration.objects.create(
            activity=paid_activity,
            user=self.user,
            **pending_payload,
        )
        ActivityRegistrationPayment.objects.create(
            activity=paid_activity,
            user=self.user,
            registration=pending_registration,
            registration_data=pending_payload,
            amount=Decimal("12.50"),
            currency="eur",
            status=ActivityRegistrationPayment.Status.PENDING,
            payment_method=ActivityRegistrationPayment.Method.ON_EVENT,
        )
        organizer_group = Group.objects.create(name="ekintza-antolatzaileak")
        self.user.groups.add(organizer_group)
        self.client.force_login(self.user)

        with translation.override("en"):
            response = self.client.get(
                reverse("activity_registration_list"),
                {"activity": paid_activity.pk},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_collected"], Decimal("12.50"))
        content = response.content.decode()
        self.assertIn("Online ordainduta", content)
        self.assertIn("Ekitaldiaren egunean ordaintzeko zain", content)
        self.assertIn("12,50 EUR", content)


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
        payment = ActivityRegistrationPayment.objects.get(activity=self.activity)
        self.assertEqual(payment.payment_method, ActivityRegistrationPayment.Method.STRIPE)
        self.assertEqual(payment.status, ActivityRegistrationPayment.Status.PENDING)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="Bizardia <no-reply@example.com>",
    STRIPE_WEBHOOK_SECRET="whsec_test",
)
class ActivityStripeWebhookTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="webhook-user",
            email="webhook@example.com",
            password="secret",
        )
        self.activity = Activity.objects.create(
            title="Webhook jarduera",
            slug="webhook-jarduera",
            author="Bizardia",
            status=Activity.Status.PUBLISHED,
            requires_payment=True,
            price=Decimal("15.00"),
            currency="eur",
        )

    def registration_payload(self):
        return {
            "name": "Maite",
            "surname": "Aranburu",
            "locality": "Zumaia",
            "federation_member": YesNo.YES,
            "anonymous": YesNo.NO,
        }

    def create_payment(self, session_id="cs_test_webhook"):
        return ActivityRegistrationPayment.objects.create(
            activity=self.activity,
            user=self.user,
            registration_data=self.registration_payload(),
            amount=self.activity.price,
            currency=self.activity.currency,
            stripe_checkout_session_id=session_id,
        )

    def stripe_event(self, session_id="cs_test_webhook", payment_status="paid"):
        return {
            "id": "evt_test",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": session_id,
                    "payment_status": payment_status,
                },
            },
        }

    def post_webhook(self):
        return self.client.post(
            reverse("stripe_webhook"),
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test-signature",
        )

    def test_stripe_webhook_rejects_invalid_signature(self):
        self.create_payment()

        response = self.post_webhook()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(ActivityRegistration.objects.count(), 0)

    @patch("applications.activity.views.stripe.Webhook.construct_event")
    def test_stripe_webhook_confirms_payment_and_creates_registration(self, construct_event_mock):
        payment = self.create_payment()
        construct_event_mock.return_value = self.stripe_event(payment.stripe_checkout_session_id)

        response = self.post_webhook()

        self.assertEqual(response.status_code, 200)
        registration = ActivityRegistration.objects.get()
        payment.refresh_from_db()
        self.assertEqual(payment.status, ActivityRegistrationPayment.Status.COMPLETED)
        self.assertEqual(payment.registration, registration)
        self.assertEqual(registration.user, self.user)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["bizardia@gmail.com"])
        self.assertEqual(mail.outbox[1].to, [self.user.email])

    @patch("applications.activity.views.stripe.Webhook.construct_event")
    def test_stripe_webhook_is_idempotent(self, construct_event_mock):
        payment = self.create_payment()
        construct_event_mock.return_value = self.stripe_event(payment.stripe_checkout_session_id)

        first_response = self.post_webhook()
        second_response = self.post_webhook()

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, ActivityRegistrationPayment.Status.COMPLETED)
        self.assertEqual(ActivityRegistration.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)

    @patch(
        "applications.activity.services.EmailMultiAlternatives.send",
        side_effect=TimeoutError("SMTP timeout"),
    )
    @patch("applications.activity.views.stripe.Webhook.construct_event")
    def test_stripe_webhook_survives_confirmation_email_failure(
        self,
        construct_event_mock,
        send_mock,
    ):
        payment = self.create_payment()
        construct_event_mock.return_value = self.stripe_event(payment.stripe_checkout_session_id)

        with self.assertLogs("applications.activity.services", level="ERROR") as logs:
            response = self.post_webhook()

        self.assertEqual(response.status_code, 200)
        registration = ActivityRegistration.objects.get()
        payment.refresh_from_db()
        self.assertEqual(payment.status, ActivityRegistrationPayment.Status.COMPLETED)
        self.assertEqual(payment.registration, registration)
        self.assertIsNone(registration.confirmation_email_sent_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["bizardia@gmail.com"])
        self.assertTrue(send_mock.called)
        self.assertIn(
            "Activity registration confirmation email could not be sent.",
            "\n".join(logs.output),
        )


class BizardiaNavigationMenuTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def render_base_for_user(self, user):
        request = self.factory.get("/")
        request.user = user
        return render_to_string("base.html", request=request)

    def test_admin_link_is_only_visible_for_staff_users(self):
        normal_user = get_user_model().objects.create_user(
            username="normal",
            email="normal@example.com",
            password="secret",
        )
        staff_user = get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="secret",
            is_staff=True,
        )

        normal_html = self.render_base_for_user(normal_user)
        staff_html = self.render_base_for_user(staff_user)

        self.assertNotIn('href="/admin/"', normal_html)
        self.assertIn('href="/admin/"', staff_html)
        self.assertIn('target="_blank"', staff_html)
        self.assertIn('rel="noopener noreferrer"', staff_html)

    def test_registration_list_link_uses_activity_registration_permissions(self):
        normal_user = get_user_model().objects.create_user(
            username="normal-zerrenda",
            email="normal-zerrenda@example.com",
            password="secret",
        )
        organizer_user = get_user_model().objects.create_user(
            username="organizer",
            email="organizer@example.com",
            password="secret",
        )
        organizer_group = Group.objects.create(name="ekintza-antolatzaileak")
        organizer_user.groups.add(organizer_group)

        normal_html = self.render_base_for_user(normal_user)
        organizer_html = self.render_base_for_user(organizer_user)

        self.assertNotIn('href="/zerrenda/"', normal_html)
        self.assertIn('href="/zerrenda/"', organizer_html)
        self.assertIn('target="_blank"', organizer_html)
        self.assertIn('rel="noopener noreferrer"', organizer_html)
