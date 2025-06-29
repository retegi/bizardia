# Generated by Django 5.2.1 on 2025-06-06 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('content', models.TextField(blank=True, null=True)),
                ('short', models.TextField(blank=True, null=True)),
                ('published_at', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='news/')),
                ('author', models.CharField(max_length=100)),
                ('published', models.BooleanField(blank=True, null=True)),
            ],
        ),
    ]
