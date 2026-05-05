from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from model_bakery import baker
from rest_framework import serializers, status, viewsets
from rest_framework.routers import DefaultRouter
from rest_framework.test import APITestCase

from core.viewsets import TenantScopedViewSet
from tenants.models import Tenant
from users.models import User


# Setup mínimo para testar a classe base sobre um model real com FK tenant.
# Usamos User como cobaia porque já tem o campo — o foco é o comportamento
# da TenantScopedViewSet, não a semântica de gerenciar usuários via API.
class _UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'tenant']


class _UserTestViewSet(TenantScopedViewSet):
    queryset = User.objects.all()
    serializer_class = _UserSerializer


_router = DefaultRouter()
_router.register('user-test', _UserTestViewSet, basename='user-test')
urlpatterns = _router.urls


@override_settings(ROOT_URLCONF='core.tests.test_viewsets')
class TenantScopedViewSetIntegracaoTest(APITestCase):
    """
    Testes de integração para validação de escopo e isolamento de dados por Tenant.
    Verifica se o usuário possui acesso aos endpoints e se a visibilidade dos registros
    está restrita ao Tenant ao qual ele pertence.
    Nota: Utiliza-se `force_authenticate` para isolar a lógica de autorização e escopo
    do processo de autenticação JWT, que não é o foco destes testes.
    """

    def setUp(self):
        self.tenant_a = baker.make(Tenant)
        self.tenant_b = baker.make(Tenant)
        self.usuario_a = baker.make(User, tenant=self.tenant_a)
        self.usuario_b = baker.make(User, tenant=self.tenant_b)
        self.superuser = User.objects.create_superuser(email='admin@sistema.com', password='admin123')

    def test_acesso_anonimo_retorna_401(self):
        response = self.client.get('/user-test/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_usuario_de_tenant_inativo_retorna_403(self):
        tenant_inativo = baker.make(Tenant, is_active=False)
        usuario_inativo = baker.make(User, tenant=tenant_inativo)
        self.client.force_authenticate(user=usuario_inativo)
        response = self.client.get('/user-test/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_autenticado_ve_apenas_registros_do_proprio_tenant(self):
        self.client.force_authenticate(user=self.usuario_a)
        response = self.client.get('/user-test/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.usuario_a.id, ids)
        self.assertNotIn(self.usuario_b.id, ids)
        self.assertNotIn(self.superuser.id, ids)

    def test_superuser_ve_todos_os_registros(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/user-test/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(len(ids), 3)
        self.assertIn(self.usuario_a.id, ids)
        self.assertIn(self.usuario_b.id, ids)
        self.assertIn(self.superuser.id, ids)


class TenantScopedViewSetTenantFieldTest(TestCase):
    def test_tenant_field_customizado_e_usado_como_lookup_no_filtro(self):
        class _ViewSetIndireto(TenantScopedViewSet):
            tenant_field = 'produto__tenant'

        viewset = _ViewSetIndireto()
        viewset.request = Mock()
        viewset.request.user.is_staff = False
        tenant_do_usuario = Mock()
        viewset.request.user.tenant = tenant_do_usuario

        qs_base = Mock()
        with patch.object(viewsets.ModelViewSet, 'get_queryset', return_value=qs_base):
            viewset.get_queryset()

        qs_base.filter.assert_called_once_with(produto__tenant=tenant_do_usuario)
