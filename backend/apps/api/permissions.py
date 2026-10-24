from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAnalystOrReadOnly(BasePermission):
    """Lecture : tout utilisateur authentifié. Écriture et actions : staff ou groupe « analyste »."""

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return u.is_staff or u.groups.filter(name="analyste").exists()