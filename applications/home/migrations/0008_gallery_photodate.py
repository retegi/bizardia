# Generated by Django 5.2.1 on 2025-06-07 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_rename_imagen_gallery_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='photoDate',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
