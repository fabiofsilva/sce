from django.db.utils import IntegrityError
from django.test import TestCase

from tenants.models import Tenant


class TenantModelTest(TestCase):
    def test_str_retorna_nome(self):
        tenant = Tenant(name='Franquia SP')
        self.assertEqual(str(tenant), 'Franquia SP')

    def test_slug_gerado_automaticamente_a_partir_do_nome(self):
        tenant = Tenant.objects.create(name='Franquia São Paulo')
        self.assertEqual(tenant.slug, 'franquia-sao-paulo')

    def test_slug_existente_nao_e_sobrescrito(self):
        tenant = Tenant.objects.create(name='Franquia SP', slug='slug-personalizado')
        self.assertEqual(tenant.slug, 'slug-personalizado')

    def test_is_active_padrao_verdadeiro(self):
        tenant = Tenant.objects.create(name='Franquia RJ')
        self.assertTrue(tenant.is_active)

    def test_nome_deve_ser_unico(self):
        Tenant.objects.create(name='Franquia BH')
        with self.assertRaises(IntegrityError):
            Tenant.objects.create(name='Franquia BH')

    def test_slug_deve_ser_unico(self):
        Tenant.objects.create(name='Franquia DF', slug='franquia-df')
        with self.assertRaises(IntegrityError):
            Tenant.objects.create(name='Franquia Distrito Federal', slug='franquia-df')
