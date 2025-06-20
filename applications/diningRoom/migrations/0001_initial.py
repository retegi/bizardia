# Generated by Django 5.2.1 on 2025-06-08 21:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('membership_number', models.CharField(max_length=50)),
                ('number_of_diners', models.PositiveIntegerField()),
                ('selected_tables', models.JSONField()),
                ('urkabe_selected', models.BooleanField(default=False)),
                ('goiko_selected', models.BooleanField(default=False)),
                ('meal_options', models.JSONField()),
                ('fire_count', models.PositiveSmallIntegerField(default=0)),
                ('oven_count', models.PositiveSmallIntegerField(default=0)),
                ('barbacue', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
