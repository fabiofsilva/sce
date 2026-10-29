from core.viewsets import TenantScopedViewSet

from ..models import Fornecedor
from .serializers import FornecedorSerializer


class FornecedorViewSet(TenantScopedViewSet):
    queryset = Fornecedor.objects.all().order_by('tenant_id', 'name')
    serializer_class = FornecedorSerializer
