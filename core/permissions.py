from functools import wraps
from django.core.exceptions import PermissionDenied
from .models import UserPagePermission

def has_page_permission(user, page_key, action):
    if not user.is_authenticated:
        return False

    #System Admin has full acess.
    if user.is_superuser or user.role == "system_admin":
        return True

    allowed_actions = {"view", "add", "edit", "delete"}
    if action not in allowed_actions:
        return False

    permission = UserPagePermission.objects.filter(
        user=user,
        page_key=page_key,
    ).first()

    if not permission:
        return False

    return getattr(permission, f"can_{action}", False)

def require_page_permission(page_key, action):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not has_page_permission(
                request.user,
                page_key,
                action,
            ):
                raise PermissionDenied(
                    "You do have permission to perform this action"
                )
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator