from django.contrib import admin

from .models import Produto, ProdutoFornecedor, UnidadeMedida


@admin.register(UnidadeMedida)
class UnidadeMedidaAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'tenant', 'created_at')
    list_filter = ('tenant', 'created_at')
    search_fields = ('name', 'abbreviation')
    ordering = ('tenant', 'name')


class ProdutoFornecedorInline(admin.TabularInline):
    model = ProdutoFornecedor
    fields = ('fornecedor', 'codigo_no_fornecedor', 'fator_conversao', 'created_at')
    readonly_fields = ('created_at',)
    extra = 1


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('description', 'code', 'tenant', 'priority', 'is_active', 'created_at')
    list_filter = ('tenant', 'priority', 'is_active', 'is_on_demand', 'created_at')
    search_fields = ('description', 'code')
    readonly_fields = ('created_at', 'updated_at')
    inlines = (ProdutoFornecedorInline,)
    fieldsets = (
        ('Identificação', {'fields': ('tenant', 'code', 'description')}),
        (
            'Medidas e Quantidade',
            {'fields': ('unidade_medida', 'minimum_quantity', 'current_quantity', 'is_on_demand')},
        ),
        ('Prioridade e Status', {'fields': ('priority', 'is_active')}),
        ('Datas', {'fields': ('created_at', 'updated_at')}),
    )
    ordering = ('tenant', 'description')


@admin.register(ProdutoFornecedor)
class ProdutoFornecedorAdmin(admin.ModelAdmin):
    list_display = ('produto', 'fornecedor', 'codigo_no_fornecedor', 'fator_conversao', 'created_at')
    list_filter = ('fornecedor', 'created_at')
    search_fields = ('produto__description', 'fornecedor__name', 'codigo_no_fornecedor')
    readonly_fields = ('created_at',)
    ordering = ('produto', 'fornecedor')
