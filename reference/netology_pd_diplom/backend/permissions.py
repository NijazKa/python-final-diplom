from rest_framework.permissions import BasePermission

# создаем отдельный класс для проверки доступа к админке
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff
