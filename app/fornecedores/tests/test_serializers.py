from unittest.mock import Mock

from django.test import TestCase
from model_bakery import baker

from fornecedores.api.serializers import FornecedorSerializer


class FornecedorSerializerTest(TestCase):
    def setUp(self):
        self.tenant = baker.make('tenants.Tenant')
        self.usuario = baker.make('users.User', tenant=self.tenant)
        self.request = Mock()
        self.request.user = self.usuario

    def _serializer(self, data, instance=None, partial=False):
        return FornecedorSerializer(instance, data=data, partial=partial, context={'request': self.request})

    def test_serializa_campos_esperados(self):
        fornecedor = baker.make('fornecedores.Fornecedor')
        serializer = FornecedorSerializer(fornecedor)
        self.assertEqual(
            set(serializer.data.keys()), {'id', 'name', 'phone', 'email', 'notes', 'is_active', 'created_at'}
        )

    def test_desserializa_dados_validos(self):
        dados = {'name': 'Ceasa', 'phone': '11999999999', 'email': 'ceasa@email.com', 'is_active': True}
        serializer = self._serializer(dados)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_nome_obrigatorio(self):
        serializer = self._serializer({})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_email_invalido_e_rejeitado(self):
        serializer = self._serializer({'name': 'Fornecedor X', 'email': 'nao-e-email'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_nome_duplicado_no_mesmo_tenant_retorna_erro(self):
        baker.make('fornecedores.Fornecedor', tenant=self.tenant, name='Ceasa')
        serializer = self._serializer({'name': 'Ceasa'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_nome_duplicado_em_tenant_diferente_e_valido(self):
        baker.make('fornecedores.Fornecedor', tenant=baker.make('tenants.Tenant'), name='Ceasa')
        serializer = self._serializer({'name': 'Ceasa'})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_nome_duplicado_na_edicao_do_proprio_registro_e_valido(self):
        fornecedor = baker.make('fornecedores.Fornecedor', tenant=self.tenant, name='Ceasa')
        serializer = self._serializer({'name': 'Ceasa'}, instance=fornecedor, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_campos_read_only_ignorados_no_input(self):
        dados = {'name': 'Nechio', 'id': 999, 'created_at': '2024-01-01T00:00:00Z'}
        serializer = self._serializer(dados)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('id', serializer.validated_data)
        self.assertNotIn('created_at', serializer.validated_data)
