from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from core.api.defaults import TenantAtualDefault

from ..models import Fornecedor


class FornecedorSerializer(serializers.ModelSerializer):
    # tenant nunca vem do body — é preenchido pelo usuário da requisição para o validator de unicidade
    tenant = serializers.HiddenField(default=TenantAtualDefault())

    class Meta:
        model = Fornecedor
        fields = ['id', 'tenant', 'name', 'phone', 'email', 'notes', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
        validators = [
            UniqueTogetherValidator(
                queryset=Fornecedor.objects.all(),
                fields=['tenant', 'name'],
                message='Já existe um fornecedor com este nome.',
            ),
        ]
