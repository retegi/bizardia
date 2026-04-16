from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, TemplateView
from django.urls import reverse
from urllib.parse import urlencode
from .models import Activity, ActivityRegistration, ActivityRegistrationPayment
from .forms import ActivityForm
from .services import send_activity_registration_confirmation_email
from django.contrib.auth.decorators import login_required
from .forms import ActivityRegistrationForm
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

ACTIVITY_REGISTRATION_LIST_GROUPS = (
    "ekintza-antolatzaileak",
    "zuzendaritza-batzordea",
)


def activity_list(request):
    activity = Activity.objects.filter(status=Activity.Status.PUBLISHED).order_by('-published_at')
    return render(request, 'activity/activity_list.html', {'activity': activity})


def activity_detail(request, slug):
    activity = get_object_or_404(Activity, slug=slug, status=Activity.Status.PUBLISHED)
    return render(request, 'activity/activity_detail.html', {'activity': activity})

def is_organizer(user):
    return user.is_authenticated and user.groups.filter(name="ekintza-antolatzaileak").exists()

def can_create_activity(user):
    if not user.is_authenticated:
        return False
    return (
        user.groups.filter(name="ekintza-antolatzaileak").exists()
        or user.groups.filter(name="zuzendaritza-batzordea").exists()
        or user.has_perm("activity.add_activity")
    )


def can_view_activity_registration_list(user):
    return (
        user.is_authenticated
        and user.groups.filter(name__in=ACTIVITY_REGISTRATION_LIST_GROUPS).exists()
    )


class ActivityRegistrationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = ActivityRegistration
    template_name = "activity/activity_registration_list.html"
    context_object_name = "registrations"
    raise_exception = True

    def test_func(self):
        return can_view_activity_registration_list(self.request.user)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        raise PermissionDenied

    def get_selected_activity(self):
        activity_id = self.request.GET.get("activity")
        if not activity_id:
            return None

        return Activity.objects.filter(pk=activity_id).first()

    def get_queryset(self):
        self.selected_activity = self.get_selected_activity()
        if not self.selected_activity:
            return ActivityRegistration.objects.none()

        return (
            ActivityRegistration.objects
            .filter(activity=self.selected_activity)
            .select_related("activity", "payment")
            .order_by("surname", "name", "id")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_activity = getattr(self, "selected_activity", None)

        context["activities"] = Activity.objects.all().order_by("-activity_date_time", "-created_at")
        context["selected_activity"] = selected_activity
        context["selected_activity_id"] = str(selected_activity.pk) if selected_activity else ""
        context["total_registrations"] = context["object_list"].count() if selected_activity else 0
        context["total_collected"] = 0
        context["total_collected_currency"] = "€"

        if selected_activity:
            context["total_collected_currency"] = (
                "€" if selected_activity.currency.lower() == "eur" else selected_activity.currency.upper()
            )

            if selected_activity.requires_payment:
                context["total_collected"] = (
                    ActivityRegistrationPayment.objects
                    .filter(
                        activity=selected_activity,
                        registration__isnull=False,
                        status=ActivityRegistrationPayment.Status.COMPLETED,
                    )
                    .aggregate(total=Sum("amount"))["total"]
                    or 0
                )

        return context


@login_required
@user_passes_test(can_create_activity)
def activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user

            # Si es junta y tiene permiso de publicar, puede dejarlo ya publicado (opcional)
            if request.user.has_perm("activity.can_publish_activity"):
                obj.status = Activity.Status.PUBLISHED
                obj.published_at = timezone.now()
                obj.published_by = request.user
            else:
                obj.status = Activity.Status.PENDING  # va a validación

            obj.save()
            return redirect('activity_app:activity_list')
    else:
        form = ActivityForm()
    return render(request, 'activity/activity_form.html', {'form': form})

def activity_register(request, slug):
    activity = get_object_or_404(Activity, slug=slug, status=Activity.Status.PUBLISHED)
    login_url = f"{reverse('account_login')}?{urlencode({'next': request.get_full_path()})}"

    if not request.user.is_authenticated:
        return render(request, 'activity/activity_register.html', {
            'activity': activity,
            'form': ActivityRegistrationForm(),
            'require_login_modal': True,
            'login_url': login_url,
        })

    if request.method == 'POST':
        form = ActivityRegistrationForm(request.POST)
        if form.is_valid():
            if activity.requires_payment:
                form.add_error(None, _("Paid activities must be confirmed through Stripe Checkout."))
                return render(request, 'activity/activity_register.html', {
                    'activity': activity,
                    'form': form,
                    'require_login_modal': False,
                    'login_url': login_url,
                })

            registration = form.save(commit=False)
            registration.activity = activity

            # Usuario logeado (opcional)
            if request.user.is_authenticated:
                registration.user = request.user

            registration.save()
            send_activity_registration_confirmation_email(registration)
            return redirect('activity_app:activity_detail', slug=slug)
    else:
        form = ActivityRegistrationForm()

    return render(request, 'activity/activity_register.html', {
        'activity': activity,
        'form': form,
        'require_login_modal': False,
        'login_url': login_url,
    })


@login_required
@require_POST
def activity_checkout(request, slug):
    activity = get_object_or_404(Activity, slug=slug, status=Activity.Status.PUBLISHED)

    if not activity.requires_payment:
        return activity_register(request, slug)

    form = ActivityRegistrationForm(request.POST)
    if not form.is_valid():
        return render(request, 'activity/activity_register.html', {
            'activity': activity,
            'form': form,
            'require_login_modal': False,
            'login_url': f"{reverse('account_login')}?{urlencode({'next': request.get_full_path()})}",
        })

    if not settings.STRIPE_SECRET_KEY:
        form.add_error(None, _("Stripe is not configured."))
        return render(request, 'activity/activity_register.html', {
            'activity': activity,
            'form': form,
            'require_login_modal': False,
            'login_url': f"{reverse('account_login')}?{urlencode({'next': request.get_full_path()})}",
        })

    if not activity.price or activity.price <= Decimal("0"):
        form.add_error(None, _("This activity requires payment, but it has no valid price."))
        return render(request, 'activity/activity_register.html', {
            'activity': activity,
            'form': form,
            'require_login_modal': False,
            'login_url': f"{reverse('account_login')}?{urlencode({'next': request.get_full_path()})}",
        })

    payment = ActivityRegistrationPayment.objects.create(
        activity=activity,
        user=request.user,
        registration_data=form.cleaned_data,
        amount=activity.price,
        currency=activity.currency.lower(),
    )

    stripe.api_key = settings.STRIPE_SECRET_KEY
    success_url = request.build_absolute_uri(
        reverse('activity_app:activity_checkout_success', kwargs={'slug': activity.slug})
    )
    cancel_url = request.build_absolute_uri(
        reverse('activity_app:activity_checkout_cancel', kwargs={'slug': activity.slug})
    )

    try:
        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": activity.currency.lower(),
                    "unit_amount": int(activity.price * Decimal("100")),
                    "product_data": {
                        "name": activity.title,
                    },
                },
                "quantity": 1,
            }],
            client_reference_id=str(payment.id),
            metadata={
                "activity_id": str(activity.id),
                "payment_id": str(payment.id),
                "user_id": str(request.user.id),
            },
            success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{cancel_url}?session_id={{CHECKOUT_SESSION_ID}}",
        )
    except stripe.StripeError:
        form.add_error(None, _("Stripe Checkout could not be started. Please try again."))
        return render(request, 'activity/activity_register.html', {
            'activity': activity,
            'form': form,
            'require_login_modal': False,
            'login_url': f"{reverse('account_login')}?{urlencode({'next': request.get_full_path()})}",
        })

    payment.stripe_checkout_session_id = checkout_session.id
    payment.save(update_fields=["stripe_checkout_session_id", "updated_at"])

    return redirect(checkout_session.url)


@login_required
def activity_checkout_success(request, slug):
    activity = get_object_or_404(Activity, slug=slug, status=Activity.Status.PUBLISHED)
    session_id = request.GET.get("session_id")

    if not session_id:
        messages.error(request, _("Stripe session is missing."))
        return redirect('activity_app:activity_register', slug=activity.slug)

    payment = get_object_or_404(
        ActivityRegistrationPayment,
        activity=activity,
        user=request.user,
        stripe_checkout_session_id=session_id,
    )

    if payment.status == ActivityRegistrationPayment.Status.COMPLETED and payment.registration_id:
        return redirect('activity_app:activity_detail', slug=activity.slug)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError:
        messages.error(request, _("Stripe payment could not be verified. Please try again."))
        return redirect('activity_app:activity_register', slug=activity.slug)

    if checkout_session.payment_status != "paid":
        messages.error(request, _("Payment has not been completed."))
        return redirect('activity_app:activity_register', slug=activity.slug)

    with transaction.atomic():
        payment = ActivityRegistrationPayment.objects.select_for_update().get(pk=payment.pk)
        if payment.status != ActivityRegistrationPayment.Status.COMPLETED:
            registration = ActivityRegistration.objects.create(
                activity=activity,
                user=request.user,
                **payment.registration_data,
            )
            payment.registration = registration
            payment.status = ActivityRegistrationPayment.Status.COMPLETED
            payment.save(update_fields=["registration", "status", "updated_at"])
            send_activity_registration_confirmation_email(registration)

    messages.success(request, _("Payment completed and registration confirmed."))
    return redirect('activity_app:activity_detail', slug=activity.slug)


@login_required
def activity_checkout_cancel(request, slug):
    activity = get_object_or_404(Activity, slug=slug, status=Activity.Status.PUBLISHED)
    session_id = request.GET.get("session_id")

    if session_id:
        ActivityRegistrationPayment.objects.filter(
            activity=activity,
            user=request.user,
            stripe_checkout_session_id=session_id,
            status=ActivityRegistrationPayment.Status.PENDING,
        ).update(status=ActivityRegistrationPayment.Status.CANCELED)

    messages.info(request, _("Payment canceled. Registration has not been created."))
    return redirect('activity_app:activity_register', slug=activity.slug)



def activity_registered_list(request, slug):
    activity = get_object_or_404(Activity, slug=slug, status=Activity.Status.PUBLISHED)

    registrations = ActivityRegistration.objects.filter(
        activity=activity,
        anonymous=False
    ).order_by('created_at')

    return render(
        request,
        'activity/activity_registered_list.html',
        {
            'activity': activity,
            'registrations': registrations
        }
    )
