from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    partner_number = models.PositiveIntegerField(unique=True)
    movil = models.CharField(max_length=20)
    movil2 = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    partner_date = models.DateField()
    related_partner = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='related_profiles')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.partner_number})"

# Create your models here.
