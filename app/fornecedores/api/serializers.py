from rest_framework import serializers

from ..models import Fornecedor


class FornecedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = ['id', 'name', 'phone', 'email', 'notes', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        # Tenant não está presente nesta classe, temos que setar o tenant pelo usuário da requisição e testar
        # a duplicidade.
        tenant = self.context['request'].user.tenant
        qs = Fornecedor.objects.filter(tenant=tenant, name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Já existe um fornecedor com este nome.')
        return value
