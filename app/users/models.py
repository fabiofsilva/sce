from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='E-mail', unique=True)
    tenant = models.ForeignKey('tenants.Tenant', verbose_name='Tenant', on_delete=models.PROTECT, null=True, blank=True,
                               related_name='usuarios')
    first_name = models.CharField(verbose_name='Nome', max_length=150, blank=True)
    last_name = models.CharField(verbose_name='Sobrenome', max_length=150, blank=True)
    is_active = models.BooleanField(verbose_name='Ativo', default=True)
    is_staff = models.BooleanField(verbose_name='Staff', default=False)
    date_joined = models.DateTimeField(verbose_name='Data de entrada', auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email
