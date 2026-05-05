from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .permissions import TenantActivePermission


class TenantScopedViewSet(viewsets.ModelViewSet):
    """ViewSet base que restringe todas as operações ao tenant do usuário autenticado."""

    # campo (ou lookup) usado para filtrar pelo tenant — sobrescreva quando o tenant
    # não estiver no model (ex: 'produto__tenant' em MovimentacaoEstoque)
    tenant_field = 'tenant'

    permission_classes = [IsAuthenticated, TenantActivePermission]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return super().get_queryset().none()
        usuario = self.request.user
        # superusuário sem tenant enxerga todos os dados — útil no Swagger e para suporte
        if usuario.is_staff and usuario.tenant is None:
            return super().get_queryset()
        return super().get_queryset().filter(**{self.tenant_field: usuario.tenant})

    def perform_create(self, serializer):
        # quando tenant é indireto, o save não injeta nada — a subclasse valida pelo serializer
        if self.tenant_field == 'tenant':
            serializer.save(tenant=self.request.user.tenant)
        else:
            serializer.save()
