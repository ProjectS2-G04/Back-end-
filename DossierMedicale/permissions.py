# i created this just for testing my create and modify functions, u can delete it or modify it as u want

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsDoctorPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            "DOCTOR",
            "MEDECIN",
        ]


def check_doctor_permission(request):

    doctor_permission = IsDoctorPermission()
    if not doctor_permission.has_permission(request, None):
        raise PermissionDenied(
            detail="You do not have permission to perform this action."
        )
