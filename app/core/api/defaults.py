from rest_framework import serializers


class TenantAtualDefault:
    """
    Default para HiddenField que preenche o tenant com o do usuário autenticado.
    Permite que o UniqueTogetherValidator enxergue o tenant sem que ele venha do body da requisição.
    """

    requires_context = True

    def __call__(self, serializer_field):
        tenant = serializer_field.context['request'].user.tenant
        if tenant is None:
            raise serializers.ValidationError('Tenant não identificado.')
        return tenant

    def __repr__(self):
        return f'{self.__class__.__name__}()'
