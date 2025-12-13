from rest_framework.permissions import BasePermission, SAFE_METHODS


def get_user_role(user):
    """
    Small helper to safely get the user's role from UserProfile.
    Returns 'admin', 'farmer', 'worker', or None.
    """
    if not user or not user.is_authenticated:
        return None

    profile = getattr(user, "profile", None)
    if profile is None:
        return None

    return getattr(profile, "role", None)


class ReadOnlyOrFarmer(BasePermission):
    """
    Permission for SensorReadingViewSet

    - GET / HEAD / OPTIONS:
        allowed for roles: admin, farmer, worker
    - POST / PUT / PATCH / DELETE:
        allowed only for roles: admin, farmer
        (worker cannot modify data)
    """

    def has_permission(self, request, view):
        role = get_user_role(request.user)
        if role is None:
            return False

        # Read-only methods (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return role in ["admin", "farmer", "worker"]

        # Write methods (POST, PUT, PATCH, DELETE)
        return role in ["admin", "farmer"]


class IsAdminFarmerWorker(BasePermission):
    """
    Generic read-only permission:

    - Any authenticated user with role admin/farmer/worker is allowed.
    - Use this on ReadOnlyModelViewSet endpoints (GET only),
      like anomalies and recommendations.
    """

    def has_permission(self, request, view):
        role = get_user_role(request.user)
        if role is None:
            return False

        return role in ["admin", "farmer", "worker"]


class IsAdminOnly(BasePermission):
    """
    Example permission if later you want endpoints that ONLY admin can access.
    Not required yet, but ready for future use.
    """

    def has_permission(self, request, view):
        role = get_user_role(request.user)
        return role == "admin"
