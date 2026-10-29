from django.db.utils import IntegrityError
from django.test import TestCase
from model_bakery import baker

from produtos.models import Produto, ProdutoFornecedor, UnidadeMedida


class UnidadeMedidaModelTest(TestCase):
    def setUp(self):
        self.tenant = baker.make('tenants.Tenant', name='Tenant Teste')

    def test_str_retorna_nome_e_abreviacao(self):
        unidade = UnidadeMedida(tenant=self.tenant, name='Quilograma', abbreviation='kg')
        self.assertEqual(str(unidade), 'Quilograma (kg)')

    def test_nome_unico_por_tenant(self):
        UnidadeMedida.objects.create(tenant=self.tenant, name='Quilograma', abbreviation='kg')
        with self.assertRaises(IntegrityError):
            UnidadeMedida.objects.create(tenant=self.tenant, name='Quilograma', abbreviation='g')

    def test_abreviacao_unica_por_tenant(self):
        UnidadeMedida.objects.create(tenant=self.tenant, name='Litro', abbreviation='L')
        with self.assertRaises(IntegrityError):
            UnidadeMedida.objects.create(tenant=self.tenant, name='Litros', abbreviation='L')

    def test_mesmo_nome_em_tenants_diferentes_e_permitido(self):
        outro_tenant = baker.make('tenants.Tenant', name='Outro Tenant')
        UnidadeMedida.objects.create(tenant=self.tenant, name='Unidade', abbreviation='un')
        unidade_outro = UnidadeMedida.objects.create(tenant=outro_tenant, name='Unidade', abbreviation='ou')
        self.assertIsNotNone(unidade_outro.pk)

    def test_mesma_abreviacao_em_tenants_diferentes_e_permitida(self):
        outro_tenant = baker.make('tenants.Tenant', name='Outro Tenant')
        UnidadeMedida.objects.create(tenant=self.tenant, name='Unidade', abbreviation='un')
        unidade_outro = UnidadeMedida.objects.create(tenant=outro_tenant, name='Outra Unidade', abbreviation='un')
        self.assertIsNotNone(unidade_outro.pk)


class ProdutoModelTest(TestCase):
    def setUp(self):
        self.tenant = baker.make('tenants.Tenant', name='Tenant Teste')
        self.unidade = UnidadeMedida.objects.create(tenant=self.tenant, name='Unidade', abbreviation='un')

    def test_str_retorna_descricao(self):
        produto = Produto(tenant=self.tenant, code='P001', description='Morango', unidade_medida=self.unidade)
        self.assertEqual(str(produto), 'Morango')

    def test_codigo_unico_por_tenant(self):
        Produto.objects.create(tenant=self.tenant, code='P001', description='Produto A', unidade_medida=self.unidade)
        with self.assertRaises(IntegrityError):
            Produto.objects.create(
                tenant=self.tenant, code='P001', description='Produto B', unidade_medida=self.unidade
            )

    def test_descricao_unica_por_tenant(self):
        Produto.objects.create(
            tenant=self.tenant, code='P001', description='Produto Unico', unidade_medida=self.unidade
        )
        with self.assertRaises(IntegrityError):
            Produto.objects.create(
                tenant=self.tenant, code='P002', description='Produto Unico', unidade_medida=self.unidade
            )

    def test_mesmo_codigo_em_tenants_diferentes_e_permitido(self):
        outro_tenant = baker.make('tenants.Tenant', name='Outro Tenant')
        outra_unidade = UnidadeMedida.objects.create(tenant=outro_tenant, name='Unidade', abbreviation='un')

        Produto.objects.create(tenant=self.tenant, code='P001', description='Produto A', unidade_medida=self.unidade)
        produto_outro = Produto.objects.create(
            tenant=outro_tenant, code='P001', description='Produto B', unidade_medida=outra_unidade
        )
        self.assertIsNotNone(produto_outro.pk)

    def test_mesma_descricao_em_tenants_diferentes_e_permitida(self):
        outro_tenant = baker.make('tenants.Tenant', name='Outro Tenant')
        outra_unidade = UnidadeMedida.objects.create(tenant=outro_tenant, name='Unidade', abbreviation='un')

        Produto.objects.create(tenant=self.tenant, code='P001', description='Morango', unidade_medida=self.unidade)
        produto_outro = Produto.objects.create(
            tenant=outro_tenant, code='P002', description='Morango', unidade_medida=outra_unidade
        )
        self.assertIsNotNone(produto_outro.pk)


class ProdutoFornecedorModelTest(TestCase):
    def setUp(self):
        self.tenant = baker.make('tenants.Tenant', name='Tenant Teste')
        self.unidade = UnidadeMedida.objects.create(tenant=self.tenant, name='Unidade', abbreviation='un')
        self.produto = Produto.objects.create(
            tenant=self.tenant, code='P001', description='Morango', unidade_medida=self.unidade
        )
        self.fornecedor = baker.make('fornecedores.Fornecedor', tenant=self.tenant)

    def test_str_retorna_produto_fornecedor_codigo(self):
        pf = ProdutoFornecedor(produto=self.produto, fornecedor=self.fornecedor, codigo_no_fornecedor='F123')
        self.assertEqual(str(pf), f'Morango - {self.fornecedor.name} (F123)')

    def test_codigo_unico_por_fornecedor(self):
        ProdutoFornecedor.objects.create(produto=self.produto, fornecedor=self.fornecedor, codigo_no_fornecedor='F123')
        with self.assertRaises(IntegrityError):
            ProdutoFornecedor.objects.create(
                produto=self.produto, fornecedor=self.fornecedor, codigo_no_fornecedor='F123'
            )

    def test_mesmo_codigo_com_fornecedor_diferente_e_permitido(self):
        outro_fornecedor = baker.make('fornecedores.Fornecedor', tenant=self.tenant)
        ProdutoFornecedor.objects.create(produto=self.produto, fornecedor=self.fornecedor, codigo_no_fornecedor='F123')
        pf_outro = ProdutoFornecedor.objects.create(
            produto=self.produto, fornecedor=outro_fornecedor, codigo_no_fornecedor='F123'
        )
        self.assertIsNotNone(pf_outro.pk)

    def test_mesmo_produto_com_multiplos_fornecedores_e_permitido(self):
        outro_fornecedor = baker.make('fornecedores.Fornecedor', tenant=self.tenant)
        ProdutoFornecedor.objects.create(produto=self.produto, fornecedor=self.fornecedor, codigo_no_fornecedor='F123')
        pf_outro = ProdutoFornecedor.objects.create(
            produto=self.produto, fornecedor=outro_fornecedor, codigo_no_fornecedor='F456'
        )
        self.assertIsNotNone(pf_outro.pk)
        self.assertEqual(self.produto.produto_fornecedores.count(), 2)
