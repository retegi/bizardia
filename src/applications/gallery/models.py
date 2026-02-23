from django.db import models
from tinymce.models import HTMLField
from django.utils.translation import gettext_lazy as _
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile



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

    class Meta:
        verbose_name = _("Galeria")
        verbose_name_plural = _("Galeriak")
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


# 🔹 NUEVO MODELO
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

    def compress_image(self, image_field, max_width=1600, quality=80):
        img = Image.open(image_field)

        # Convertir a RGB si viene PNG con transparencia
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Redimensionar si es demasiado grande
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        output = BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)

        filename = image_field.name.split(".")[0] + ".jpg"

        return ContentFile(output.getvalue(), name=filename)

    def save(self, *args, **kwargs):

        # Solo comprimir cuando es nueva imagen
        if self.image and not self.pk:
            self.image = self.compress_image(self.image)

        super().save(*args, **kwargs)
