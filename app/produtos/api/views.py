from django.shortcuts import get_object_or_404

from core.viewsets import TenantScopedViewSet
from produtos.api.serializers import ProdutoFornecedorSerializer, ProdutoSerializer, UnidadeMedidaSerializer
from produtos.models import Produto, ProdutoFornecedor, UnidadeMedida


class UnidadeMedidaViewSet(TenantScopedViewSet):
    queryset = UnidadeMedida.objects.all().order_by('tenant_id', 'name')
    serializer_class = UnidadeMedidaSerializer


class ProdutoViewSet(TenantScopedViewSet):
    queryset = Produto.objects.prefetch_related('produto_fornecedores__fornecedor').order_by('tenant_id', 'description')
    serializer_class = ProdutoSerializer


class ProdutoFornecedorViewSet(TenantScopedViewSet):
    queryset = ProdutoFornecedor.objects.select_related('fornecedor').order_by('id')
    serializer_class = ProdutoFornecedorSerializer
    tenant_field = 'produto__tenant'

    def get_queryset(self):
        # o filtro por tenant vem da classe base — aqui só restringe ao produto da URL
        return super().get_queryset().filter(produto_id=self.kwargs.get('produto_pk'))

    def _get_produto(self):
        usuario = self.request.user
        produtos = Produto.objects.all()
        if not (usuario.is_staff and usuario.tenant is None):
            produtos = produtos.filter(tenant=usuario.tenant)
        return get_object_or_404(produtos, id=self.kwargs['produto_pk'])

    def perform_create(self, serializer):
        serializer.save(produto=self._get_produto())
