from unittest.mock import Mock

from django.test import TestCase
from rest_framework import serializers

from core.api.defaults import TenantAtualDefault


class TenantAtualDefaultTest(TestCase):
    def _criar_campo(self, tenant):
        request = Mock()
        request.user.tenant = tenant
        campo = Mock()
        campo.context = {'request': request}
        return campo

    def test_retorna_tenant_do_usuario_autenticado(self):
        tenant = Mock()
        self.assertIs(TenantAtualDefault()(self._criar_campo(tenant)), tenant)

    def test_usuario_sem_tenant_levanta_erro_de_validacao(self):
        with self.assertRaises(serializers.ValidationError):
            TenantAtualDefault()(self._criar_campo(None))
