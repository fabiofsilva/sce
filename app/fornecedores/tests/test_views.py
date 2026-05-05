from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from fornecedores.models import Fornecedor
from tenants.models import Tenant
from users.models import User


class FornecedorViewSetTest(APITestCase):
    def setUp(self):
        self.tenant = baker.make(Tenant)
        self.usuario = baker.make(User, tenant=self.tenant)
        self.client.force_authenticate(user=self.usuario)

    def test_lista_apenas_fornecedores_do_proprio_tenant(self):
        baker.make('fornecedores.Fornecedor', tenant=self.tenant, _quantity=3)
        baker.make('fornecedores.Fornecedor', tenant=baker.make(Tenant))
        response = self.client.get('/api/fornecedores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_nao_acessa_fornecedor_de_outro_tenant(self):
        fornecedor_alheio = baker.make('fornecedores.Fornecedor', tenant=baker.make(Tenant))
        response = self.client.get(f'/api/fornecedores/{fornecedor_alheio.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cria_fornecedor_com_tenant_do_usuario_autenticado(self):
        dados = {'name': 'Ceasa', 'phone': '11999999999', 'email': 'ceasa@ceasa.com', 'is_active': True}
        response = self.client.post('/api/fornecedores/', dados)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        fornecedor = Fornecedor.objects.get(id=response.data['id'])
        self.assertEqual(fornecedor.tenant, self.tenant)

    def test_acesso_anonimo_retorna_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/fornecedores/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tenant_inativo_retorna_403(self):
        tenant_inativo = baker.make(Tenant, is_active=False)
        usuario_inativo = baker.make(User, tenant=tenant_inativo)
        self.client.force_authenticate(user=usuario_inativo)
        response = self.client.get('/api/fornecedores/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_atualiza_parcialmente_fornecedor_do_proprio_tenant(self):
        fornecedor = baker.make('fornecedores.Fornecedor', tenant=self.tenant, name='Ceasa')
        response = self.client.patch(f'/api/fornecedores/{fornecedor.id}/', {'name': 'Ceasa SP'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fornecedor.refresh_from_db()
        self.assertEqual(fornecedor.name, 'Ceasa SP')

    def test_exclui_fornecedor_do_proprio_tenant(self):
        fornecedor = baker.make('fornecedores.Fornecedor', tenant=self.tenant)
        response = self.client.delete(f'/api/fornecedores/{fornecedor.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Fornecedor.objects.filter(id=fornecedor.id).exists())

    def test_nao_exclui_fornecedor_de_outro_tenant(self):
        fornecedor_alheio = baker.make('fornecedores.Fornecedor', tenant=baker.make(Tenant))
        response = self.client.delete(f'/api/fornecedores/{fornecedor_alheio.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Fornecedor.objects.filter(id=fornecedor_alheio.id).exists())

    def test_nome_duplicado_no_mesmo_tenant_retorna_400(self):
        baker.make('fornecedores.Fornecedor', tenant=self.tenant, name='Ceasa')
        response = self.client.post('/api/fornecedores/', {'name': 'Ceasa'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_nome_duplicado_em_tenant_diferente_e_permitido(self):
        baker.make('fornecedores.Fornecedor', tenant=baker.make(Tenant), name='Ceasa')
        response = self.client.post('/api/fornecedores/', {'name': 'Ceasa'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
