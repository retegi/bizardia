from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import Announcement


def announcement_detail(request, slug):
    announcement = get_object_or_404(Announcement, slug=slug)

    if not announcement.active:
        raise PermissionDenied

    now = timezone.now()
    if not (announcement.start_date <= now <= announcement.end_date):
        raise PermissionDenied

    if announcement.visibility == "members":
        is_member = request.user.is_authenticated and request.user.groups.filter(name="bazkideak").exists()
        if not is_member:
            raise PermissionDenied

    if announcement.visibility == "board":
        raise PermissionDenied

    return render(request, "announcement/detail.html", {"announcement": announcement})
