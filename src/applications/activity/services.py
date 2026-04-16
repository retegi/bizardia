import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import override

logger = logging.getLogger(__name__)


def send_activity_registration_confirmation_email(registration):
    if registration.confirmation_email_sent_at:
        return False

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

    try:
        message.send(fail_silently=False)
    except Exception:
        logger.exception("Activity registration confirmation email could not be sent.")
        return False

    registration.confirmation_email_sent_at = timezone.now()
    registration.save(update_fields=["confirmation_email_sent_at"])
    return True
