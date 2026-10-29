from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from produtos.models import Produto, ProdutoFornecedor, UnidadeMedida
from tenants.models import Tenant
from users.models import User


class ProdutoViewSetTest(APITestCase):
    def setUp(self):
        self.tenant = baker.make('tenants.Tenant')
        self.usuario = baker.make('users.User', tenant=self.tenant)
        self.unidade = baker.make('produtos.UnidadeMedida', tenant=self.tenant)
        self.client.force_authenticate(user=self.usuario)

    def test_lista_apenas_produtos_do_proprio_tenant(self):
        baker.make('produtos.Produto', tenant=self.tenant, _quantity=3)
        baker.make('produtos.Produto', tenant=baker.make(Tenant))
        response = self.client.get('/api/produtos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_nao_acessa_produto_de_outro_tenant(self):
        produto_alheio = baker.make('produtos.Produto', tenant=baker.make(Tenant))
        response = self.client.get(f'/api/produtos/{produto_alheio.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cria_produto_com_tenant_do_usuario_autenticado(self):
        dados = {'code': 'P001', 'description': 'Morango', 'unidade_medida': self.unidade.id}
        response = self.client.post('/api/produtos/', dados)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        produto = Produto.objects.get(id=response.data['id'])
        self.assertEqual(produto.tenant, self.tenant)

    def test_cria_ignora_tenant_enviado_no_body(self):
        outro_tenant = baker.make(Tenant)
        dados = {'code': 'P001', 'description': 'Morango', 'unidade_medida': self.unidade.id, 'tenant': outro_tenant.id}
        response = self.client.post('/api/produtos/', dados)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('tenant', response.data)
        produto = Produto.objects.get(id=response.data['id'])
        self.assertEqual(produto.tenant, self.tenant)

    def test_atualiza_ignora_tenant_enviado_no_body(self):
        outro_tenant = baker.make(Tenant)
        produto = baker.make('produtos.Produto', tenant=self.tenant, unidade_medida=self.unidade)
        dados = {'code': 'P002', 'description': 'Banana', 'unidade_medida': self.unidade.id, 'tenant': outro_tenant.id}
        response = self.client.put(f'/api/produtos/{produto.id}/', dados)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        produto.refresh_from_db()
        self.assertEqual(produto.tenant, self.tenant)

    def test_atualiza_parcialmente_ignora_tenant_enviado_no_body(self):
        outro_tenant = baker.make(Tenant)
        produto = baker.make('produtos.Produto', tenant=self.tenant, unidade_medida=self.unidade)
        response = self.client.patch(f'/api/produtos/{produto.id}/', {'tenant': outro_tenant.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        produto.refresh_from_db()
        self.assertEqual(produto.tenant, self.tenant)

    def test_acesso_anonimo_retorna_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/produtos/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tenant_inativo_retorna_403(self):
        tenant_inativo = baker.make(Tenant, is_active=False)
        usuario_inativo = baker.make(User, tenant=tenant_inativo)
        self.client.force_authenticate(user=usuario_inativo)
        response = self.client.get('/api/produtos/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_atualiza_parcialmente_produto_do_proprio_tenant(self):
        produto = baker.make('produtos.Produto', tenant=self.tenant, code='P001', description='Morango')
        response = self.client.patch(f'/api/produtos/{produto.id}/', {'description': 'Morango Vermelho'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        produto.refresh_from_db()
        self.assertEqual(produto.description, 'Morango Vermelho')

    def test_exclui_produto_do_proprio_tenant(self):
        produto = baker.make('produtos.Produto', tenant=self.tenant)
        response = self.client.delete(f'/api/produtos/{produto.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Produto.objects.filter(id=produto.id).exists())

    def test_nao_exclui_produto_de_outro_tenant(self):
        produto_alheio = baker.make('produtos.Produto', tenant=baker.make(Tenant))
        response = self.client.delete(f'/api/produtos/{produto_alheio.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Produto.objects.filter(id=produto_alheio.id).exists())

    def test_code_duplicado_no_mesmo_tenant_retorna_400(self):
        baker.make('produtos.Produto', tenant=self.tenant, code='P001')
        dados = {'code': 'P001', 'description': 'Outro', 'unidade_medida': self.unidade.id}
        response = self.client.post('/api/produtos/', dados)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_code_duplicado_em_tenant_diferente_e_permitido(self):
        baker.make('produtos.Produto', tenant=baker.make(Tenant), code='P001')
        dados = {'code': 'P001', 'description': 'Produto', 'unidade_medida': self.unidade.id}
        response = self.client.post('/api/produtos/', dados)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_description_duplicada_no_mesmo_tenant_retorna_400(self):
        baker.make('produtos.Produto', tenant=self.tenant, description='Morango')
        dados = {'code': 'P002', 'description': 'Morango', 'unidade_medida': self.unidade.id}
        response = self.client.post('/api/produtos/', dados)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_description_duplicada_em_tenant_diferente_e_permitida(self):
        baker.make('produtos.Produto', tenant=baker.make(Tenant), description='Morango')
        dados = {'code': 'P001', 'description': 'Morango', 'unidade_medida': self.unidade.id}
        response = self.client.post('/api/produtos/', dados)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_campos_obrigatorios_rejeitados(self):
        response = self.client.post('/api/produtos/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)
        self.assertIn('description', response.data)
        self.assertIn('unidade_medida', response.data)


class ProdutoFornecedorViewSetTest(APITestCase):
    def setUp(self):
        self.tenant = baker.make('tenants.Tenant')
        self.usuario = baker.make('users.User', tenant=self.tenant)
        self.unidade = baker.make('produtos.UnidadeMedida', tenant=self.tenant)
        self.produto = baker.make('produtos.Produto', tenant=self.tenant, unidade_medida=self.unidade)
        self.produto_outro_tenant = baker.make('produtos.Produto', tenant=baker.make(Tenant))
        self.fornecedor = baker.make('fornecedores.Fornecedor', tenant=self.tenant)
        self.client.force_authenticate(user=self.usuario)

    def test_lista_apenas_fornecedores_do_produto_do_proprio_tenant(self):
        baker.make('produtos.ProdutoFornecedor', produto=self.produto, _quantity=2)
        baker.make('produtos.ProdutoFornecedor', produto=self.produto_outro_tenant)
        response = self.client.get(f'/api/produtos/{self.produto.id}/fornecedores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_nao_acessa_fornecedor_de_produto_outro_tenant(self):
        pf = baker.make('produtos.ProdutoFornecedor', produto=self.produto_outro_tenant)
        response = self.client.get(f'/api/produtos/{self.produto_outro_tenant.id}/fornecedores/{pf.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cria_fornecedor_para_produto_do_proprio_tenant(self):
        dados = {'fornecedor': self.fornecedor.id, 'codigo_no_fornecedor': 'F123'}
        response = self.client.post(f'/api/produtos/{self.produto.id}/fornecedores/', dados)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pf = ProdutoFornecedor.objects.get(id=response.data['id'])
        self.assertEqual(pf.produto, self.produto)
        self.assertEqual(pf.fornecedor, self.fornecedor)

    def test_acesso_anonimo_retorna_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f'/api/produtos/{self.produto.id}/fornecedores/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tenant_inativo_retorna_403(self):
        tenant_inativo = baker.make(Tenant, is_active=False)
        usuario_inativo = baker.make(User, tenant=tenant_inativo)
        self.client.force_authenticate(user=usuario_inativo)
        response = self.client.get(f'/api/produtos/{self.produto.id}/fornecedores/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_atualiza_parcialmente_fornecedor_do_proprio_tenant(self):
        pf = baker.make('produtos.ProdutoFornecedor', produto=self.produto, codigo_no_fornecedor='F123')
        response = self.client.patch(
            f'/api/produtos/{self.produto.id}/fornecedores/{pf.id}/', {'fator_conversao': '2.5'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pf.refresh_from_db()
        self.assertEqual(float(pf.fator_conversao), 2.5)

    def test_exclui_fornecedor_do_proprio_tenant(self):
        pf = baker.make('produtos.ProdutoFornecedor', produto=self.produto)
        response = self.client.delete(f'/api/produtos/{self.produto.id}/fornecedores/{pf.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProdutoFornecedor.objects.filter(id=pf.id).exists())

    def test_nao_exclui_fornecedor_de_outro_tenant(self):
        pf = baker.make('produtos.ProdutoFornecedor', produto=self.produto_outro_tenant)
        response = self.client.delete(f'/api/produtos/{self.produto_outro_tenant.id}/fornecedores/{pf.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(ProdutoFornecedor.objects.filter(id=pf.id).exists())

    def test_codigo_duplicado_mesmo_fornecedor_retorna_400(self):
        baker.make('produtos.ProdutoFornecedor', fornecedor=self.fornecedor, codigo_no_fornecedor='F123')
        dados = {'fornecedor': self.fornecedor.id, 'codigo_no_fornecedor': 'F123'}
        response = self.client.post(f'/api/produtos/{self.produto.id}/fornecedores/', dados)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_codigo_duplicado_fornecedor_diferente_e_permitido(self):
        outro_fornecedor = baker.make('fornecedores.Fornecedor', tenant=self.tenant)
        baker.make('produtos.ProdutoFornecedor', fornecedor=self.fornecedor, codigo_no_fornecedor='F123')
        dados = {'fornecedor': outro_fornecedor.id, 'codigo_no_fornecedor': 'F123'}
        response = self.client.post(f'/api/produtos/{self.produto.id}/fornecedores/', dados)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_campos_obrigatorios_rejeitados(self):
        response = self.client.post(f'/api/produtos/{self.produto.id}/fornecedores/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fornecedor', response.data)

    def test_lista_vazia_para_produto_de_outro_tenant(self):
        baker.make('produtos.ProdutoFornecedor', produto=self.produto_outro_tenant)
        response = self.client.get(f'/api/produtos/{self.produto_outro_tenant.id}/fornecedores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_nao_cria_fornecedor_para_produto_de_outro_tenant(self):
        dados = {'fornecedor': self.fornecedor.id, 'codigo_no_fornecedor': 'F123'}
        response = self.client.post(f'/api/produtos/{self.produto_outro_tenant.id}/fornecedores/', dados)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(ProdutoFornecedor.objects.filter(produto=self.produto_outro_tenant).exists())

    def test_cria_fornecedor_para_produto_inexistente_retorna_404(self):
        dados = {'fornecedor': self.fornecedor.id, 'codigo_no_fornecedor': 'F123'}
        response = self.client.post('/api/produtos/999999/fornecedores/', dados)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nao_vincula_fornecedor_de_outro_tenant(self):
        fornecedor_outro_tenant = baker.make('fornecedores.Fornecedor', tenant=baker.make(Tenant))
        dados = {'fornecedor': fornecedor_outro_tenant.id, 'codigo_no_fornecedor': 'F123'}
        response = self.client.post(f'/api/produtos/{self.produto.id}/fornecedores/', dados)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fornecedor', response.data)

    def test_patch_sem_fornecedor_detecta_codigo_duplicado(self):
        baker.make('produtos.ProdutoFornecedor', fornecedor=self.fornecedor, codigo_no_fornecedor='F123')
        pf = baker.make(
            'produtos.ProdutoFornecedor', produto=self.produto, fornecedor=self.fornecedor, codigo_no_fornecedor='F999'
        )
        response = self.client.patch(
            f'/api/produtos/{self.produto.id}/fornecedores/{pf.id}/', {'codigo_no_fornecedor': 'F123'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)


class UnidadeMedidaViewSetTest(APITestCase):
    def setUp(self):
        self.tenant = baker.make(Tenant)
        self.usuario = baker.make(User, tenant=self.tenant)
        self.client.force_authenticate(user=self.usuario)

    def test_lista_apenas_unidades_do_proprio_tenant(self):
        baker.make(UnidadeMedida, tenant=self.tenant, _quantity=3)
        baker.make(UnidadeMedida, tenant=baker.make(Tenant))
        response = self.client.get('/api/produtos/unidades/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_nao_acessa_unidade_de_outro_tenant(self):
        unidade_alheio = baker.make(UnidadeMedida, tenant=baker.make(Tenant))
        response = self.client.get(f'/api/produtos/unidades/{unidade_alheio.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cria_unidade_com_tenant_do_usuario_autenticado(self):
        dados = {'name': 'Quilograma', 'abbreviation': 'kg'}
        response = self.client.post('/api/produtos/unidades/', dados)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        unidade = UnidadeMedida.objects.get(id=response.data['id'])
        self.assertEqual(unidade.tenant, self.tenant)

    def test_cria_ignora_tenant_enviado_no_body(self):
        outro_tenant = baker.make(Tenant)
        dados = {'name': 'Quilograma', 'abbreviation': 'kg', 'tenant': outro_tenant.id}
        response = self.client.post('/api/produtos/unidades/', dados)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('tenant', response.data)
        unidade = UnidadeMedida.objects.get(id=response.data['id'])
        self.assertEqual(unidade.tenant, self.tenant)

    def test_atualiza_ignora_tenant_enviado_no_body(self):
        outro_tenant = baker.make(Tenant)
        unidade = baker.make(UnidadeMedida, tenant=self.tenant)
        dados = {'name': 'Grama', 'abbreviation': 'g', 'tenant': outro_tenant.id}
        response = self.client.put(f'/api/produtos/unidades/{unidade.id}/', dados)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unidade.refresh_from_db()
        self.assertEqual(unidade.tenant, self.tenant)

    def test_atualiza_parcialmente_ignora_tenant_enviado_no_body(self):
        outro_tenant = baker.make(Tenant)
        unidade = baker.make(UnidadeMedida, tenant=self.tenant)
        response = self.client.patch(f'/api/produtos/unidades/{unidade.id}/', {'tenant': outro_tenant.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unidade.refresh_from_db()
        self.assertEqual(unidade.tenant, self.tenant)

    def test_acesso_anonimo_retorna_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/produtos/unidades/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tenant_inativo_retorna_403(self):
        tenant_inativo = baker.make(Tenant, is_active=False)
        usuario_inativo = baker.make(User, tenant=tenant_inativo)
        self.client.force_authenticate(user=usuario_inativo)
        response = self.client.get('/api/produtos/unidades/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_atualiza_parcialmente_unidade_do_proprio_tenant(self):
        unidade = baker.make(UnidadeMedida, tenant=self.tenant, name='Quilograma')
        response = self.client.patch(f'/api/produtos/unidades/{unidade.id}/', {'abbreviation': 'Kg'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unidade.refresh_from_db()
        self.assertEqual(unidade.abbreviation, 'Kg')

    def test_exclui_unidade_do_proprio_tenant(self):
        unidade = baker.make(UnidadeMedida, tenant=self.tenant)
        response = self.client.delete(f'/api/produtos/unidades/{unidade.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UnidadeMedida.objects.filter(id=unidade.id).exists())

    def test_nao_exclui_unidade_de_outro_tenant(self):
        unidade_alheio = baker.make(UnidadeMedida, tenant=baker.make(Tenant))
        response = self.client.delete(f'/api/produtos/unidades/{unidade_alheio.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(UnidadeMedida.objects.filter(id=unidade_alheio.id).exists())

    def test_nome_duplicado_no_mesmo_tenant_retorna_400(self):
        baker.make(UnidadeMedida, tenant=self.tenant, name='Quilograma')
        response = self.client.post('/api/produtos/unidades/', {'name': 'Quilograma', 'abbreviation': 'kg'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_nome_duplicado_em_tenant_diferente_e_permitido(self):
        baker.make(UnidadeMedida, tenant=baker.make(Tenant), name='Quilograma')
        dados = {'name': 'Quilograma', 'abbreviation': 'kg'}
        response = self.client.post('/api/produtos/unidades/', dados)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_abreviacao_duplicada_no_mesmo_tenant_retorna_400(self):
        baker.make(UnidadeMedida, tenant=self.tenant, abbreviation='kg')
        response = self.client.post('/api/produtos/unidades/', {'name': 'Quilo', 'abbreviation': 'kg'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_abreviacao_duplicada_em_tenant_diferente_e_permitida(self):
        baker.make(UnidadeMedida, tenant=baker.make(Tenant), abbreviation='kg')
        dados = {'name': 'Quilograma', 'abbreviation': 'kg'}
        response = self.client.post('/api/produtos/unidades/', dados)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_campos_obrigatorios_rejeitados(self):
        response = self.client.post('/api/produtos/unidades/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('abbreviation', response.data)
