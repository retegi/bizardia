import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from PIL import Image, ImageOps
from tinymce.models import HTMLField


class Gallery(models.Model):
    title = models.CharField(_("Izenburua"), max_length=200)

    date = models.DateTimeField(_("Data"), null=True, blank=True)

    content = HTMLField(_("Edukia"), blank=True, null=True)

    short = models.TextField(_("Laburpena"), blank=True, null=True)

    published_at = models.DateTimeField(
        _("Argitaratze-data"),
        auto_now_add=True
    )

    author = models.CharField(_("Egilea"), max_length=100)

    published = models.BooleanField(
        _("Argitaratua"),
        default=True
    )
    featured = models.BooleanField(
        _("Destacada"),
        default=False,
    )
    cover_image = models.ForeignKey(
        "GalleryImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cover_for_galleries",
        verbose_name=_("Fotografía de portada"),
    )

    class Meta:
        verbose_name = _("Galeria")
        verbose_name_plural = _("Galeriak")
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("gallery_app:gallery_detail", kwargs={"pk": self.pk})

    def clean(self):
        super().clean()
        if (
            self.cover_image
            and self.pk
            and self.cover_image.gallery_id != self.pk
        ):
            raise ValidationError(
                {"cover_image": _("La fotografía de portada debe pertenecer a esta galería.")}
            )


class GalleryImage(models.Model):
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        _("Irudia"),
        upload_to="gallery/images/"
    )

    title = models.CharField(
        _("Izenburua"),
        max_length=200,
        blank=True
    )

    order = models.PositiveIntegerField(
        _("Ordena"),
        default=0
    )

    class Meta:
        ordering = ["order"]
        verbose_name = _("Galeriako irudia")
        verbose_name_plural = _("Galeriako irudiak")

    def __str__(self):
        return f"{self.gallery.title} - {self.id}"

    def process_image(self, image_field, max_width=1600, quality=90):
        img = Image.open(image_field)

        # Apply EXIF orientation so saved bytes are physically correct.
        img = ImageOps.exif_transpose(img)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        output = BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)

        base_name = os.path.splitext(image_field.name)[0]
        filename = f"{base_name}.jpg"
        return ContentFile(output.getvalue(), name=filename)

    def _image_has_changed(self):
        if not self.image:
            return False
        if not self.pk:
            return True
        old = type(self).objects.filter(pk=self.pk).only("image").first()
        if not old:
            return True
        return old.image.name != self.image.name

    def save(self, *args, **kwargs):
        if self._image_has_changed():
            self.image = self.process_image(self.image)
        super().save(*args, **kwargs)
