from PIL import UnidentifiedImageError

from django.core.management.base import BaseCommand

from applications.gallery.models import GalleryImage


class Command(BaseCommand):
    help = "Fix EXIF orientation and recompress existing gallery images"

    def handle(self, *args, **options):
        fixed = 0
        failed = 0

        queryset = GalleryImage.objects.exclude(image="")
        total = queryset.count()

        self.stdout.write(f"Processing {total} gallery images...")

        for image_obj in queryset.iterator():
            try:
                image_obj.image = image_obj.process_image(image_obj.image)
                image_obj.save(update_fields=["image"])
                fixed += 1
            except (UnidentifiedImageError, OSError, ValueError) as exc:
                failed += 1
                self.stderr.write(
                    f"Failed image {image_obj.pk} ({image_obj.image.name}): {exc}"
                )

        self.stdout.write(self.style.SUCCESS(f"Fixed: {fixed}"))
        self.stdout.write(self.style.WARNING(f"Failed: {failed}"))
