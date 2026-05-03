import os

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Gallery


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = "__all__"


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "widget",
            MultipleFileInput(attrs={"multiple": True, "accept": "image/*"}),
        )
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(item, initial) for item in data]
        return single_file_clean(data, initial)


class MultipleGalleryImageUploadForm(forms.Form):
    gallery = forms.ModelChoiceField(
        queryset=Gallery.objects.all(),
        label=_("Galeria"),
        required=True,
    )
    images = MultipleFileField(
        label=_("Irudiak"),
        required=True,
    )

    def clean_images(self):
        files = self.files.getlist("images")
        if not files:
            raise forms.ValidationError(_("Aukeratu gutxienez irudi bat."))

        for uploaded_file in files:
            content_type = (uploaded_file.content_type or "").lower()
            if not content_type.startswith("image/"):
                raise forms.ValidationError(
                    _("Fitxategi baliogabea: %(name)s") % {"name": uploaded_file.name}
                )
        return files

    @staticmethod
    def title_from_filename(filename):
        return os.path.splitext(os.path.basename(filename))[0]
