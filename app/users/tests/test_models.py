from django.test import TestCase

from tenants.models import Tenant
from users.models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='Franquia SP')

    def test_str_retorna_email(self):
        usuario = User(email='joao@franquia.com')
        self.assertEqual(str(usuario), 'joao@franquia.com')

    def test_campo_autenticacao_e_email(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_campos_obrigatorios_sao_vazios(self):
        self.assertEqual(User.REQUIRED_FIELDS, [])

    def test_is_active_padrao_verdadeiro(self):
        usuario = User.objects.create_user(email='ativo@franquia.com', password='senha123', tenant=self.tenant)
        self.assertTrue(usuario.is_active)

    def test_is_staff_padrao_falso(self):
        usuario = User.objects.create_user(email='operador@franquia.com', password='senha123', tenant=self.tenant)
        self.assertFalse(usuario.is_staff)

    def test_senha_e_armazenada_com_hash(self):
        usuario = User.objects.create_user(email='hash@franquia.com', password='senha123', tenant=self.tenant)
        self.assertNotEqual(usuario.password, 'senha123')
        self.assertTrue(usuario.check_password('senha123'))

    def test_superusuario_tem_is_staff_verdadeiro(self):
        superusuario = User.objects.create_superuser(email='admin@sistema.com', password='admin123')
        self.assertTrue(superusuario.is_staff)
        self.assertTrue(superusuario.is_superuser)

    def test_superusuario_sem_tenant(self):
        superusuario = User.objects.create_superuser(email='admin@sistema.com', password='admin123')
        self.assertIsNone(superusuario.tenant)

    def test_criar_usuario_sem_email_levanta_erro(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='senha123')
