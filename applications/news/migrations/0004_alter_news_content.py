# Generated by Django 5.2.3 on 2025-06-18 16:07

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_news_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='content',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
    ]
