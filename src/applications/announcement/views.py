from django.shortcuts import render, get_object_or_404
from .models import Announcement


def announcement_detail(request, slug):
    announcement = get_object_or_404(Announcement, slug=slug)
    return render(request, "announcement/detail.html", {"announcement": announcement})
