from unittest.mock import Mock

from django.test import TestCase
from model_bakery import baker

from produtos.api.serializers import ProdutoFornecedorSerializer, ProdutoSerializer, UnidadeMedidaSerializer


class UnidadeMedidaSerializerTest(TestCase):
    def setUp(self):
        self.tenant = baker.make('tenants.Tenant')
        self.usuario = baker.make('users.User', tenant=self.tenant)
        self.request = Mock()
        self.request.user = self.usuario

    def _serializer(self, data, instance=None, partial=False):
        return UnidadeMedidaSerializer(instance, data=data, partial=partial, context={'request': self.request})

    def test_serializa_campos_esperados(self):
        unidade = baker.make('produtos.UnidadeMedida')
        serializer = UnidadeMedidaSerializer(unidade)
        self.assertEqual(set(serializer.data.keys()), {'id', 'name', 'abbreviation'})

    def test_desserializa_dados_validos(self):
        dados = {'name': 'Quilograma', 'abbreviation': 'kg'}
        serializer = self._serializer(dados)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_nome_obrigatorio(self):
        serializer = self._serializer({'abbreviation': 'kg'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_abreviacao_obrigatoria(self):
        serializer = self._serializer({'name': 'Quilograma'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('abbreviation', serializer.errors)

    def test_nome_duplicado_no_mesmo_tenant_retorna_erro(self):
        baker.make('produtos.UnidadeMedida', tenant=self.tenant, name='Quilograma')
        serializer = self._serializer({'name': 'Quilograma', 'abbreviation': 'kg'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_nome_duplicado_em_tenant_diferente_e_valido(self):
        baker.make('produtos.UnidadeMedida', tenant=baker.make('tenants.Tenant'), name='Quilograma')
        serializer = self._serializer({'name': 'Quilograma', 'abbreviation': 'kg'})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_abreviacao_duplicada_no_mesmo_tenant_retorna_erro(self):
        baker.make('produtos.UnidadeMedida', tenant=self.tenant, abbreviation='kg')
        serializer = self._serializer({'name': 'Quilo', 'abbreviation': 'kg'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_abreviacao_duplicada_em_tenant_diferente_e_valida(self):
        baker.make('produtos.UnidadeMedida', tenant=baker.make('tenants.Tenant'), abbreviation='kg')
        serializer = self._serializer({'name': 'Quilograma', 'abbreviation': 'kg'})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_nome_duplicado_na_edicao_do_proprio_registro_e_valido(self):
        unidade = baker.make('produtos.UnidadeMedida', tenant=self.tenant, name='Quilograma')
        serializer = self._serializer({'name': 'Quilograma'}, instance=unidade, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class ProdutoFornecedorSerializerTest(TestCase):
    def setUp(self):
        self.tenant = baker.make('tenants.Tenant')
        self.usuario = baker.make('users.User', tenant=self.tenant)
        self.unidade = baker.make('produtos.UnidadeMedida', tenant=self.tenant)
        self.produto = baker.make('produtos.Produto', tenant=self.tenant, unidade_medida=self.unidade)
        self.fornecedor = baker.make('fornecedores.Fornecedor', tenant=self.tenant)
        self.request = Mock()
        self.request.user = self.usuario

    def _serializer(self, data, instance=None, partial=False):
        return ProdutoFornecedorSerializer(instance, data=data, partial=partial, context={'request': self.request})

    def test_serializa_campos_esperados(self):
        pf = baker.make('produtos.ProdutoFornecedor', produto=self.produto, fornecedor=self.fornecedor)
        serializer = ProdutoFornecedorSerializer(pf)
        self.assertEqual(
            set(serializer.data.keys()),
            {'id', 'fornecedor', 'fornecedor_name', 'codigo_no_fornecedor', 'fator_conversao', 'created_at'},
        )

    def test_desserializa_dados_validos(self):
        dados = {'fornecedor': self.fornecedor.id, 'codigo_no_fornecedor': 'F123', 'fator_conversao': '1.5'}
        serializer = self._serializer(dados)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_fornecedor_obrigatorio(self):
        serializer = self._serializer({'codigo_no_fornecedor': 'F123'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('fornecedor', serializer.errors)

    def test_codigo_no_fornecedor_obrigatorio(self):
        serializer = self._serializer({'fornecedor': self.fornecedor.id})
        self.assertFalse(serializer.is_valid())
        self.assertIn('codigo_no_fornecedor', serializer.errors)

    def test_codigo_duplicado_mesmo_fornecedor_retorna_erro(self):
        baker.make('produtos.ProdutoFornecedor', fornecedor=self.fornecedor, codigo_no_fornecedor='F123')
        serializer = self._serializer({'fornecedor': self.fornecedor.id, 'codigo_no_fornecedor': 'F123'})
        self.assertFalse(serializer.is_valid())

    def test_codigo_duplicado_fornecedor_diferente_e_valido(self):
        outro_fornecedor = baker.make('fornecedores.Fornecedor', tenant=self.tenant)
        baker.make('produtos.ProdutoFornecedor', fornecedor=self.fornecedor, codigo_no_fornecedor='F123')
        serializer = self._serializer({'fornecedor': outro_fornecedor.id, 'codigo_no_fornecedor': 'F123'})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_campos_read_only_ignorados_no_input(self):
        dados = {
            'fornecedor': self.fornecedor.id,
            'codigo_no_fornecedor': 'F123',
            'id': 999,
            'created_at': '2024-01-01T00:00:00Z',
        }
        serializer = self._serializer(dados)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('id', serializer.validated_data)
        self.assertNotIn('created_at', serializer.validated_data)


class ProdutoSerializerTest(TestCase):
    def setUp(self):
        self.tenant = baker.make('tenants.Tenant')
        self.usuario = baker.make('users.User', tenant=self.tenant)
        self.unidade = baker.make('produtos.UnidadeMedida', tenant=self.tenant)
        self.request = Mock()
        self.request.user = self.usuario

    def _serializer(self, data, instance=None, partial=False):
        return ProdutoSerializer(instance, data=data, partial=partial, context={'request': self.request})

    def test_serializa_campos_esperados(self):
        produto = baker.make('produtos.Produto')
        serializer = ProdutoSerializer(produto)
        self.assertEqual(
            set(serializer.data.keys()),
            {
                'id',
                'code',
                'description',
                'fornecedores',
                'unidade_medida',
                'unidade_medida_name',
                'priority',
                'is_on_demand',
                'minimum_quantity',
                'current_quantity',
                'is_active',
                'created_at',
                'updated_at',
            },
        )

    def test_desserializa_dados_validos(self):
        dados = {
            'code': 'P001',
            'description': 'Morango',
            'unidade_medida': self.unidade.id,
        }
        serializer = self._serializer(dados)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_code_obrigatorio(self):
        serializer = self._serializer({'description': 'Morango', 'unidade_medida': self.unidade.id})
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)

    def test_description_obrigatoria(self):
        serializer = self._serializer({'code': 'P001', 'unidade_medida': self.unidade.id})
        self.assertFalse(serializer.is_valid())
        self.assertIn('description', serializer.errors)

    def test_unidade_medida_obrigatoria(self):
        serializer = self._serializer({'code': 'P001', 'description': 'Morango'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('unidade_medida', serializer.errors)

    def test_code_duplicado_no_mesmo_tenant_retorna_erro(self):
        baker.make('produtos.Produto', tenant=self.tenant, code='P001')
        serializer = self._serializer({'code': 'P001', 'description': 'Outro', 'unidade_medida': self.unidade.id})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_code_duplicado_em_tenant_diferente_e_valido(self):
        baker.make('produtos.Produto', tenant=baker.make('tenants.Tenant'), code='P001')
        serializer = self._serializer({'code': 'P001', 'description': 'Produto', 'unidade_medida': self.unidade.id})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_description_duplicada_no_mesmo_tenant_retorna_erro(self):
        baker.make('produtos.Produto', tenant=self.tenant, description='Morango')
        serializer = self._serializer({'code': 'P002', 'description': 'Morango', 'unidade_medida': self.unidade.id})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_description_duplicada_em_tenant_diferente_e_valida(self):
        baker.make('produtos.Produto', tenant=baker.make('tenants.Tenant'), description='Morango')
        serializer = self._serializer({'code': 'P001', 'description': 'Morango', 'unidade_medida': self.unidade.id})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_code_duplicado_na_edicao_do_proprio_registro_e_valido(self):
        produto = baker.make('produtos.Produto', tenant=self.tenant, code='P001')
        serializer = self._serializer({'code': 'P001'}, instance=produto, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_description_duplicada_na_edicao_do_proprio_registro_e_valida(self):
        produto = baker.make('produtos.Produto', tenant=self.tenant, description='Morango')
        serializer = self._serializer({'description': 'Morango'}, instance=produto, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_campos_read_only_ignorados_no_input(self):
        dados = {
            'code': 'P001',
            'description': 'Morango',
            'unidade_medida': self.unidade.id,
            'id': 999,
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        serializer = self._serializer(dados)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('id', serializer.validated_data)
        self.assertNotIn('created_at', serializer.validated_data)
        self.assertNotIn('updated_at', serializer.validated_data)
