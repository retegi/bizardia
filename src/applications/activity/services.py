import logging

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import override

logger = logging.getLogger(__name__)


def get_activity_registration_email_connection():
    return get_connection(
        timeout=getattr(settings, "ACTIVITY_REGISTRATION_EMAIL_TIMEOUT", 10),
    )


def send_activity_registration_email_message(message, registration, email_type):
    try:
        message.connection = get_activity_registration_email_connection()
        return message.send(fail_silently=False) > 0
    except Exception:
        logger.exception(
            "Activity registration %s email could not be sent.",
            email_type,
            extra={
                "registration_id": registration.pk,
                "activity_id": registration.activity_id,
                "activity_title": registration.activity.title,
                "user_id": registration.user_id,
            },
        )
        return False


def send_activity_registration_admin_email(registration):
    recipient = getattr(
        settings,
        "ACTIVITY_REGISTRATION_NOTIFICATION_EMAIL",
        "bizardia@gmail.com",
    )
    if not recipient:
        return False

    payment = registration.completed_payment
    if payment:
        payment_status = payment.get_status_display()
        paid_amount = f"{payment.amount} {payment.currency.upper()}"
    elif registration.activity.requires_payment:
        payment_status = "Ordainketa baieztapenaren zain"
        paid_amount = "-"
    else:
        payment_status = "Ez dagokio"
        paid_amount = "-"

    body = "\n".join([
        "Jarduera izen-emate berria jaso da.",
        "",
        f"Jarduera: {registration.activity.title}",
        f"Izena: {registration.name} {registration.surname}",
        f"Herria: {registration.locality or '-'}",
        f"Mendi federazioko kidea: {registration.get_federation_member_display()}",
        f"Izen-emate data: {timezone.localtime(registration.created_at).strftime('%Y-%m-%d %H:%M')}",
        f"Ordainketa egoera: {payment_status}",
        f"Ordaindutako zenbatekoa: {paid_amount}",
    ])

    message = EmailMessage(
        subject=f"Bizardia - {registration.activity.title} jarduerako izen-emate berria",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )

    return send_activity_registration_email_message(message, registration, "admin")


def send_activity_registration_confirmation_email(registration):
    if registration.confirmation_email_sent_at:
        return False

    send_activity_registration_admin_email(registration)

    user = registration.user
    recipient = getattr(user, "email", "") if user else ""
    if not recipient:
        return False

    context = {
        "registration": registration,
        "activity": registration.activity,
    }
    subject = f"Bizardia - {registration.activity.title} jarduerako izen-ematea"
    with override("eu"):
        text_body = render_to_string(
            "activity/email/registration_confirmation.txt",
            context,
        )
        html_body = render_to_string(
            "activity/email/registration_confirmation.html",
            context,
        )

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    message.attach_alternative(html_body, "text/html")

    if not send_activity_registration_email_message(message, registration, "confirmation"):
        return False

    registration.confirmation_email_sent_at = timezone.now()
    registration.save(update_fields=["confirmation_email_sent_at"])
    return True
