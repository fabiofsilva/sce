from django.db import models


class Fornecedor(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.PROTECT, verbose_name='Tenant',
                               related_name='fornecedores')
    name = models.CharField(verbose_name='Nome', max_length=255)
    phone = models.CharField(verbose_name='Telefone', max_length=20, blank=True, null=True)
    email = models.EmailField(verbose_name='E-mail', blank=True, null=True)
    notes = models.TextField(verbose_name='Observações', blank=True, null=True)
    is_active = models.BooleanField(verbose_name='Ativo', default=True)
    created_at = models.DateTimeField(verbose_name='Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'name'], name='unique_fornecedor')
        ]

    def __str__(self):
        return self.name
