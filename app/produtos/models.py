from django.db import models


class UnidadeMedida(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='unidades_medida')
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Unidades de Medida'
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'name'], name='unique_unidade_name'),
            models.UniqueConstraint(fields=['tenant', 'abbreviation'], name='unique_unidade_abbrev'),
        ]

    def __str__(self):
        return f'{self.name} ({self.abbreviation})'


class Produto(models.Model):
    class PriorityChoices(models.TextChoices):
        URGENTE = 'A', 'Urgente'
        ALTA = 'B', 'Alta'
        NORMAL = 'C', 'Normal'
        BAIXA = 'D', 'Baixa'

    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='produtos')
    unidade_medida = models.ForeignKey(UnidadeMedida, on_delete=models.PROTECT, related_name='produtos')
    code = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    priority = models.CharField(max_length=1, choices=PriorityChoices.choices, default=PriorityChoices.NORMAL)
    is_on_demand = models.BooleanField(default=False)
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'code'], name='unique_produto_code'),
            models.UniqueConstraint(fields=['tenant', 'description'], name='unique_produto_description'),
        ]

    def __str__(self):
        return self.description


class ProdutoFornecedor(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='produto_fornecedores')
    fornecedor = models.ForeignKey(
        'fornecedores.Fornecedor', on_delete=models.PROTECT, related_name='produto_fornecedores'
    )
    codigo_no_fornecedor = models.CharField(max_length=100)
    fator_conversao = models.DecimalField(max_digits=10, decimal_places=4, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['fornecedor', 'codigo_no_fornecedor'], name='unique_fornecedor_codigo'),
        ]

    def __str__(self):
        return f'{self.produto.description} - {self.fornecedor.name} ({self.codigo_no_fornecedor})'
