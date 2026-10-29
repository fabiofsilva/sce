from django.urls import path
from rest_framework.routers import DefaultRouter

from produtos.api.views import ProdutoFornecedorViewSet, ProdutoViewSet, UnidadeMedidaViewSet

router = DefaultRouter()
router.register(r'unidades', UnidadeMedidaViewSet, basename='unidade-medida')
router.register(r'', ProdutoViewSet, basename='produto')

produto_fornecedores_list = ProdutoFornecedorViewSet.as_view({'get': 'list', 'post': 'create'})
produto_fornecedores_detail = ProdutoFornecedorViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
)

urlpatterns = router.urls + [
    path('<int:produto_pk>/fornecedores/', produto_fornecedores_list, name='produto-fornecedor-list'),
    path('<int:produto_pk>/fornecedores/<int:pk>/', produto_fornecedores_detail, name='produto-fornecedor-detail'),
]
