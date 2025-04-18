from rest_framework.permissions import BasePermission

class IsAuthenticatedMedecin(BasePermission):
    """
    Allows access only to authenticated users in the 'MÉDECIN' group.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="Médecin").exists()
        )
