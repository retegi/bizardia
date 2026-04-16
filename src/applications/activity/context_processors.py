from .permissions import can_access_django_admin, can_view_activity_registration_list


def activity_navigation_permissions(request):
    user = request.user
    return {
        "can_access_django_admin": can_access_django_admin(user),
        "can_view_activity_registration_list": can_view_activity_registration_list(user),
    }
