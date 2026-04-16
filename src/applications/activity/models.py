from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField



class YesNo(models.TextChoices):
    YES = "yes", _("Bai")
    NO = "no", _("Ez")


class Activity(models.Model):
    title = models.CharField(_("Izenburua"), max_length=200)
    slug = models.SlugField(_("URL testua (tartetik ez utzi)"), unique=True, blank=True)
    content = HTMLField(_("Informazio osoa xehetasun guztiekin"), blank=True, null=True)
    short = models.TextField(_("Informazio laburra"), blank=True, null=True)

    class Audience(models.TextChoices):
        ANYONE = "Edozein pertsonak", _("Edozein pertsonak")
        MEMBERS = "Bazkideek", _("Bazkideak")
        CHILDREN = "Haurrak", _("Haurrak")
        ADULTS = "Helduak", _("Helduak")
        FAMILIES = "Familiak", _("Familiak")
        MEMBERS_CHILDREN = "Bazkideak eta haurrak", _("Bazkideak eta haurrak")

    audience = models.CharField(
        _("Nork hartu dezake parte?"),
        max_length=30,
        choices=Audience.choices,
        default=Audience.ANYONE
    )

    audience_note = models.CharField(
        _("Ohar gehigarria"),
        max_length=160,
        blank=True,
        null=True,
        help_text=_("Ej: “Haurrak heldu batekin lagundua”, “12 urtetik aurrera”…")
    )

    cover_image = models.ImageField(
        upload_to='activity/',
        blank=True,
        null=True,
        verbose_name=_("Irudi nagusia")
    )

    # Recomendación: relacionarlo con User para permisos por autor
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
        verbose_name=_("Sortzailea")
    )

    # Si quieres mantener el nombre visible del organizador:
    author = models.CharField(_("Antolatzailea"), max_length=100)

    outstanding = models.BooleanField(_("Nabarmendua"), default=False)

    price = models.DecimalField(
        _("Prezioa"),
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )
    currency = models.CharField(
        _("Moneta"),
        max_length=3,
        default="eur",
        help_text=_("Stripe-rako ISO moneta-kodea. Adibidez: eur")
    )
    requires_payment = models.BooleanField(_("Ordainketa behar du"), default=False)

    activity_date_time = models.DateTimeField(_("Data eta ordua"), null=True, blank=True)

    show_registration_button = models.BooleanField(_("Izena emateko botoia agertzea"), default=True)
    show_price = models.BooleanField(_("Prezioa agertzea"), default=True)

    # ✅ Flujo editorial
    class Status(models.TextChoices):
        DRAFT = "draft", _("Zirriborroa")
        PENDING = "pending", _("Balidazio zain")
        PUBLISHED = "published", _("Argitaratua")
        ARCHIVED = "archived", _("Artxibatua")

    status = models.CharField(
        _("Egoera"),
        max_length=12,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True
    )

    # ✅ Metadatos
    created_at = models.DateTimeField(_("Sortze-data"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Eguneratua"), auto_now=True)

    # ✅ Publicación real (solo cuando se publica)
    published_at = models.DateTimeField(_("Argitaratze-data"), null=True, blank=True)
    published_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_activities",
        verbose_name=_("Nork argitaratu du")
    )

    class Meta:
        verbose_name = _("Jarduera")
        verbose_name_plural = _("Jarduerak")
        ordering = ["-published_at", "-created_at"]
        permissions = [
            ("can_publish_activity", "Can publish activities"),
            ("can_review_activity", "Can review/validate activities"),
        ]

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    def submit_for_review(self):
        """El organizador marca la actividad como 'pendiente'."""
        if self.status == self.Status.DRAFT:
            self.status = self.Status.PENDING

    def publish(self, user=None):
        """Publicación final: solo debería llamarse si el usuario tiene permiso."""
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        if user:
            self.published_by = user


class ActivityImage(models.Model):

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="activity/gallery/"
    )

    title = models.CharField(
        max_length=200,
        blank=True
    )

    order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.activity.title} - Image {self.id}"

    def save(self, *args, **kwargs):

        if self.image and not self.pk:
            img = Image.open(self.image)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            if img.width > 1200:
                ratio = 1200 / float(img.width)
                new_height = int(float(img.height) * ratio)
                img = img.resize((1200, new_height), Image.LANCZOS)

            output = BytesIO()
            img.save(output, format="JPEG", quality=75, optimize=True)

            self.image = ContentFile(output.getvalue(), name=self.image.name)

        super().save(*args, **kwargs)



class ActivityQuestionAnswer(models.Model):

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="questions_answers",
        verbose_name=_("Jarduera")
    )

    question = models.TextField(
        _("Galdera"),
        blank=False,
    )

    answer = models.TextField(
        _("Erantzuna"),
        blank=False,
    )

    order = models.PositiveIntegerField(
        _("Ordena"),
        default=0,
    )

    class Meta:
        verbose_name = _("Jardueraren galdera/erantzuna")
        verbose_name_plural = _("Jardueraren galderak eta erantzunak")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.activity.title} - {self.question[:50]}"


class ActivityRegistration(models.Model):

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name=_("Jarduera")
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Erabiltzailea")
    )

    name = models.CharField(_("Izena"), max_length=100)
    surname = models.CharField(_("Abizena"), max_length=100)
    locality = models.CharField(_("Herria"), max_length=100, blank=True)

    federation_member = models.CharField(
        _("Mendi federazioko kidea"),
        max_length=3,
        choices=YesNo.choices,
        blank=False,
    )

    anonymous = models.CharField(
        _("Erregistro anonimoa"),
        max_length=3,
        choices=YesNo.choices,
        default=YesNo.NO,
        blank=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    confirmation_email_sent_at = models.DateTimeField(
        _("Baieztapen emaila bidalita"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Jardueraren izen-ematea")
        verbose_name_plural = _("Jardueretako izen-emateak")

    def __str__(self):
        return f"{self.activity.title} - {self.name}"

    @property
    def has_completed_payment(self):
        try:
            return self.payment.status == ActivityRegistrationPayment.Status.COMPLETED
        except ActivityRegistrationPayment.DoesNotExist:
            return False

    @property
    def completed_payment(self):
        try:
            payment = self.payment
        except ActivityRegistrationPayment.DoesNotExist:
            return None

        if payment.status == ActivityRegistrationPayment.Status.COMPLETED:
            return payment
        return None

    @property
    def pending_on_event_payment(self):
        try:
            payment = self.payment
        except ActivityRegistrationPayment.DoesNotExist:
            return None

        is_pending_on_event = (
            payment.payment_method == ActivityRegistrationPayment.Method.ON_EVENT
            and payment.status == ActivityRegistrationPayment.Status.PENDING
        )
        if is_pending_on_event:
            return payment
        return None


class ActivityRegistrationPayment(models.Model):
    class Method(models.TextChoices):
        STRIPE = "stripe", _("Stripe")
        ON_EVENT = "on_event", _("Ekitaldiaren egunean")

    class Status(models.TextChoices):
        PENDING = "pending", _("Ordainketa zain")
        COMPLETED = "completed", _("Ordainduta")
        CANCELED = "canceled", _("Bertan behera")

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="registration_payments",
        verbose_name=_("Jarduera")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Erabiltzailea")
    )
    registration = models.OneToOneField(
        ActivityRegistration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment",
        verbose_name=_("Izen-ematea")
    )
    stripe_checkout_session_id = models.CharField(
        _("Stripe Checkout Session ID"),
        max_length=255,
        unique=True,
        blank=True,
        null=True
    )
    status = models.CharField(
        _("Egoera"),
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    payment_method = models.CharField(
        _("Ordainketa modua"),
        max_length=12,
        choices=Method.choices,
        default=Method.STRIPE,
    )
    registration_data = models.JSONField(_("Izen-emate datuak"))
    amount = models.DecimalField(_("Zenbatekoa"), max_digits=6, decimal_places=2)
    currency = models.CharField(_("Moneta"), max_length=3, default="eur")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Jarduera izen-ematearen ordainketa")
        verbose_name_plural = _("Jarduera izen-emateen ordainketak")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.activity.title} - {self.amount} {self.currency}"
