from django.db.utils import IntegrityError
from django.test import TestCase
from model_bakery import baker

from fornecedores.models import Fornecedor


class FornecedorModelTest(TestCase):
    def setUp(self):
        self.tenant = baker.make('tenants.Tenant', name='Franquia Teste')

    def test_str_retorna_nome(self):
        fornecedor = Fornecedor(name='Ceasa', tenant=self.tenant)
        self.assertEqual(str(fornecedor), 'Ceasa')

    def test_nome_unico_por_tenant(self):
        Fornecedor.objects.create(name='Ceasa', tenant=self.tenant)
        with self.assertRaises(IntegrityError):
            Fornecedor.objects.create(name='Ceasa', tenant=self.tenant)

    def test_mesmo_nome_em_tenants_diferentes_e_permitido(self):
        outro_tenant = baker.make('tenants.Tenant', name='Franquia RJ')
        Fornecedor.objects.create(name='Ceasa', tenant=self.tenant)
        fornecedor_rj = Fornecedor.objects.create(name='Ceasa', tenant=outro_tenant)
        self.assertIsNotNone(fornecedor_rj.pk)
