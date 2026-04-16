ACTIVITY_REGISTRATION_LIST_GROUPS = (
    "ekintza-antolatzaileak",
    "zuzendaritza-batzordea",
)


def can_access_django_admin(user):
    return user.is_authenticated and user.is_active and user.is_staff


def can_create_activity(user):
    if not user.is_authenticated:
        return False
    return (
        user.groups.filter(name="ekintza-antolatzaileak").exists()
        or user.groups.filter(name="zuzendaritza-batzordea").exists()
        or user.has_perm("activity.add_activity")
    )


def can_view_activity_registration_list(user):
    return (
        user.is_authenticated
        and user.groups.filter(name__in=ACTIVITY_REGISTRATION_LIST_GROUPS).exists()
    )
