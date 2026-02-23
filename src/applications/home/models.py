# blog/models.py
from django.db import models

class HomeContent(models.Model):

    # =========================
    # Visibility Control
    # =========================
    show_welcome_section = models.BooleanField(default=True)
    show_director_section = models.BooleanField(default=True)
    show_membership_section = models.BooleanField(default=True)
    show_membership_button = models.BooleanField(default=True)

    # =========================
    # Bienvenida / Presentación
    # =========================
    director_name = models.CharField(
        max_length=100,
        blank=True
    )

    director_position = models.CharField(
        max_length=100,
        blank=True
    )

    director_welcome_text = models.TextField(
        blank=True
    )

    director_image = models.ImageField(
        upload_to="home/",
        blank=True,
        null=True
    )

    # =========================
    # Contact Information
    # =========================
    phone = models.CharField(
        max_length=30,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    address = models.CharField(
        max_length=255,
        blank=True
    )

    # =========================
    # Association Information
    # =========================
    association_name = models.CharField(
        max_length=100,
        blank=True
    )

    slogan = models.CharField(
        max_length=100,
        blank=True
    )

    foundation_year = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    number_of_members = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    activities_per_year = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    # =========================
    # Membership Section
    # =========================
    membership_button_text = models.CharField(
        max_length=100,
        blank=True
    )

    membership_info_text = models.TextField(
        blank=True
    )

    membership_button_url = models.CharField(
        max_length=200,
        blank=True
    )

    # =========================
    # Social Media
    # =========================
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)  # X

    # =========================
    # Control
    # =========================
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contenido de la Home"
        verbose_name_plural = "Contenido de la Home"

    def __str__(self):
        return self.association_name or "Contenido principal de la Home"
