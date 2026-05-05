from rest_framework.permissions import BasePermission


class TenantActivePermission(BasePermission):
    """Bloqueia requisições de usuários cujo tenant está inativo. Superusuários (tenant=None) são isentos."""

    def has_permission(self, request, view):
        usuario = request.user
        if not usuario or not usuario.is_authenticated:
            return False
        # superusuários do sistema não pertencem a nenhum tenant e não devem ser barrados aqui
        if usuario.is_staff and usuario.tenant is None:
            return True
        return usuario.tenant is not None and usuario.tenant.is_active
