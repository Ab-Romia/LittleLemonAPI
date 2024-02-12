from rest_framework import permissions


class ManagerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.group.filter(name="Manager").exists():
            return True


class DeliveryCrewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.group.filter(name="Delivery Crew").exists():
            return True
