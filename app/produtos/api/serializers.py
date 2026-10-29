from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from core.api.defaults import TenantAtualDefault
from produtos.models import Produto, ProdutoFornecedor, UnidadeMedida


class UnidadeMedidaSerializer(serializers.ModelSerializer):
    # tenant nunca vem do body — é preenchido pelo usuário da requisição para os validators de unicidade
    tenant = serializers.HiddenField(default=TenantAtualDefault())

    class Meta:
        model = UnidadeMedida
        fields = ('id', 'tenant', 'name', 'abbreviation')
        validators = [
            UniqueTogetherValidator(
                queryset=UnidadeMedida.objects.all(),
                fields=['tenant', 'name'],
                message='Já existe uma unidade de medida com este nome.',
            ),
            UniqueTogetherValidator(
                queryset=UnidadeMedida.objects.all(),
                fields=['tenant', 'abbreviation'],
                message='Já existe uma unidade de medida com esta abreviação.',
            ),
        ]


class ProdutoFornecedorSerializer(serializers.ModelSerializer):
    fornecedor_name = serializers.CharField(source='fornecedor.name', read_only=True)

    class Meta:
        model = ProdutoFornecedor
        fields = ('id', 'fornecedor', 'fornecedor_name', 'codigo_no_fornecedor', 'fator_conversao', 'created_at')
        read_only_fields = ('id', 'created_at')
        validators = [
            UniqueTogetherValidator(
                queryset=ProdutoFornecedor.objects.all(),
                fields=['fornecedor', 'codigo_no_fornecedor'],
                message='Já existe outro produto com este código para este fornecedor.',
            ),
        ]

    def validate_fornecedor(self, value):
        request = self.context.get('request')
        if not request or not request.user.tenant:
            raise serializers.ValidationError('Tenant não identificado.')

        # mesma mensagem de "não existe" para não revelar fornecedores de outros tenants
        if value.tenant_id != request.user.tenant.id:
            raise serializers.ValidationError('Fornecedor não encontrado.')

        return value


class ProdutoSerializer(serializers.ModelSerializer):
    # tenant nunca vem do body — é preenchido pelo usuário da requisição para os validators de unicidade
    tenant = serializers.HiddenField(default=TenantAtualDefault())
    unidade_medida_name = serializers.CharField(source='unidade_medida.name', read_only=True)
    fornecedores = ProdutoFornecedorSerializer(source='produto_fornecedores', many=True, read_only=True)

    class Meta:
        model = Produto
        fields = (
            'id',
            'tenant',
            'code',
            'description',
            'fornecedores',
            'unidade_medida',
            'unidade_medida_name',
            'priority',
            'is_on_demand',
            'minimum_quantity',
            'current_quantity',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
        validators = [
            UniqueTogetherValidator(
                queryset=Produto.objects.all(),
                fields=['tenant', 'code'],
                message='Já existe um produto com este código.',
            ),
            UniqueTogetherValidator(
                queryset=Produto.objects.all(),
                fields=['tenant', 'description'],
                message='Já existe um produto com esta descrição.',
            ),
        ]
