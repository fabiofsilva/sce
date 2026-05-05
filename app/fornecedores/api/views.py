from core.viewsets import TenantScopedViewSet

from ..models import Fornecedor
from .serializers import FornecedorSerializer


class FornecedorViewSet(TenantScopedViewSet):
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer

    def get_serializer_context(self):
        return super().get_serializer_context()

