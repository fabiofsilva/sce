from unittest.mock import Mock

from django.test import TestCase

from core.permissions import TenantActivePermission


class TenantActivePermissionTest(TestCase):
    def setUp(self):
        self.permissao = TenantActivePermission()

    def _criar_request(self, autenticado=True, is_staff=False, tenant=None):
        usuario = Mock()
        usuario.is_authenticated = autenticado
        usuario.is_staff = is_staff
        usuario.tenant = tenant
        request = Mock()
        request.user = usuario
        return request

    def _criar_tenant(self, ativo=True):
        tenant = Mock()
        tenant.is_active = ativo
        return tenant

    def test_tenant_ativo_permite_acesso(self):
        request = self._criar_request(tenant=self._criar_tenant(ativo=True))
        self.assertTrue(self.permissao.has_permission(request, None))

    def test_tenant_inativo_bloqueia_acesso(self):
        request = self._criar_request(tenant=self._criar_tenant(ativo=False))
        self.assertFalse(self.permissao.has_permission(request, None))

    def test_superusuario_sem_tenant_permite_acesso(self):
        request = self._criar_request(is_staff=True, tenant=None)
        self.assertTrue(self.permissao.has_permission(request, None))

    def test_usuario_nao_autenticado_bloqueia_acesso(self):
        request = self._criar_request(autenticado=False, tenant=self._criar_tenant())
        self.assertFalse(self.permissao.has_permission(request, None))

    def test_usuario_sem_tenant_bloqueia_acesso(self):
        request = self._criar_request(tenant=None)
        self.assertFalse(self.permissao.has_permission(request, None))
