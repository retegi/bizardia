from .models import Profile


def user_profile(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"user_profile": None}

    profile = (
        Profile.objects.filter(user=request.user)
        .only("id", "avatar")
        .first()
    )
    return {"user_profile": profile}

