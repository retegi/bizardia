from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(default=timezone.now)
    membership_number = models.CharField(max_length=20)
    num_diners = models.PositiveIntegerField()
    selected_tables = models.JSONField()
    room_urkabe = models.BooleanField(default=False)
    room_goiko = models.BooleanField(default=False)
    is_birthday = models.BooleanField(default=False)
    fires = models.IntegerField(default=0, choices=[(i, str(i)) for i in range(5)])
    ovens = models.IntegerField(default=0, choices=[(i, str(i)) for i in range(3)])
    barbacue = models.BooleanField(default=False)
    activities = models.JSONField(default=list, blank=True)
    custom_activity = models.CharField(max_length=100, blank=True)


    def __str__(self):
        return f"{self.reservation_date} - {self.user.username}"

